import requests
import json

def send_chat_message(message, workspace_slug="anki"):
    # Try the standard API endpoint first
    url = f"http://localhost:3001/api/workspace/{workspace_slug}/chat"
    
    payload = {
        "message": message,
        "mode": "chat"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending request to: {url}")
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error Response: {response.text}")
            
            # If that fails, try the v1 endpoint
            v1_url = f"http://localhost:3001/v1/workspace/{workspace_slug}/chat"
            print(f"Trying v1 endpoint: {v1_url}")
            
            v1_response = requests.post(v1_url, json=payload, headers=headers)
            print(f"V1 Status Code: {v1_response.status_code}")
            
            if v1_response.status_code == 200:
                return v1_response.json()
            else:
                print(f"V1 Error Response: {v1_response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Test the chat functionality
if __name__ == "__main__":
    message = "Hello, how are you?"
    response = send_chat_message(message, "anki")
    
    if response:
        print("Chat Response:", json.dumps(response, indent=2))
