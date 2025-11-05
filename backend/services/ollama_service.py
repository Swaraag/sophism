import ollama
import json

async def init_ollama():
    '''Verify the Ollama model is running and working properly.'''
    try:
        response = ollama.generate(model='llama3.1:8b', prompt="Test")
        if not response or not response.get("response"):
            raise Exception("Ollama returned an empty response.")
        print("The Ollama service is ready and working.")
    except ollama.ResponseError as e:
        raise Exception(f"Ollama error: {e}")
    
async def detect_fallacies(transcript, fallacy_list):
    # transcript format: transcript = [{"speaker": "speaker1", "start": 0:00, "end": 0:25, "transcript": "Hi my name is..."}, ...]

    string_transcript = ""
    for dialogue in transcript:
        string_transcript += f"{dialogue['speaker']} ({dialogue['start']} - {dialogue['end']}s): {dialogue['transcript']}\n"

    messages = [
        {'role': 'system', 'content': 'You are an expert on logical fallacies and debate. '
        'Given this transcript, try to detect fallacies from either speaker. If no fallacy is detected, then respond with nothing. '
        'Do not try to respond with a fallacy if there is no fallacy detected.'
        'If a fallacy is detected, respond with JSON that can be read as a Python dictionary that provides the speaker who committed the fallacy, the type of fallacy, '
        'the statement which caused the fallacy, an explanation of why it is a fallacy, and a confidence level (between 0 and 1) for how likely it is to be a fallacy.'
        'The names of the fields are "speaker", "fallacy_type", "statement", "explanation", "confidence".'
        'Use the entire transcript for context, but only look for fallacies in the last couple dialogues or in relatively recent history.'},
        {'role': 'user', 'content': string_transcript}
        ]
    
    response = ollama.chat(model='llama3.1:8b', messages=messages)
    json_format = json.loads(response["message"]["content"])
    fallacy_list.append(json_format)