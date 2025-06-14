#!/usr/bin/env python3
"""
Simple Speech-to-Text and Text-to-Speech Test Script
Tests both functionalities that AnythingLLM uses locally
"""

import speech_recognition as sr
import pyttsx3
import pyaudio
import wave
import tempfile
import os
from chat_client import send_chat_message

def test_speech_to_text():
    """Test speech-to-text using the same approach as AnythingLLM's local whisper"""
    print("🎤 Testing Speech-to-Text (like AnythingLLM's whisper-tiny)")
    print("=" * 50)
    
    # Initialize recognizer
    r = sr.Recognizer()
    
    # Use microphone
    with sr.Microphone() as source:
        print("🔧 Adjusting for ambient noise... Please wait")
        r.adjust_for_ambient_noise(source)
        print("🎤 Say something! (I'm listening for 5 seconds)")
        
        try:
            # Listen for audio
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            print("✅ Audio captured! Processing...")
            
            # Try to recognize speech using Google (similar to whisper)
            try:
                text = r.recognize_google(audio)
                print(f"📝 Transcribed text: '{text}'")
                return text
            except sr.UnknownValueError:
                print("❌ Could not understand the audio")
                return None
            except sr.RequestException as e:
                print(f"❌ Error with speech recognition: {e}")
                return None
                
        except sr.WaitTimeoutError:
            print("❌ No speech detected within timeout")
            return None

def test_text_to_speech(text):
    """Test text-to-speech using system native TTS (like AnythingLLM)"""
    print("\n🔊 Testing Text-to-Speech (like AnythingLLM's system native)")
    print("=" * 50)
    
    if not text:
        text = "Hello! This is a test of the text to speech functionality."
    
    try:
        # Initialize TTS engine (system native)
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        if voices:
            print(f"🎭 Using voice: {voices[0].name}")
            engine.setProperty('voice', voices[0].id)
        
        # Set speech rate
        engine.setProperty('rate', 200)
        
        print(f"🔊 Speaking: '{text}'")
        engine.say(text)
        engine.runAndWait()
        print("✅ Text-to-speech completed!")
        
    except Exception as e:
        print(f"❌ Error with text-to-speech: {e}")

def test_full_voice_chat():
    """Test complete voice chat workflow like AnythingLLM"""
    print("\n🎙️ Testing Full Voice Chat Workflow")
    print("=" * 50)
    
    # Step 1: Speech to text
    print("Step 1: Converting your speech to text...")
    user_text = test_speech_to_text()
    
    if not user_text:
        print("❌ Cannot proceed without speech input")
        return
    
    # Step 2: Send to AnythingLLM chat
    print(f"\nStep 2: Sending '{user_text}' to AnythingLLM...")
    try:
        response = send_chat_message(user_text, workspace_slug="anki")
        if response and response.get('textResponse'):
            bot_response = response['textResponse']
            print(f"🤖 AnythingLLM response: '{bot_response}'")
            
            # Step 3: Convert response to speech
            print("\nStep 3: Converting response to speech...")
            test_text_to_speech(bot_response)
            
        else:
            print("❌ No response from AnythingLLM")
            
    except Exception as e:
        print(f"❌ Error communicating with AnythingLLM: {e}")

def main():
    """Main function"""
    print("🎙️ Simple Speech Test for AnythingLLM")
    print("=" * 60)
    
    while True:
        print("\nChoose test:")
        print("1. Test Speech-to-Text only")
        print("2. Test Text-to-Speech only") 
        print("3. Test Full Voice Chat (Speech → AnythingLLM → Speech)")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            test_speech_to_text()
            
        elif choice == "2":
            text = input("Enter text to speak (or press Enter for default): ").strip()
            test_text_to_speech(text if text else None)
            
        elif choice == "3":
            test_full_voice_chat()
            
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    main()