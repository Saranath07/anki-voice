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
        print("Warning: key.txt file not found")
        return None

def check_server_health(base_url="http://localhost:3001"):
    """Check if the server is running and what endpoints are available"""
    print(f"\n=== Checking server health at {base_url} ===")
    
    # Try common health/status endpoints
    health_endpoints = [
        "/health",
        "/status",
        "/api/health",
        "/v1/health",
        "/",
        "/api",
        "/v1"
    ]
    
    for endpoint in health_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"Trying: {url}")
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    print(f"  Response: {response.json()}")
                except:
                    print(f"  Response: {response.text[:200]}")
            print()
        except requests.exceptions.RequestException as e:
            print(f"  Failed: {e}")
            print()

def try_workspace_endpoints(base_url="http://localhost:3001", workspace_slug="anki"):
    """Try different workspace endpoint patterns"""
    print(f"\n=== Trying workspace endpoints for '{workspace_slug}' ===")
    
    # Different possible endpoint patterns
    endpoints = [
        f"/workspace/{workspace_slug}/chat",
        f"/v1/workspace/{workspace_slug}/chat",
        f"/api/workspace/{workspace_slug}/chat",
        f"/api/v1/workspace/{workspace_slug}/chat",
        f"/workspaces/{workspace_slug}/chat",
        f"/v1/workspaces/{workspace_slug}/chat",
        f"/{workspace_slug}/chat",
        f"/chat/{workspace_slug}",
        f"/v1/chat/{workspace_slug}",
        f"/api/chat/{workspace_slug}"
    ]
    
    payload = {
        "message": "What is deep learning?",
        "mode": "chat",
        "sessionId": "test-session"
    }
    
    # Load API key for authentication
    api_key = load_api_key()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"Trying POST: {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  SUCCESS! Response: {response.json()}")
                return url, response.json()
            elif response.status_code != 404:
                print(f"  Response: {response.text[:200]}")
            print()
        except requests.exceptions.RequestException as e:
            print(f"  Failed: {e}")
            print()
    
    return None, None

def list_workspaces(base_url="http://localhost:3001"):
    """Try to find an endpoint that lists available workspaces"""
    print(f"\n=== Trying to list workspaces ===")
    
    endpoints = [
        "/workspaces",
        "/v1/workspaces",
        "/api/workspaces",
        "/api/v1/workspaces",
        "/workspace",
        "/v1/workspace"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"Trying GET: {url}")
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  SUCCESS! Workspaces: {json.dumps(data, indent=2)}")
                    return data
                except:
                    print(f"  Response: {response.text[:200]}")
            elif response.status_code != 404:
                print(f"  Response: {response.text[:200]}")
            print()
        except requests.exceptions.RequestException as e:
            print(f"  Failed: {e}")
            print()
    
    return None

def send_chat_message(message, workspace_slug="anki", session_id="python-session-1"):
    """Send chat message with proper authentication"""
    # Use the correct endpoint that we discovered
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
        print(f"\n=== Original endpoint test ===")
        print(f"Sending request to: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    print("=== Chat API Test ===")
    
    # Test the chat endpoint with authentication
    message = "Hello, how are you?"
    print(f"Sending message: '{message}'")
    
    response = send_chat_message(message, "anki", "user-123")
    
    if response:
        print("\n✅ SUCCESS! Chat Response:")
        print(json.dumps(response, indent=2))
    else:
        print("\n❌ Failed to get response")
        print("\nRunning diagnostic...")
        
        # Run diagnostics if the main request fails
        check_server_health()
        workspaces = list_workspaces()
        working_url, diag_response = try_workspace_endpoints()
        
        if working_url:
            print(f"\n✅ Found working endpoint: {working_url}")
        else:
            print("\n❌ No working chat endpoint found")
