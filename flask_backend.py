from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import requests
import json
import ast
import re
import tempfile
import os
import threading
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import logging
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

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
def text_to_speech_file(text):
    """Convert text to speech and return audio file path"""
    try:
        # Create a temporary file for the audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Set properties with error handling
        try:
            voices = engine.getProperty('voices')
            if voices and len(voices) > 0:
                engine.setProperty('voice', voices[0].id)
        except Exception as voice_error:
            logger.warning(f"Could not set voice: {voice_error}")
        
        try:
            engine.setProperty('rate', 200)
            engine.setProperty('volume', 0.9)
        except Exception as prop_error:
            logger.warning(f"Could not set TTS properties: {prop_error}")
        
        # Save to file with better error handling
        try:
            engine.save_to_file(text, temp_file_path)
            engine.runAndWait()
            
            # Give it a moment to complete
            import time
            time.sleep(0.5)
            
        except Exception as save_error:
            logger.error(f"Error saving TTS file: {save_error}")
            # Try alternative approach - create a simple audio response
            return create_simple_audio_response(text, temp_file_path)
        
        # Check if file was created and has content
        if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 44:  # WAV header is ~44 bytes
            return temp_file_path
        else:
            logger.warning("TTS file was not created properly, trying alternative")
            return create_simple_audio_response(text, temp_file_path)
            
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
    """Convert speech file to text using speech_recognition"""
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio = r.record(source)
        
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        logger.error("Could not understand the audio")
        return None
    except sr.RequestError as e:
        logger.error(f"Speech recognition error: {e}")
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
        if not data or not all(key in data for key in ['question', 'correct_answer', 'user_answer']):
            return jsonify({'error': 'Question, correct_answer, and user_answer are required'}), 400
        
        question = data['question']
        correct_answer = data['correct_answer']
        user_answer = data['user_answer']
        
        prompt_template = load_reviewer_prompt_template()
        if not prompt_template:
            # Fallback to human-like emotional prompt
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
User's Answer: {user_answer}

Respond with:
Rating: [1-4]
Reason: [Your very human, emotional evaluation with natural speech elements]
"""
        else:
            # Use the improved prompt template
            prompt = prompt_template.format(
                question=question,
                correct_answer=correct_answer,
                user_answer=user_answer
            )
        
        response = send_chat_message(prompt, workspace_slug="anki", session_id="anki-reviewer")
        if response and response.get('textResponse'):
            response_text = response['textResponse'].strip()
            
            # Extract rating from response
            rating_match = re.search(r'Rating:\s*(\d)', response_text)
            if rating_match:
                rating = int(rating_match.group(1))
                if 1 <= rating <= 4:
                    return jsonify({
                        'success': True,
                        'rating': rating,
                        'explanation': response_text
                    })
            
            # Fallback: look for just a number
            number_match = re.search(r'\b([1-4])\b', response_text)
            if number_match:
                rating = int(number_match.group(1))
                return jsonify({
                    'success': True,
                    'rating': rating,
                    'explanation': response_text
                })
                
        return jsonify({
            'success': True,
            'rating': 3,
            'explanation': "Could not determine rating, defaulting to Good (3)"
        })
        
    except Exception as e:
        logger.error(f"Error in evaluate_answer_with_llm: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/read_question', methods=['POST'])
def read_question():
    """Convert question text to speech and return audio file"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question text is required'}), 400
        
        question = data['question']
        enhance = data.get('enhance', False)  # Whether to enhance with LLM
        
        text_to_speak = question
        
        if enhance:
            # Enhance question for TTS using LLM
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
            
            response = send_chat_message(prompt, workspace_slug="anki", session_id="question-enhancer")
            if response and response.get('textResponse'):
                enhanced_text = response['textResponse'].strip()
                # Remove any quotes or extra formatting
                enhanced_text = enhanced_text.strip('"\'')
                text_to_speak = enhanced_text
        
        # Generate audio file
        audio_file_path = text_to_speech_file(text_to_speak)
        
        if audio_file_path:
            return send_file(audio_file_path, as_attachment=True, download_name='question.wav')
        else:
            return jsonify({'error': 'Failed to generate audio'}), 500
            
    except Exception as e:
        logger.error(f"Error in read_question: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/record_answer', methods=['POST'])
def record_answer():
    """Convert uploaded audio file to text"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file is required'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio_file.save(temp_file.name)
        temp_file.close()
        
        # Convert speech to text
        text = speech_to_text_from_file(temp_file.name)
        
        # Clean up temporary file
        os.unlink(temp_file.name)
        
        if text:
            return jsonify({
                'success': True,
                'text': text
            })
        else:
            return jsonify({'error': 'Could not understand the audio'}), 400
            
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