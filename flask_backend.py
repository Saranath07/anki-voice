from flask import Flask, request, jsonify, send_file, render_template_string, url_for
from flask_cors import CORS
from datetime import datetime
import requests
import json
import ast
import re
import tempfile
import os
import threading
import speech_recognition as sr
import logging
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Serve static audio files
@app.route('/static/<filename>')
def serve_static_file(filename):
    """Serve static audio files"""
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_file(os.path.join(static_folder, filename))

# AnkiConnect endpoint
ANKI_CONNECT_URL = "http://localhost:8765"

# Helper functions from anki_streamlit.py
def load_api_key():
    """Load API key from key.txt file"""
    try:
        with open('key.txt', 'r') as f:
            content = f.read().strip()
            if content.startswith('API_KEY='):
                return content.split('=', 1)[1]
            return content
    except FileNotFoundError:
        logger.error("Error: key.txt file not found")
        return None

def load_prompt_template():
    """Load the prompt template from prompt_3.txt"""
    try:
        with open('prompt_3.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Error: prompt_3.txt file not found")
        return None

def load_reviewer_prompt_template():
    """Load the improved reviewer prompt template from improved_anki_reviewer_prompt.txt"""
    try:
        with open('improved_anki_reviewer_prompt.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Error: improved_anki_reviewer_prompt.txt file not found")
        return None

def send_chat_message(message, workspace_slug="anki", session_id="flashcard-generator"):
    """Send chat message to generate flashcards"""
    url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
    
    api_key = load_api_key()
    if not api_key:
        logger.error("Error: No API key found")
        return None
    
    payload = {
        "message": message,
        "mode": "chat",
        "sessionId": session_id
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"LLM API Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"LLM Request failed: {e}")
        return None

def parse_qa_response(response_text):
    """Parse the LLM response to extract list of dictionaries"""
    try:
        # Clean up the response text
        cleaned_response = response_text.strip()
        
        # Try to parse as JSON first
        try:
            qa_list = json.loads(cleaned_response)
            if isinstance(qa_list, list) and all(isinstance(item, dict) for item in qa_list):
                # Validate that each dict has Front and Back keys
                if all('Front' in item and 'Back' in item for item in qa_list):
                    return qa_list
        except json.JSONDecodeError:
            pass
        
        # Try to find a Python list in the response using regex with DOTALL flag
        list_pattern = r'\[.*?\]'
        matches = re.findall(list_pattern, cleaned_response, re.DOTALL)
        
        if matches:
            # Try to evaluate each match as a Python literal
            for match in matches:
                try:
                    # Try JSON parsing first
                    qa_list = json.loads(match)
                    if isinstance(qa_list, list) and all(isinstance(item, dict) for item in qa_list):
                        if all('Front' in item and 'Back' in item for item in qa_list):
                            return qa_list
                except json.JSONDecodeError:
                    try:
                        # Fallback to ast.literal_eval
                        qa_list = ast.literal_eval(match)
                        if isinstance(qa_list, list) and all(isinstance(item, dict) for item in qa_list):
                            if all('Front' in item and 'Back' in item for item in qa_list):
                                return qa_list
                    except (ValueError, SyntaxError):
                        continue
        
        # Try to parse the entire response with ast.literal_eval
        try:
            qa_list = ast.literal_eval(cleaned_response)
            if isinstance(qa_list, list) and all(isinstance(item, dict) for item in qa_list):
                if all('Front' in item and 'Back' in item for item in qa_list):
                    return qa_list
        except (ValueError, SyntaxError):
            pass
        
        # If all parsing methods fail, try to convert old Q/A format
        return convert_old_format_to_new(cleaned_response)
        
    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}")
        return None

def convert_old_format_to_new(response_text):
    """Convert old Q/A format to new list format"""
    try:
        lines = response_text.strip().split('\n')
        qa_pairs = []
        current_q = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q: '):
                current_q = line[3:]  # Remove 'Q: '
            elif line.startswith('A: ') and current_q:
                current_a = line[3:]  # Remove 'A: '
                qa_pairs.append({"Front": current_q, "Back": current_a})
                current_q = None
        
        if qa_pairs:
            return qa_pairs
        else:
            logger.error("Failed to parse LLM response into valid QA pairs")
            return None
            
    except Exception as e:
        logger.error(f"Error converting old format: {e}")
        return None

# LLM-based question enhancement for TTS
def enhance_question_for_tts(question):
    """Use LLM to enhance question with natural speech elements for TTS."""
    prompt = f"""
Add ONLY natural speech elements to make this question sound human when spoken. DO NOT change the question content or reveal any answers.

STRICT RULES:
- Add ONLY 1-2 natural speech elements: "uhh", "hmm", "well", "so", "now"
- Convert math symbols/formulas to spoken words (e.g., "x²" → "x squared")
- NEVER change the actual question content
- NEVER add answers or hints
- NEVER make it longer than the original
- Keep the exact same meaning

Question: {question}

Enhanced for speech (keep question identical, just add natural speech):"""
    
    try:
        response = send_chat_message(prompt, workspace_slug="anki", session_id="question-enhancer")
        if response and response.get('textResponse'):
            enhanced_text = response['textResponse'].strip()
            # Basic validation: ensure it's not empty and not excessively long
            if enhanced_text and len(enhanced_text) < (len(question) * 3 + 50): # Heuristic
                logger.info(f"Successfully enhanced question for TTS: {enhanced_text}")
                return enhanced_text
        logger.warning(f"Question enhancement for TTS failed or produced invalid output for: {question}. Using original.")
        return question  # Fallback to original if enhancement fails
    except Exception as e:
        logger.error(f"Question enhancement for TTS error: {e}")
        return question

# AnkiConnect functions
def invoke(action, params=None):
    """General invoke wrapper for AnkiConnect"""
    payload = {"action": action, "version": 6}
    if params:
        payload["params"] = params
    
    try:
        res = requests.post(ANKI_CONNECT_URL, json=payload).json()
        if res.get("error"):
            logger.error(f"AnkiConnect Error ({action}): {res['error']}")
            return None
        return res.get("result")
    except Exception as e:
        logger.error(f"AnkiConnect request failed: {e}")
        return None

def get_deck_stats(deck_names):
    """Get deck statistics"""
    return invoke("getDeckStats", {"decks": deck_names}) or {}

def find_cards(query):
    """Find cards with query"""
    return invoke("findCards", {"query": query}) or []

def get_cards_info(card_ids):
    """Get card information"""
    return invoke("cardsInfo", {"cards": card_ids}) or []

# TTS and ASR Functions
def text_to_speech_file(text, note_id=None):
    """Convert text to speech using external TTS API and return audio file path"""
    try:
        # Create static folder if it doesn't exist
        static_folder = os.path.join(os.getcwd(), 'static')
        if not os.path.exists(static_folder):
            os.makedirs(static_folder)
        
        # Determine file path - use note_id if provided, otherwise create temp file
        if note_id:
            file_path = os.path.join(static_folder, f"{note_id}.wav")
        else:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            file_path = temp_file.name
            temp_file.close()
        
        # Prepare payload for the TTS API
        payload = {
            "input": text,
            "model": "orpheus",
            "voice": "tara",
            "response_format": "wav",
            "speed": 1
        }
        
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
          # Make request to TTS API
        try:
            response = requests.post(
                'http://localhost:5005/v1/audio/speech',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                # Save the audio content to the file
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                # Check if file was created and has content
                if os.path.exists(file_path) and os.path.getsize(file_path) > 44:  # WAV header is ~44 bytes
                    logger.info(f"Successfully generated TTS audio for text: {text[:50]}...")
                    return file_path
                else:
                    logger.warning("TTS API returned empty or invalid audio file")
                    return create_simple_audio_response(text, file_path)
            else:
                logger.error(f"TTS API Error: HTTP {response.status_code} - {response.text}")
                return create_simple_audio_response(text, file_path)
                
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to TTS service at http://localhost:5005")
            return create_simple_audio_response(text, file_path)
        except requests.exceptions.Timeout:
            logger.error("TTS API request timed out")
            return create_simple_audio_response(text, file_path)
        except Exception as api_error:
            logger.error(f"TTS API request failed: {api_error}")
            return create_simple_audio_response(text, file_path)
            
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        return create_simple_audio_response(text if 'text' in locals() else "Error", None)

def create_simple_audio_response(text, file_path=None):
    """Create a simple audio file as fallback"""
    try:
        if not file_path:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            file_path = temp_file.name
            temp_file.close()
        
        # Create a minimal WAV file with silence (for testing purposes)
        # This is a basic WAV header + some silence
        wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        silence_data = b'\x00' * 8000  # 1 second of silence at 8kHz
        
        with open(file_path, 'wb') as f:
            f.write(wav_header + silence_data)
        
        logger.info(f"Created fallback audio file for text: {text[:50]}...")
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to create fallback audio: {e}")
        return None

def speech_to_text_from_file(audio_file_path):
    """Convert speech file to text using external ASR API"""
    try:
        # Send audio to external ASR API
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            response = requests.post('http://localhost:5000/transcribe', files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                return result.get('transcript')
            else:
                logger.error(f"ASR API Error: {result.get('message', 'Unknown error')}")
                return None
        else:
            logger.error(f"ASR API Error: HTTP {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to ASR service at http://localhost:5000")
        return None
    except Exception as e:
        logger.error(f"ASR Error: {e}")
        return None

# API Endpoints

@app.route('/api/generate_flashcards_with_llm', methods=['POST'])
def generate_flashcards_with_llm():
    """Generate flashcards using LLM for the given statement"""
    try:
        data = request.get_json()
        if not data or 'statement' not in data:
            return jsonify({'error': 'Statement is required'}), 400
        
        statement = data['statement']
        
        prompt_template = load_prompt_template()
        if not prompt_template:
            return jsonify({'error': 'Prompt template not found'}), 500
        
        # Replace <INPUT_TEXT> with the actual statement
        prompt = prompt_template.replace('<INPUT_TEXT>', statement)
        
        response = send_chat_message(prompt)
        
        if response and 'textResponse' in response:
            qa_pairs = parse_qa_response(response['textResponse'])
            if qa_pairs:
                return jsonify({
                    'success': True,
                    'flashcards': qa_pairs,
                    'count': len(qa_pairs)
                })
            else:
                return jsonify({'error': 'Failed to parse LLM response'}), 500
        else:
            return jsonify({'error': 'Failed to generate flashcards with LLM'}), 500
            
    except Exception as e:
        logger.error(f"Error in generate_flashcards_with_llm: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluate_answer_with_llm', methods=['POST'])
def evaluate_answer_with_llm():
    """Use LLM to evaluate user's answer and suggest rating"""
    try:
        data = request.get_json()
        required_fields = ['question', 'correct_answer', 'user_answer']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing one or more required fields: {required_fields}"}), 400
        
        question = data['question']
        correct_answer = data['correct_answer']
        user_answer = data['user_answer']
        
        prompt_template = load_reviewer_prompt_template()
        if not prompt_template:
            logger.error("Reviewer prompt template (improved_anki_reviewer_prompt.txt) not found. Using fallback prompt.")
            # Fallback prompt (similar to anki_streamlit.py)
            prompt = f"""
You are a very emotional, human-like tutor who gets genuinely excited when students do well and disappointed when they struggle. Evaluate the student's answer and respond with authentic human emotions.

RATING SCALE:
1 = Again (completely wrong) - Be disappointed but encouraging
2 = Hard (partially correct) - Show mild concern but be supportive
3 = Good (mostly correct) - Be pleased and encouraging
4 = Easy (perfect answer) - Be EXTREMELY happy and excited!

EMOTIONAL RESPONSE GUIDELINES:
- For rating 1: Express disappointment but be encouraging. Use phrases like "Oh no...", "Hmm, that's not quite right", "Don't worry, let's try again"
- For rating 2: Show mild concern. Use "Uhh...", "Well...", "You're getting there but..."
- For rating 3: Be pleased! Use "Good job!", "Nice work!", "You got it mostly right!"
- For rating 4: Be EXTREMELY excited! Use "Excellent!", "Perfect!", "Amazing!", "You nailed it!", add excitement sounds like "Wow!"

Add natural speech elements like:
- "uhh...", "hmm...", "well...", "oh!", "wow!"
- "<laugh>", "<excited>", "<sigh>", "<pleased>"
- Emotional reactions that match the performance

IMPORTANT RULES:
- Minor grammar, spelling, or word form errors should NOT lower the rating below 3
- Focus on MEANING and KEY CONTENT, not perfect grammar
- If the main idea is correct, rate 3 or 4
- Only rate 1 or 2 if the answer is actually wrong or missing important information
- Do not look for grammatical perfection, just the core understanding is enough for rating 4.

Question: {question}
Correct Answer: {correct_answer}
Student's Answer: {user_answer}

Respond with:
Rating: [1-4]
Reason: [Your very human, emotional evaluation with natural speech elements]
"""
        else:
            prompt = prompt_template.format(
                question=question,
                correct_answer=correct_answer,
                user_answer=user_answer
            )
        
        response = send_chat_message(prompt, workspace_slug="anki", session_id="anki-reviewer")
        
        if response and response.get('textResponse'):
            response_text = response['textResponse']
            rating = None
            reason = "Could not parse LLM evaluation. Raw response: " + response_text

            # Improved parsing for "Rating: X" and "Reason: Y"
            rating_match = re.search(r"Rating:\s*([1-4])", response_text, re.IGNORECASE)
            # Reason can be multi-line and might be the rest of the text after Rating.
            # Look for "Reason:" then capture everything after it.
            # If "Reason:" is not found, but rating is, take the whole text as reason.
            reason_search_match = re.search(r"Reason:\s*(.+)", response_text, re.IGNORECASE | re.DOTALL)

            if rating_match:
                rating = int(rating_match.group(1))
                if reason_search_match:
                    reason = reason_search_match.group(1).strip()
                else:
                    # If "Reason:" marker is not found, but we have a rating,
                    # try to extract a plausible reason from the text,
                    # or use a generic message.
                    # For now, let's take the whole response if "Reason:" is missing.
                    # This might need further refinement based on LLM's typical output.
                    reason = response_text # Or a more sophisticated extraction
                    logger.warning("LLM evaluation response parsed for rating, but 'Reason:' marker not found. Using full response as reason.")
            
            if rating is not None:
                return jsonify({"rating": rating, "reason": reason})
            else:
                logger.error(f"LLM response received but failed to parse rating: {response_text}")
                return jsonify({"rating": None, "reason": response_text, "message": "LLM response received but rating parsing failed."})
        else:
            return jsonify({"error": "Failed to get LLM evaluation"}), 500
            
    except Exception as e:
        logger.error(f"Error in evaluate_answer_with_llm: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/read_question', methods=['POST'])
def read_question():
    """Convert question text to speech and return audio file"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400
        
        question_text = data['question']
        note_id = data.get('note_id') # Optional for filename uniqueness

        enhanced_question = enhance_question_for_tts(question_text)
        
        audio_file_path = text_to_speech_file(enhanced_question, note_id=note_id)
        
        if audio_file_path:
            filename = os.path.basename(audio_file_path)
            # Ensure the static folder is correctly referenced if it's not at the root
            # For url_for, 'static' is the default endpoint for the static folder.
            audio_url = url_for('serve_static_file', filename=filename, _external=True)
            logger.info(f"Generated TTS audio URL: {audio_url}")
            return jsonify({"audio_url": audio_url, "message": "TTS successful"})
        else:
            logger.error(f"Failed to generate TTS audio for question: {question_text}")
            return jsonify({"error": "Failed to generate TTS audio"}), 500
            
    except Exception as e:
        logger.error(f"Error in read_question: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/record_answer', methods=['POST'])
def record_answer():
    """Convert uploaded audio file to text"""
    try:
        if 'audio_file' not in request.files:
            return jsonify({"error": "No audio file part"}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file:
            # Save to a temporary file to pass to speech_to_text_from_file
            # Ensure the suffix is correct if the ASR service is picky.
            temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav") # Assuming WAV
            file.save(temp_audio_file.name)
            temp_audio_file.name_to_delete = temp_audio_file.name # Store name for deletion
            temp_audio_file.close() # Close the file before passing its name
            
            transcribed_text = None
            try:
                transcribed_text = speech_to_text_from_file(temp_audio_file.name_to_delete)
            finally:
                if os.path.exists(temp_audio_file.name_to_delete):
                    os.remove(temp_audio_file.name_to_delete) # Clean up temp file
            
            if transcribed_text is not None:
                logger.info(f"ASR successful: {transcribed_text}")
                return jsonify({"transcribed_text": transcribed_text, "message": "ASR successful"})
            else:
                logger.error("Failed to transcribe audio via ASR.")
                return jsonify({"error": "Failed to transcribe audio"}), 500
        
    except Exception as e:
        logger.error(f"Error in record_answer: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/change_of_modes', methods=['POST'])
def change_of_modes():
    """Handle mode changes for the application"""
    try:
        data = request.get_json()
        if not data or 'mode' not in data:
            return jsonify({'error': 'Mode is required'}), 400
        
        mode = data['mode']
        valid_modes = ['add_cards', 'review_cards', 'deck_stats', 'tts_only', 'asr_llm', 'enhanced_tts_asr_llm']
        
        if mode not in valid_modes:
            return jsonify({'error': f'Invalid mode. Valid modes: {valid_modes}'}), 400
        
        # You can add mode-specific logic here
        mode_descriptions = {
            'add_cards': 'Add new flashcards to deck',
            'review_cards': 'Review existing flashcards',
            'deck_stats': 'View deck statistics',
            'tts_only': 'Text-to-speech only mode',
            'asr_llm': 'Speech recognition with LLM evaluation',
            'enhanced_tts_asr_llm': 'Enhanced mode with TTS, ASR, and LLM'
        }
        
        return jsonify({
            'success': True,
            'mode': mode,
            'description': mode_descriptions.get(mode, 'Unknown mode')
        })
        
    except Exception as e:
        logger.error(f"Error in change_of_modes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/deck_stats', methods=['GET'])
def deck_stats():
    """Get statistics for specified deck(s)"""
    try:
        deck_name = request.args.get('deck_name')
        if not deck_name:
            return jsonify({'error': 'deck_name parameter is required'}), 400
        
        deck_names = [deck_name]
        stats = get_deck_stats(deck_names)
        
        if stats:
            deck_stat = stats.get(deck_name, {})
            
            # Get additional card counts
            due_cards = find_cards(f'deck:"{deck_name}" is:due')
            new_cards = find_cards(f'deck:"{deck_name}" is:new')
            all_cards = find_cards(f'deck:"{deck_name}"')
            
            return jsonify({
                'success': True,
                'deck_name': deck_name,
                'stats': {
                    'total_in_deck': deck_stat.get('total_in_deck', 0),
                    'new_count': deck_stat.get('new_count', 0),
                    'learn_count': deck_stat.get('learn_count', 0),
                    'review_count': deck_stat.get('review_count', 0),
                    'due_cards': len(due_cards),
                    'new_cards': len(new_cards),
                    'total_cards': len(all_cards)
                }
            })
        else:
            return jsonify({'error': 'Failed to get deck statistics'}), 500
            
    except Exception as e:
        logger.error(f"Error in deck_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_question_answer', methods=['POST'])
def send_question_answer():
    """Send question and answer data (for logging or processing)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        # Extract relevant fields
        question = data.get('question', '')
        answer = data.get('answer', '')
        user_answer = data.get('user_answer', '')
        rating = data.get('rating', 0)
        timestamp = data.get('timestamp', datetime.now().isoformat())
        deck_name = data.get('deck_name', '')
        card_id = data.get('card_id', '')
        
        # Log the data (you can modify this to save to database, file, etc.)
        log_entry = {
            'timestamp': timestamp,
            'deck_name': deck_name,
            'card_id': card_id,
            'question': question,
            'correct_answer': answer,
            'user_answer': user_answer,
            'rating': rating
        }
        
        logger.info(f"Question-Answer log: {json.dumps(log_entry)}")
        
        # You can add additional processing here:
        # - Save to database
        # - Send to analytics service
        # - Update user progress tracking
        # - etc.
        
        return jsonify({
            'success': True,
            'message': 'Question-answer data received and logged',
            'logged_data': log_entry
        })
        
    except Exception as e:
        logger.error(f"Error in send_question_answer: {e}")
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'anki_connect_available': invoke("version") is not None
    })

# Get available decks
@app.route('/api/decks', methods=['GET'])
def get_decks():
    """Get list of available Anki decks"""
    try:
        deck_names = invoke("deckNames") or []
        return jsonify({
            'success': True,
            'decks': deck_names
        })
    except Exception as e:
        logger.error(f"Error getting decks: {e}")
        return jsonify({'error': str(e)}), 500

# Add notes to Anki
@app.route('/api/add_notes', methods=['POST'])
def add_notes_to_anki():
    """Add notes to Anki through AnkiConnect"""
    try:
        data = request.get_json()
        notes = data.get('notes', [])
        
        if not notes:
            return jsonify({'error': 'No notes provided'}), 400
        
        # Use AnkiConnect to add notes
        result = invoke("addNotes", {"notes": notes})
        
        if result is None:
            return jsonify({'error': 'Failed to add notes to Anki'}), 500
        
        # Count successful additions (non-null IDs)
        success_count = len([note_id for note_id in result if note_id is not None])
        
        return jsonify({
            'success': True,
            'note_ids': result,
            'success_count': success_count,
            'total_count': len(notes)
        })
        
    except Exception as e:
        logger.error(f"Error adding notes to Anki: {e}")
        return jsonify({'error': str(e)}), 500

# Get available note models
@app.route('/api/note_models', methods=['GET'])
def get_note_models():
    """Get list of available Anki note models"""
    try:
        model_names = invoke("modelNames") or []
        return jsonify({
            'success': True,
            'models': model_names
        })
    except Exception as e:
        logger.error(f"Error getting note models: {e}")
        return jsonify({'error': str(e)}), 500

# Create new deck
@app.route('/api/create_deck', methods=['POST'])
def create_deck():
    """Create a new Anki deck"""
    try:
        data = request.get_json()
        deck_name = data.get('deck_name', '').strip()
        
        if not deck_name:
            return jsonify({'error': 'Deck name is required'}), 400
        
        # Use AnkiConnect to create deck
        result = invoke("createDeck", {"deck": deck_name})
        
        if result is None:
            return jsonify({'error': 'Failed to create deck'}), 500
        
        return jsonify({
            'success': True,
            'deck_name': deck_name,
            'message': f'Deck "{deck_name}" created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating deck: {e}")
        return jsonify({'error': str(e)}), 500

# Start GUI deck review
@app.route('/api/gui_deck_review', methods=['POST'])
def gui_deck_review():
    """Start native review in Anki GUI"""
    try:
        data = request.get_json()
        deck_name = data.get('deck_name', '').strip()
        
        if not deck_name:
            return jsonify({'error': 'Deck name is required'}), 400
        
        # Use AnkiConnect to start GUI review
        result = invoke("guiDeckReview", {"name": deck_name})
        
        if result is None:
            return jsonify({'error': 'Failed to start native review'}), 500
        
        return jsonify({
            'success': True,
            'deck_name': deck_name,
            'message': f'Started native review for deck "{deck_name}"'
        })
        
    except Exception as e:
        logger.error(f"Error starting GUI deck review: {e}")
        return jsonify({'error': str(e)}), 500

# Answer cards
@app.route('/api/answer_cards', methods=['POST'])
def answer_cards():
    """Answer cards with ratings"""
    try:
        data = request.get_json()
        answers = data.get('answers', [])
        
        if not answers:
            return jsonify({'error': 'No answers provided'}), 400
        
        # Use AnkiConnect to answer cards
        result = invoke("answerCards", {"answers": answers})
        
        if result is None:
            return jsonify({'error': 'Failed to answer cards'}), 500
        
        return jsonify({
            'success': True,
            'result': result,
            'message': f'Answered {len(answers)} card(s)'
        })
        
    except Exception as e:
        logger.error(f"Error answering cards: {e}")
        return jsonify({'error': str(e)}), 500

# Get Cards of a Deck
@app.route('/api/get_cards_of_deck', methods=['GET'])
def get_cards_of_deck():
    """Get cards of a specific deck"""
    try:
        deck_name = request.args.get('deck_name')
        if not deck_name:
            return jsonify({'error': 'deck_name parameter is required'}), 400
        
        # Find cards in the specified deck
        card_ids = find_cards(f'deck:"{deck_name}"')
        
        if not card_ids:
            return jsonify({'error': f'No cards found in deck "{deck_name}"'}), 404
        
        # Get detailed info for each card
        cards_info = get_cards_info(card_ids)
        
        return jsonify({
            'success': True,
            'deck_name': deck_name,
            'cards': cards_info
        })
        
    except Exception as e:
        logger.error(f"Error getting cards of deck: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_review_cards', methods=['GET'])
def get_review_cards():
    """Get cards that are due for review and new cards for a specific deck"""
    try:
        deck_name = request.args.get('deck')
        if not deck_name:
            return jsonify({"error": "Missing 'deck' query parameter"}), 400

        logger.info(f"Fetching review cards for deck: {deck_name}")

        due_card_ids = find_cards(f'deck:"{deck_name}" is:due') or []
        new_card_ids = find_cards(f'deck:"{deck_name}" is:new') or []
        
        # Combine and remove duplicates, though is:due and is:new should be distinct
        card_ids_to_fetch = list(set(due_card_ids + new_card_ids))

        if not card_ids_to_fetch:
            logger.info(f"No review cards (due or new) found for deck: {deck_name}")
            return jsonify([]) # Return empty list if no cards

        raw_cards_info = get_cards_info(card_ids_to_fetch)
        
        if raw_cards_info is None: # get_cards_info might return None on AnkiConnect error
            logger.error(f"Failed to get card info from AnkiConnect for deck: {deck_name}")
            return jsonify({"error": "Failed to retrieve card details from AnkiConnect"}), 500

        # Process cards_info to a more usable format if needed
        # The default 'question' and 'answer' fields from cardsInfo are usually the front and back.
        # We also want to include noteId for TTS caching.
        processed_cards = []
        for card_info in raw_cards_info:
            processed_cards.append({
                "cardId": card_info.get("cardId"),
                "question": card_info.get("question"), # Typically the 'Front' field content
                "answer": card_info.get("answer"),   # Typically the 'Back' field content
                "noteId": card_info.get("note"),     # Note ID for potential TTS caching key
                "deckName": card_info.get("deckName"),
                "modelName": card_info.get("modelName"),
                "fields": card_info.get("fields")    # Full fields for more complex frontends
            })
        
        logger.info(f"Found {len(processed_cards)} cards for review in deck: {deck_name}")
        return jsonify(processed_cards)

    except Exception as e:
        logger.error(f"Error getting review cards: {e}")
        return jsonify({'error': str(e)}), 500

# Swagger UI endpoints
@app.route('/docs')
def swagger_ui():
    """Serve Swagger UI documentation"""
    swagger_ui_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Anki Voice API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
        <style>
            html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
            *, *:before, *:after { box-sizing: inherit; }
            body { margin:0; background: #fafafa; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
        <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: '/swagger.yaml',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout"
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(swagger_ui_html)

@app.route('/swagger.yaml')
def swagger_spec():
    """Serve the OpenAPI specification"""
    try:
        with open('swagger.yaml', 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/yaml'}
    except FileNotFoundError:
        return jsonify({'error': 'Swagger specification not found'}), 404

if __name__ == '__main__':
    # Check if required files exist
    required_files = ['key.txt', 'prompt_3.txt']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        logger.warning(f"Missing files: {missing_files}. Some functionality may not work.")
    
    # Check AnkiConnect connection
    if invoke("version"):
        logger.info("AnkiConnect connection successful")
    else:
        logger.warning("AnkiConnect not available. Make sure Anki is running with AnkiConnect addon.")
    
    app.run(debug=True, host='0.0.0.0', port=5001)