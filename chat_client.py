import requests
import json

def load_api_key():
    """Load API key from key.txt file"""
    try:
        with open('key.txt', 'r') as f:
            content = f.read().strip()
            if content.startswith('API_KEY='):
                return content.split('=', 1)[1]
            return content
    except FileNotFoundError:
        print("Error: key.txt file not found")
        return None

def send_chat_message(message, workspace_slug="anki", session_id="python-session-1"):
    """Send chat message to the workspace"""
    # Use the correct endpoint
    url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("Error: No API key found. Please check key.txt file.")
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
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    # Interactive chat example
    print("=== Chat Client ===")
    print("Type 'quit' to exit")
    
    session_id = "interactive-session"
    
    while True:
        message = input("\nYou: ").strip()
        
        if message.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not message:
            continue
        
        print("Sending...")
        response = send_chat_message(message, "anki", session_id)
        
        if response:
            print(f"\nBot: {response['textResponse']}")
            if response.get('sources'):
                print(f"Sources: {len(response['sources'])} documents referenced")
        else:
            print("Failed to get response")