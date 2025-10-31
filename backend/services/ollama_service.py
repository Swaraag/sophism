import ollama

async def init_ollama():
    '''Verify the Ollama model is running and working properly.'''
    try:
        response = ollama.generate(model='llama3.1:8b', prompt="Test")
        if not response or not response.get("response"):
            raise Exception("Ollama returned an empty response.")
        print("The Ollama service is ready and working.")
    except ollama.ResponseError as e:
        raise Exception(f"Ollama error: {e}")