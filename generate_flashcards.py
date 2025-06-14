import requests
import json
import time
from datetime import datetime

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

def load_prompt_template():
    """Load the prompt template from prompt_3.txt"""
    try:
        with open('prompt_3.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        print("Error: prompt_3.txt file not found")
        return None

def load_ml_facts():
    """Load ML facts from the database"""
    try:
        with open('dl_facts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: ml_facts_database.json file not found")
        return None

def send_chat_message(message, workspace_slug="anki", session_id="flashcard-generator"):
    """Send chat message to generate flashcards"""
    url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
    
    api_key = load_api_key()
    if not api_key:
        print("Error: No API key found")
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
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def generate_flashcards_for_fact(fact, prompt_template):
    """Generate flashcards for a single fact"""
    # Replace <INPUT_TEXT> with the actual fact
    prompt = prompt_template.replace('<INPUT_TEXT>', fact)
    
    print(f"Processing: {fact[:60]}...")
    
    response = send_chat_message(prompt)
    
    if response and 'textResponse' in response:
        return {
            "question": fact,
            "response": response['textResponse']
        }
    else:
        print(f"Failed to generate flashcards for: {fact[:60]}...")
        return {
            "question": fact,
            "response": "ERROR: Failed to generate response"
        }

def main():
    print("=== Flashcard Generator ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load required files
    prompt_template = load_prompt_template()
    if not prompt_template:
        return
    
    ml_facts = load_ml_facts()
    if not ml_facts:
        return
    
    # Collect all facts from all categories
    all_facts = []
    for category, facts in ml_facts.items():
        for fact in facts:
            all_facts.append({
                "category": category,
                "fact": fact
            })
    
    print(f"Found {len(all_facts)} facts to process")
    
    # Generate flashcards for each fact
    results = []
    
    for i, item in enumerate(all_facts, 1):
        print(f"\n[{i}/{len(all_facts)}] Category: {item['category']}")
        
        flashcard_data = generate_flashcards_for_fact(item['fact'], prompt_template)
        
        # Add category information
        flashcard_data['category'] = item['category']
        flashcard_data['fact_number'] = i
        
        results.append(flashcard_data)
        
        # Add a small delay to avoid overwhelming the API
        time.sleep(1)
    
    # Save results to file
    output_filename = f"flashcards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ SUCCESS!")
        print(f"Generated flashcards for {len(results)} facts")
        print(f"Results saved to: {output_filename}")
        
        # Print summary
        successful = sum(1 for r in results if not r['response'].startswith('ERROR:'))
        failed = len(results) - successful
        
        print(f"\nSummary:")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        
        # Show categories processed
        categories = {}
        for result in results:
            cat = result['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\nBy Category:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} facts")
            
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()