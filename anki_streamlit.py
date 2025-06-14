import streamlit as st
import requests
import json
import time
import ast
import re
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import tempfile
import os
import threading

# AnkiConnect endpoint
ANKI_CONNECT_URL = "http://localhost:8765"

# LLM integration functions
def load_api_key():
    """Load API key from key.txt file"""
    try:
        with open('key.txt', 'r') as f:
            content = f.read().strip()
            if content.startswith('API_KEY='):
                return content.split('=', 1)[1]
            return content
    except FileNotFoundError:
        st.error("Error: key.txt file not found")
        return None

def load_prompt_template():
    """Load the prompt template from prompt_3.txt"""
    try:
        with open('prompt_3.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        st.error("Error: prompt_3.txt file not found")
        return None

def load_reviewer_prompt_template():
    """Load the improved reviewer prompt template from improved_anki_reviewer_prompt.txt"""
    try:
        with open('improved_anki_reviewer_prompt.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        st.error("Error: improved_anki_reviewer_prompt.txt file not found")
        return None

def enhance_question_for_tts(question):
    """Use LLM to enhance question with emotional elements and convert MathJax to readable text"""
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
            # Remove any quotes or extra formatting
            enhanced_text = enhanced_text.strip('"\'')
            return enhanced_text
        return question  # Fallback to original if enhancement fails
    except Exception as e:
        st.error(f"Question enhancement error: {e}")
        return question

def evaluate_answer_with_human_llm(question, correct_answer, user_answer):
    """Use LLM to evaluate user's answer with very human-like emotional responses"""
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

Question: {question}
Correct Answer: {correct_answer}
Student's Answer: {user_answer}

Respond with:
Rating: [1-4]
Emotional Response: [Your very human, emotional evaluation with natural speech elements]
"""
    
    try:
        response = send_chat_message(prompt, workspace_slug="anki", session_id="human-evaluator")
        if response and response.get('textResponse'):
            response_text = response['textResponse'].strip()
            
            # Extract rating from response
            rating_match = re.search(r'Rating:\s*(\d)', response_text)
            if rating_match:
                rating = int(rating_match.group(1))
                if 1 <= rating <= 4:
                    return rating, response_text
            
            # Fallback: look for just a number
            number_match = re.search(r'\b([1-4])\b', response_text)
            if number_match:
                rating = int(number_match.group(1))
                return rating, response_text
                
        return 3, "Good job! <pleased> You're doing well, keep it up!"
    except Exception as e:
        st.error(f"Human LLM evaluation error: {e}")
        return 3, f"Hmm... <confused> There was an issue, but you're doing fine! {e}"

def send_chat_message(message, workspace_slug="anki", session_id="flashcard-generator"):
    """Send chat message to generate flashcards"""
    url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
    
    api_key = load_api_key()
    if not api_key:
        st.error("Error: No API key found")
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
            st.error(f"LLM API Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"LLM Request failed: {e}")
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
        st.error(f"Error parsing LLM response: {e}")
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
            st.error("Failed to parse LLM response into valid QA pairs")
            return None
            
    except Exception as e:
        st.error(f"Error converting old format: {e}")
        return None

def generate_flashcards_with_llm(statement):
    """Generate flashcards using LLM for the given statement"""
    prompt_template = load_prompt_template()
    if not prompt_template:
        return None
    
    # Replace <INPUT_TEXT> with the actual statement
    prompt = prompt_template.replace('<INPUT_TEXT>', statement)
    
    with st.spinner("Generating flashcards with LLM..."):
        response = send_chat_message(prompt)
    
    if response and 'textResponse' in response:
        qa_pairs = parse_qa_response(response['textResponse'])
        return qa_pairs
    else:
        st.error("Failed to generate flashcards with LLM")
        return None

# General invoke wrapper for AnkiConnect
def invoke(action, params=None):
    payload = {"action": action, "version": 6}
    if params:
        payload["params"] = params
    res = requests.post(ANKI_CONNECT_URL, json=payload).json()
    if res.get("error"):
        st.error(f"AnkiConnect Error ({action}): {res['error']}")
    return res.get("result")

# Ensure permission granted
permission = invoke("requestPermission")
if permission and permission.get("permission") != "granted":
    st.error("Please grant permission in Anki to allow AnkiConnect API calls.")

# Core API methods using AnkiConnect documented actions
def get_deck_names():
    return invoke("deckNames") or []

def create_deck(deck_name):
    return invoke("createDeck", {"deck": deck_name})

def get_model_names():
    return invoke("modelNames") or []

def find_cards(query):
    return invoke("findCards", {"query": query}) or []

def get_cards_info(card_ids):
    return invoke("cardsInfo", {"cards": card_ids}) or []

def add_notes(notes):
    return invoke("addNotes", {"notes": notes})

def answer_cards(answers):
    # answers: list of {cardId, ease}
    return invoke("answerCards", {"answers": answers})

def get_deck_stats(deck_names):
    return invoke("getDeckStats", {"decks": deck_names}) or {}

def get_num_reviewed_today():
    return invoke("getNumCardsReviewedToday") or 0

# TTS and ASR Functions
def text_to_speech(text):
    """Convert text to speech using pyttsx3"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 200)
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return False

def speech_to_text():
    """Convert speech to text using speech_recognition"""
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now!")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            
        st.info("🔄 Processing speech...")
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("❌ Could not understand the audio")
        return None
    except sr.RequestException as e:
        st.error(f"❌ Speech recognition error: {e}")
        return None
    except sr.WaitTimeoutError:
        st.error("❌ No speech detected within timeout")
        return None
    except Exception as e:
        st.error(f"❌ ASR Error: {e}")
        return None

def evaluate_answer_with_llm(question, correct_answer, user_answer):
    """Use LLM to evaluate user's answer and suggest rating"""
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
    
    try:
        response = send_chat_message(prompt, workspace_slug="anki", session_id="anki-reviewer")
        if response and response.get('textResponse'):
            response_text = response['textResponse'].strip()
            
            # Extract rating from response
            rating_match = re.search(r'Rating:\s*(\d)', response_text)
            if rating_match:
                rating = int(rating_match.group(1))
                if 1 <= rating <= 4:
                    return rating, response_text
            
            # Fallback: look for just a number
            number_match = re.search(r'\b([1-4])\b', response_text)
            if number_match:
                rating = int(number_match.group(1))
                return rating, response_text
                
        return 3, "Could not determine rating, defaulting to Good (3)"
    except Exception as e:
        st.error(f"LLM evaluation error: {e}")
        return 3, f"Error in evaluation: {e}"

 # Streamlit UI
st.set_page_config(page_title="Anki LLM Companion", layout="wide")
st.title("📚 Anki LLM Companion")

 # Sidebar: Deck & Mode
decks = get_deck_names()
if not decks:
    st.sidebar.error("No decks found. Open Anki and ensure AnkiConnect is running.")
    st.stop()
deck = st.sidebar.selectbox("Select Deck", decks)
mode = st.sidebar.radio("Mode", ["Add Cards", "Review Cards", "Deck Stats"])

if mode == "Add Cards":
    st.header("➕ Add QA Cards")
    # Allow creating new deck
    new_deck = st.text_input("Or create new deck:")
    if new_deck:
        if st.button("Create Deck"):
            create_deck(new_deck)
            st.success(f"Created deck: {new_deck}")
    statement = st.text_area("Enter statement/theorem/fact:")
    model_names = get_model_names()
    model = st.selectbox("Note Model", model_names)
    if st.button("Generate QA Pairs with LLM"):
        if statement.strip():
            qa_pairs = generate_flashcards_with_llm(statement)
            if qa_pairs:
                st.session_state.qa = qa_pairs
                st.success(f"Generated {len(qa_pairs)} QA pairs!")
            else:
                st.error("Failed to generate QA pairs. Please check your LLM service and try again.")
        else:
            st.warning("Please enter a statement/theorem/fact first.")
    if st.session_state.get("qa"):
        st.subheader("Generated QA Pairs")
        
        # Add clear button at the top
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Generated {len(st.session_state.qa)} flashcards. Review and select which ones to add:")
        with col2:
            if st.button("Clear All", type="secondary"):
                st.session_state.qa = []
                st.rerun()
        
        notes = []
        for i, qa in enumerate(st.session_state.qa):
            with st.expander(f"Card {i+1}: {qa['Front'][:50]}..."):
                st.write(f"**Question:** {qa['Front']}")
                st.write(f"**Answer:** {qa['Back']}")
                approved = st.checkbox(f"Add this card to Anki", key=f"card_{i}")
                if approved:
                    note = {
                        "deckName": deck,
                        "modelName": model,
                        "fields": qa,
                        "options": {"allowDuplicate": False},
                        "tags": ["llm-generated"]
                    }
                    notes.append(note)
        
        # Add select all/none buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Select All"):
                for i in range(len(st.session_state.qa)):
                    st.session_state[f"card_{i}"] = True
                st.rerun()
        with col2:
            if st.button("Select None"):
                for i in range(len(st.session_state.qa)):
                    st.session_state[f"card_{i}"] = False
                st.rerun()
        
        if notes:
            st.write(f"**Selected {len(notes)} cards to add to Anki**")
            if st.button("Add Selected Cards to Anki", type="primary"):
                with st.spinner("Adding cards to Anki..."):
                    result = add_notes(notes)
                if result:
                    st.success(f"Successfully added {len(result)} cards to Anki!")
                    st.balloons()
                else:
                    st.error("Failed to add cards to Anki. Please check your Anki connection.")
        else:
            st.info("Select at least one card to add to Anki.")

elif mode == "Review Cards":
    st.header("📝 Advanced Review Mode")
    
    # Start native review UI
    if st.button("Start Deck Review in Anki GUI"):
        invoke("guiDeckReview", {"name": deck})
    
    st.divider()
    
    # Review Mode Selection
    review_mode = st.radio(
        "Select Review Mode:",
        ["🎤🔊🤖 Enhanced TTS + ASR + LLM", "🎤🤖 ASR + LLM", "🔊 TTS Only"],
        horizontal=True,
        help="Enhanced mode uses human-like speech and emotional AI evaluation"
    )
    
    st.divider()
    
    # Find cards that are due or new for review
    with st.spinner("Loading cards for review..."):
        # Try to get due cards first
        due_card_ids = find_cards(f"deck:\"{deck}\" is:due")
        # Also get new cards
        new_card_ids = find_cards(f"deck:\"{deck}\" is:new")
        
        # Combine both lists and remove duplicates
        all_review_card_ids = list(set(due_card_ids + new_card_ids))
        
        # If no due/new cards, get all cards from the deck
        if not all_review_card_ids:
            all_review_card_ids = find_cards(f"deck:\"{deck}\"")
        
        # Get card information
        cards = get_cards_info(all_review_card_ids) if all_review_card_ids else []
    
    # Show what we found
    st.info(f"Found {len(due_card_ids)} due cards, {len(new_card_ids)} new cards, {len(cards)} total cards for review")
    
    if cards:
        # Initialize session state
        if 'current_card_idx' not in st.session_state:
            st.session_state.current_card_idx = 0
        if 'show_answer' not in st.session_state:
            st.session_state.show_answer = False
        if 'user_spoken_answer' not in st.session_state:
            st.session_state.user_spoken_answer = ""
        if 'llm_rating' not in st.session_state:
            st.session_state.llm_rating = None
        if 'llm_explanation' not in st.session_state:
            st.session_state.llm_explanation = ""
        if 'enhanced_question' not in st.session_state:
            st.session_state.enhanced_question = ""
        
        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Previous", disabled=st.session_state.current_card_idx == 0):
                st.session_state.current_card_idx = max(0, st.session_state.current_card_idx - 1)
                st.session_state.show_answer = False
                st.session_state.user_spoken_answer = ""
                st.session_state.llm_rating = None
                st.session_state.llm_explanation = ""
                st.session_state.enhanced_question = ""
                st.rerun()
        
        with col2:
            st.write(f"Card {st.session_state.current_card_idx + 1} of {len(cards)}")
        
        with col3:
            if st.button("Next ➡️", disabled=st.session_state.current_card_idx >= len(cards) - 1):
                st.session_state.current_card_idx = min(len(cards) - 1, st.session_state.current_card_idx + 1)
                st.session_state.show_answer = False
                st.session_state.user_spoken_answer = ""
                st.session_state.llm_rating = None
                st.session_state.llm_explanation = ""
                st.session_state.enhanced_question = ""
                st.rerun()
        
        # Current card
        current_card = cards[st.session_state.current_card_idx]
        
        # Extract card content safely
        def get_field_value(card, field_name):
            """Safely extract field value from card"""
            try:
                if 'fields' in card and field_name in card['fields']:
                    field_data = card['fields'][field_name]
                    if isinstance(field_data, dict) and 'value' in field_data:
                        return field_data['value']
                    elif isinstance(field_data, str):
                        return field_data
                return f"[{field_name} not found]"
            except Exception as e:
                return f"[Error accessing {field_name}: {e}]"
        
        # Get question and answer
        question = get_field_value(current_card, 'Front')
        answer = get_field_value(current_card, 'Back')
        
        # Display question
        st.markdown("### Question")
        st.markdown(f"**{question}**")
        
        # Show enhanced question info for Enhanced mode
        if review_mode == "🎤🔊🤖 Enhanced TTS + ASR + LLM" and st.session_state.enhanced_question:
            with st.expander("🤖 Enhanced Question for TTS", expanded=False):
                st.markdown("*This is how the AI will read the question with natural speech elements:*")
                st.markdown(f"**{st.session_state.enhanced_question}**")
        
        # TTS for question (for TTS modes)
        if review_mode in ["🎤🔊🤖 Enhanced TTS + ASR + LLM", "🔊 TTS Only"]:
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🔊 Read Question", key="tts_question"):
                    if review_mode == "🎤🔊🤖 Enhanced TTS + ASR + LLM":
                        # Enhanced mode: Question -> LLM -> TTS
                        with st.spinner("Enhancing question for natural speech..."):
                            if not st.session_state.enhanced_question:
                                st.session_state.enhanced_question = enhance_question_for_tts(question)
                        with st.spinner("Speaking enhanced question..."):
                            text_to_speech(st.session_state.enhanced_question)
                    else:
                        # Regular TTS mode
                        with st.spinner("Speaking question..."):
                            text_to_speech(question)
        
        # Answer input based on mode
        if review_mode == "🎤🔊🤖 Enhanced TTS + ASR + LLM":
            # Mode 1: TTS + ASR + LLM
            st.markdown("### Your Answer (Voice)")
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("🎤 Record Answer", key="record_answer"):
                    with st.spinner("Recording... Please speak your answer"):
                        spoken_text = speech_to_text()
                        if spoken_text:
                            st.session_state.user_spoken_answer = spoken_text
                            st.rerun()
            
            if st.session_state.user_spoken_answer:
                st.write(f"**Your spoken answer:** {st.session_state.user_spoken_answer}")
                
                # Show answer and get LLM evaluation
                if st.button("Show Answer & Get AI Evaluation", type="primary"):
                    st.session_state.show_answer = True
                    with st.spinner("AI is evaluating your answer..."):
                        rating, explanation = evaluate_answer_with_llm(question, answer, st.session_state.user_spoken_answer)
                        st.session_state.llm_rating = rating
                        st.session_state.llm_explanation = explanation
                    st.rerun()
        
        elif review_mode == "🎤🤖 ASR + LLM":
            # Mode 2: ASR + LLM (no TTS)
            st.markdown("### Your Answer (Voice)")
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("🎤 Record Answer", key="record_answer_asr"):
                    with st.spinner("Recording... Please speak your answer"):
                        spoken_text = speech_to_text()
                        if spoken_text:
                            st.session_state.user_spoken_answer = spoken_text
                            st.rerun()
            
            if st.session_state.user_spoken_answer:
                st.write(f"**Your spoken answer:** {st.session_state.user_spoken_answer}")
                
                # Show answer and get LLM evaluation
                if st.button("Show Answer & Get AI Evaluation", type="primary"):
                    st.session_state.show_answer = True
                    with st.spinner("AI is evaluating your answer..."):
                        rating, explanation = evaluate_answer_with_llm(question, answer, st.session_state.user_spoken_answer)
                        st.session_state.llm_rating = rating
                        st.session_state.llm_explanation = explanation
                    st.rerun()
        
        else:
            # Mode 3: TTS Only
            st.markdown("### Think of Your Answer")
            st.info("💭 Think of your answer in your mind, then reveal the correct answer below.")
            
            # Show answer button
            if not st.session_state.show_answer:
                if st.button("Show Answer", type="primary"):
                    st.session_state.show_answer = True
                    st.rerun()
        
        # Show answer and rating
        if st.session_state.show_answer:
            st.markdown("### Correct Answer")
            st.markdown(f"**{answer}**")
            
            # TTS for answer (for TTS modes)
            if review_mode in ["🎤🔊🤖 Enhanced TTS + ASR + LLM", "🔊 TTS Only"]:
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🔊 Read Answer", key="tts_answer"):
                        with st.spinner("Speaking answer..."):
                            text_to_speech(answer)
            
            # Show LLM evaluation for AI modes
            if review_mode in ["🎤🔊🤖 Enhanced TTS + ASR + LLM", "🎤🤖 ASR + LLM"] and st.session_state.llm_rating:
                st.markdown("### AI Evaluation")
                rating_colors = {1: "🔴", 2: "🟡", 3: "🟢", 4: "🔵"}
                rating_names = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
                
                st.markdown(f"**AI Suggested Rating:** {rating_colors.get(st.session_state.llm_rating, '⚪')} {st.session_state.llm_rating} - {rating_names.get(st.session_state.llm_rating, 'Unknown')}")
                st.markdown(f"**Evaluation:** {st.session_state.llm_explanation}")
                
                # Add TTS for human-like evaluation in Enhanced mode
                if review_mode == "🎤🔊🤖 Enhanced TTS + ASR + LLM":
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("🔊 Hear Evaluation", key="tts_evaluation"):
                            # Extract just the emotional response part for TTS
                            evaluation_text = st.session_state.llm_explanation
                            # Try to extract the emotional response part
                            if "Emotional Response:" in evaluation_text:
                                emotional_part = evaluation_text.split("Emotional Response:")[-1].strip()
                                with st.spinner("Speaking AI's emotional evaluation..."):
                                    text_to_speech(emotional_part)
                            else:
                                with st.spinner("Speaking AI evaluation..."):
                                    text_to_speech(evaluation_text)
                
                # Auto-apply AI rating or manual override
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"✅ Accept AI Rating ({st.session_state.llm_rating})", type="primary", use_container_width=True):
                        answer_cards([{"cardId": current_card['cardId'], "ease": st.session_state.llm_rating}])
                        st.success(f"Card rated as {rating_names.get(st.session_state.llm_rating)} by AI")
                        st.session_state.show_answer = False
                        st.session_state.user_spoken_answer = ""
                        st.session_state.llm_rating = None
                        st.session_state.llm_explanation = ""
                        st.session_state.enhanced_question = ""
                        time.sleep(1)
                        st.rerun()
                
                with col2:
                    st.markdown("**Manual Override:**")
            
            # Manual rating buttons
            st.markdown("### Rate Your Performance:")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🔴 Again (1)", type="secondary", use_container_width=True):
                    answer_cards([{"cardId": current_card['cardId'], "ease": 1}])
                    st.success("Card marked as 'Again'")
                    st.session_state.show_answer = False
                    st.session_state.user_spoken_answer = ""
                    st.session_state.llm_rating = None
                    st.session_state.llm_explanation = ""
                    st.session_state.enhanced_question = ""
                    time.sleep(1)
                    st.rerun()
            
            with col2:
                if st.button("🟡 Hard (2)", type="secondary", use_container_width=True):
                    answer_cards([{"cardId": current_card['cardId'], "ease": 2}])
                    st.success("Card marked as 'Hard'")
                    st.session_state.show_answer = False
                    st.session_state.user_spoken_answer = ""
                    st.session_state.llm_rating = None
                    st.session_state.llm_explanation = ""
                    st.session_state.enhanced_question = ""
                    time.sleep(1)
                    st.rerun()
            
            with col3:
                if st.button("🟢 Good (3)", type="secondary", use_container_width=True):
                    answer_cards([{"cardId": current_card['cardId'], "ease": 3}])
                    st.success("Card marked as 'Good'")
                    st.session_state.show_answer = False
                    st.session_state.user_spoken_answer = ""
                    st.session_state.llm_rating = None
                    st.session_state.llm_explanation = ""
                    st.session_state.enhanced_question = ""
                    time.sleep(1)
                    st.rerun()
            
            with col4:
                if st.button("🔵 Easy (4)", type="secondary", use_container_width=True):
                    answer_cards([{"cardId": current_card['cardId'], "ease": 4}])
                    st.success("Card marked as 'Easy'")
                    st.session_state.show_answer = False
                    st.session_state.user_spoken_answer = ""
                    st.session_state.llm_rating = None
                    st.session_state.llm_explanation = ""
                    st.session_state.enhanced_question = ""
                    time.sleep(1)
                    st.rerun()
        
        # Debug information (expandable)
        with st.expander("Debug Info", expanded=False):
            st.write(f"**Card ID:** {current_card.get('cardId', 'N/A')}")
            st.write(f"**Note ID:** {current_card.get('note', 'N/A')}")
            st.write(f"**Deck:** {current_card.get('deckName', 'N/A')}")
            st.write(f"**Model:** {current_card.get('modelName', 'N/A')}")
            st.write(f"**Review Mode:** {review_mode}")
            if st.session_state.user_spoken_answer:
                st.write(f"**Spoken Answer:** {st.session_state.user_spoken_answer}")
            if st.session_state.llm_rating:
                st.write(f"**AI Rating:** {st.session_state.llm_rating}")
            st.write("**Full card data:**")
            st.json(current_card)
    else:
        st.warning("No cards found for review in this deck.")
        st.markdown("**Possible reasons:**")
        st.markdown("- The deck is empty")
        st.markdown("- All cards have been reviewed recently")
        st.markdown("- AnkiConnect connection issue")
        st.markdown("\n**Try:**")
        st.markdown("- Add some cards first using the 'Add Cards' mode")
        st.markdown("- Check 'Deck Stats' to see if there are cards in the deck")
        st.markdown("- Make sure Anki is running with AnkiConnect enabled")

else:  # Deck Stats
    st.header(f"📊 Stats for Deck: {deck}")
    stats = get_deck_stats([deck]).get(str(deck), {})
    st.metric("Total in deck", stats.get("total_in_deck", 0))
    st.metric("New today", stats.get("new_count", 0))
    st.metric("Learning", stats.get("learn_count", 0))
    st.metric("Review", stats.get("review_count", 0))
    st.metric("Reviewed Today", get_num_reviewed_today())
    # Bar chart distribution
    import pandas as pd
    df = pd.DataFrame({
        "New": [stats.get("new_count",0)],
        "Learning": [stats.get("learn_count",0)],
        "Review": [stats.get("review_count",0)],
    })
    st.bar_chart(df)