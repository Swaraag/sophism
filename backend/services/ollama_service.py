import ollama
import json
import os

# OLLAMA INSTRUCTIONS
current_dir = os.path.dirname(__file__)
ollama_instructions_path = os.path.join(current_dir, "ollama_instructions.txt")
try:
    with open(ollama_instructions_path, "r") as f:
        ollama_instructions = f.read()
except FileNotFoundError:
    print("Error: The file backend/services/ollama_instructions.txt was not found.")
except IOError as e:
    print(f"Error reading file: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# init_ollama() is called in main.py's lifespan() function
async def init_ollama():
    '''Verify the Ollama model is running and working properly.'''
    try:
        response = ollama.generate(model='llama3.1:8b', prompt="Test")
        if not response or not response.get("response"):
            raise Exception("Ollama returned an empty response.")
        print("The Ollama service is ready and working.")
    except ollama.ResponseError as e:
        raise Exception(f"Ollama error: {e}")

# detect_fallacies() is called in main.py's websocket_endpoint() function
async def detect_fallacies(transcript):
    # transcript format: transcript = [{"speaker": "speaker1", "start": 0:00, "end": 0:25, "transcript": "Hi my name is..."}, ...]
    fallacy_list = []
    if 'ollama_instructions' not in globals():
        print("Ollama instructions was not initialized properly.")
        return fallacy_list
    
    if not transcript:
        return fallacy_list
      
    has_content = any(seg.get('transcript', '').strip() for seg in transcript)
    if not has_content:
        print("No transcript content to analyze")
        return fallacy_list
    
    string_transcript = ""
    for dialogue in transcript:
        try:
            string_transcript += f"{dialogue['speaker']} ({dialogue['start']} - {dialogue['end']}s): {dialogue['transcript']}\n"
        except KeyError:
            print(f"Invalid dialogue format: {dialogue}")


    messages = [
            {'role': 'system', 'content': ollama_instructions},
            {'role': 'user', 'content': string_transcript}
            ]
    try:
        response = ollama.chat(model='llama3.1:8b', messages=messages, options={"temperature": 0})
    except ollama.ResponseError as e:
        print(f"Ollama ran into an error: {e}")
        return fallacy_list
    except Exception as e:
        print(f"Unexpected Ollama error: {e}")

    try:
        json_response = json.loads(response["message"]["content"])
    except json.JSONDecodeError:
        print("JSON DECODE ERROR")
        return fallacy_list
    if not isinstance(json_response, list):
        if isinstance(json_response, dict):
            json_response = [json_response]
        else:
            print("JSON RESPONSE ISNT LIST")
            return fallacy_list
    for fallacy in json_response:
        if check_fallacy_format(fallacy):
            fallacy_list.append(fallacy)
    return fallacy_list

def check_fallacy_format(fallacy):
    if fallacy is not None and fallacy != "" and isinstance(fallacy, dict):
        if all(key in fallacy for key in ['speaker', 'fallacy_type', 'statement', 'explanation', 'confidence']):
            return True
    return False