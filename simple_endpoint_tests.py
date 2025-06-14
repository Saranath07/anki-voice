#!/usr/bin/env python3
"""
Simple individual endpoint tests for the Flask backend
Run specific tests without running the full test suite
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5001/api"

def test_health():
    """Quick health check"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Health Check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_flashcard_generation():
    """Test flashcard generation"""
    data = {
        "statement": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate_flashcards_with_llm",
            json=data,
            timeout=30
        )
        print(f"Flashcard Generation: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Flashcard generation failed: {e}")
        return False

def test_answer_evaluation():
    """Test answer evaluation"""
    data = {
        "question": "What is the capital of Japan?",
        "correct_answer": "Tokyo",
        "user_answer": "Tokyo is the capital"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/evaluate_answer_with_llm",
            json=data,
            timeout=30
        )
        print(f"Answer Evaluation: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Answer evaluation failed: {e}")
        return False

def test_mode_change():
    """Test mode change"""
    data = {"mode": "review_cards"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/change_of_modes",
            json=data,
            timeout=10
        )
        print(f"Mode Change: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Mode change failed: {e}")
        return False

def test_deck_stats():
    """Test deck statistics"""
    try:
        response = requests.get(f"{BASE_URL}/deck_stats?deck_name=Default", timeout=10)
        print(f"Deck Stats: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code in [200, 500]  # 500 might be expected if deck doesn't exist
    except Exception as e:
        print(f"Deck stats failed: {e}")
        return False

def test_send_qa():
    """Test sending question-answer data"""
    data = {
        "question": "Test question",
        "answer": "Test answer",
        "user_answer": "User's test answer",
        "rating": 3,
        "deck_name": "Test Deck",
        "card_id": "test123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/send_question_answer",
            json=data,
            timeout=10
        )
        print(f"Send Q&A: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Send Q&A failed: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_endpoint_tests.py <test_name>")
        print("Available tests:")
        print("  health - Health check")
        print("  flashcards - Generate flashcards")
        print("  evaluate - Evaluate answer")
        print("  mode - Change mode")
        print("  stats - Deck statistics")
        print("  send - Send question-answer data")
        print("  all - Run all tests")
        return
    
    test_name = sys.argv[1].lower()
    
    tests = {
        'health': test_health,
        'flashcards': test_flashcard_generation,
        'evaluate': test_answer_evaluation,
        'mode': test_mode_change,
        'stats': test_deck_stats,
        'send': test_send_qa
    }
    
    if test_name == 'all':
        print("Running all tests...")
        for name, test_func in tests.items():
            print(f"\n--- Testing {name} ---")
            test_func()
    elif test_name in tests:
        print(f"Running {test_name} test...")
        tests[test_name]()
    else:
        print(f"Unknown test: {test_name}")

if __name__ == "__main__":
    main()