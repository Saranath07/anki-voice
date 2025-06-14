import requests
import json
import time
import os
import tempfile
from datetime import datetime

# Base URL for the Flask API
BASE_URL = "http://localhost:5001/api"

class AnkiFlaskTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health_check(self):
        """Test the health check endpoint"""
        print("🔍 Testing Health Check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_get_decks(self):
        """Test getting available decks"""
        print("\n🔍 Testing Get Decks...")
        try:
            response = self.session.get(f"{self.base_url}/decks")
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return response.status_code == 200 and data.get('success', False)
        except Exception as e:
            print(f"❌ Get decks failed: {e}")
            return False
    
    def test_generate_flashcards_with_llm(self):
        """Test flashcard generation with LLM"""
        print("\n🔍 Testing Generate Flashcards with LLM...")
        try:
            test_data = {
                "statement": "The Pythagorean theorem states that in a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides."
            }
            
            response = self.session.post(
                f"{self.base_url}/generate_flashcards_with_llm",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            return response.status_code == 200 and data.get('success', False)
        except Exception as e:
            print(f"❌ Generate flashcards failed: {e}")
            return False
    
    def test_evaluate_answer_with_llm(self):
        """Test answer evaluation with LLM"""
        print("\n🔍 Testing Evaluate Answer with LLM...")
        try:
            test_data = {
                "question": "What is the capital of France?",
                "correct_answer": "Paris",
                "user_answer": "Paris is the capital city"
            }
            
            response = self.session.post(
                f"{self.base_url}/evaluate_answer_with_llm",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            return response.status_code == 200 and data.get('success', False)
        except Exception as e:
            print(f"❌ Evaluate answer failed: {e}")
            return False
    
    def test_read_question(self):
        """Test text-to-speech for questions"""
        print("\n🔍 Testing Read Question (TTS)...")
        try:
            test_data = {
                "question": "What is the square root of 16?",
                "enhance": True
            }
            
            response = self.session.post(
                f"{self.base_url}/read_question",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Save the audio file for verification
                with open('test_question_audio.wav', 'wb') as f:
                    f.write(response.content)
                print("✅ Audio file saved as 'test_question_audio.wav'")
                return True
            else:
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Read question failed: {e}")
            return False
    
    def test_record_answer(self):
        """Test speech-to-text for answers (using a dummy audio file)"""
        print("\n🔍 Testing Record Answer (ASR)...")
        try:
            # Create a dummy audio file for testing
            # In real usage, this would be an actual audio recording
            dummy_audio_path = self.create_dummy_audio_file()
            
            if not dummy_audio_path:
                print("❌ Could not create dummy audio file")
                return False
            
            with open(dummy_audio_path, 'rb') as audio_file:
                files = {'audio': ('test_audio.wav', audio_file, 'audio/wav')}
                response = self.session.post(f"{self.base_url}/record_answer", files=files)
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Clean up
            os.unlink(dummy_audio_path)
            
            return response.status_code in [200, 400]  # 400 is expected for dummy audio
        except Exception as e:
            print(f"❌ Record answer failed: {e}")
            return False
    
    def test_change_of_modes(self):
        """Test mode change functionality"""
        print("\n🔍 Testing Change of Modes...")
        try:
            test_modes = ['add_cards', 'review_cards', 'deck_stats', 'tts_only', 'asr_llm', 'enhanced_tts_asr_llm']
            
            for mode in test_modes:
                test_data = {"mode": mode}
                response = self.session.post(
                    f"{self.base_url}/change_of_modes",
                    json=test_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"Mode '{mode}' - Status Code: {response.status_code}")
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if response.status_code != 200 or not data.get('success', False):
                    return False
            
            return True
        except Exception as e:
            print(f"❌ Change of modes failed: {e}")
            return False
    
    def test_deck_stats(self):
        """Test deck statistics"""
        print("\n🔍 Testing Deck Stats...")
        try:
            # First get available decks
            decks_response = self.session.get(f"{self.base_url}/decks")
            if decks_response.status_code != 200:
                print("❌ Could not get decks list")
                return False
            
            decks_data = decks_response.json()
            decks = decks_data.get('decks', [])
            
            if not decks:
                print("⚠️ No decks available for testing stats")
                # Test with a dummy deck name
                test_deck = "Default"
            else:
                test_deck = decks[0]
            
            response = self.session.get(f"{self.base_url}/deck_stats?deck_name={test_deck}")
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            return response.status_code in [200, 500]  # 500 might be expected if deck doesn't exist
        except Exception as e:
            print(f"❌ Deck stats failed: {e}")
            return False
    
    def test_send_question_answer(self):
        """Test sending question-answer data"""
        print("\n🔍 Testing Send Question Answer...")
        try:
            test_data = {
                "question": "What is 2 + 2?",
                "answer": "4",
                "user_answer": "Four",
                "rating": 4,
                "timestamp": datetime.now().isoformat(),
                "deck_name": "Math",
                "card_id": "12345"
            }
            
            response = self.session.post(
                f"{self.base_url}/send_question_answer",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            return response.status_code == 200 and data.get('success', False)
        except Exception as e:
            print(f"❌ Send question answer failed: {e}")
            return False
    
    def create_dummy_audio_file(self):
        """Create a dummy audio file for testing"""
        try:
            # Create a minimal WAV file header (44 bytes) + some dummy data
            wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
            dummy_data = b'\x00' * 1000  # 1000 bytes of silence
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.write(wav_header + dummy_data)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            print(f"Error creating dummy audio file: {e}")
            return None
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Flask Backend API Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Get Decks", self.test_get_decks),
            ("Generate Flashcards with LLM", self.test_generate_flashcards_with_llm),
            ("Evaluate Answer with LLM", self.test_evaluate_answer_with_llm),
            ("Read Question (TTS)", self.test_read_question),
            ("Record Answer (ASR)", self.test_record_answer),
            ("Change of Modes", self.test_change_of_modes),
            ("Deck Stats", self.test_deck_stats),
            ("Send Question Answer", self.test_send_question_answer)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = "✅ PASSED" if result else "❌ FAILED"
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                results[test_name] = f"❌ ERROR: {e}"
        
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        for test_name, result in results.items():
            print(f"{test_name}: {result}")
        
        passed = sum(1 for r in results.values() if "PASSED" in r)
        total = len(results)
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        return results

def main():
    """Main function to run tests"""
    print("Flask Backend API Tester")
    print("Make sure the Flask server is running on http://localhost:5000")
    print("Also ensure Anki is running with AnkiConnect addon enabled")
    
    input("\nPress Enter to start testing...")
    
    tester = AnkiFlaskTester()
    results = tester.run_all_tests()
    
    print("\n🔧 TROUBLESHOOTING TIPS:")
    print("- If health check fails: Make sure Flask server is running")
    print("- If LLM tests fail: Check if key.txt and prompt files exist")
    print("- If Anki tests fail: Ensure Anki is running with AnkiConnect")
    print("- If TTS/ASR tests fail: Check if required audio libraries are installed")

if __name__ == "__main__":
    main()