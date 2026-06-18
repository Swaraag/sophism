import ollama
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

current_dir = os.path.dirname(__file__)
ollama_instructions_path = os.path.join(current_dir, "ollama_instructions.txt")
try:
    with open(ollama_instructions_path, "r") as f:
        ollama_instructions = f.read()
except FileNotFoundError:
    logger.error("Error: backend/services/ollama_instructions.txt was not found.")
except IOError as e:
    logger.error(f"Error reading ollama_instructions.txt: {e}")
except Exception as e:
    logger.error(f"Unexpected error loading ollama_instructions.txt: {e}", exc_info=True)

async def init_ollama():
    '''Verify the Ollama model is running and working properly.'''
    try:
        response = ollama.generate(model='llama3.1:8b', prompt="Test")
        if not response or not response.get("response"):
            raise Exception("Ollama returned an empty response.")
        logger.info("Ollama service is ready.")
    except ollama.ResponseError as e:
        raise Exception(f"Ollama error: {e}")

async def detect_fallacies(full_transcript, new_segments):
    '''
    Analyzes new_segments for fallacies using full_transcript as context.
    Only flags fallacies present in new_segments to avoid re-detecting old ones.
    '''
    fallacy_list = []

    if 'ollama_instructions' not in globals():
        logger.error("Ollama instructions not initialized.")
        return fallacy_list

    if not new_segments:
        return fallacy_list

    has_content = any(seg.get('transcript', '').strip() for seg in new_segments)
    if not has_content:
        logger.info("New segments have no speech content, skipping fallacy detection.")
        return fallacy_list

    # full transcript gives the model context for who said what
    full_transcript_str = ""
    for dialogue in full_transcript:
        try:
            full_transcript_str += f"{dialogue['speaker']} ({dialogue['start']:.1f}–{dialogue['end']:.1f}s): {dialogue['transcript']}\n"
        except KeyError:
            logger.error(f"Invalid dialogue format: {dialogue}")

    # new segments tell the model exactly what to analyze
    new_segments_str = ""
    for dialogue in new_segments:
        try:
            new_segments_str += f"{dialogue['speaker']} ({dialogue['start']:.1f}–{dialogue['end']:.1f}s): {dialogue['transcript']}\n"
        except KeyError:
            logger.error(f"Invalid new segment format: {dialogue}")

    user_content = (
        f"FULL TRANSCRIPT (for context):\n{full_transcript_str}\n"
        f"ANALYZE ONLY THESE NEW STATEMENTS FOR FALLACIES:\n{new_segments_str}"
    )

    messages = [
        {'role': 'system', 'content': ollama_instructions},
        {'role': 'user', 'content': user_content}
    ]

    try:
        response = ollama.chat(model='llama3.1:8b', messages=messages, options={"temperature": 0})
        raw = response["message"]["content"]
        logger.info(f"Ollama raw response: {raw}")
        json_response = json.loads(raw)
    except ollama.ResponseError as e:
        logger.error(f"Ollama error: {e}")
        return fallacy_list
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error — raw response: {response['message']['content']}")
        logger.error(e)
        return fallacy_list
    except Exception as e:
        logger.error(f"Unexpected Ollama error: {e}", exc_info=True)
        return fallacy_list

    if not isinstance(json_response, list):
        if isinstance(json_response, dict):
            json_response = [json_response]
        else:
            logger.error("Ollama response is not a list or dict")
            return fallacy_list

    for fallacy in json_response:
        if _valid_fallacy(fallacy):
            fallacy_list.append(fallacy)

    return fallacy_list

def _valid_fallacy(fallacy):
    return (
        fallacy is not None
        and fallacy != ""
        and isinstance(fallacy, dict)
        and all(key in fallacy for key in ['speaker', 'fallacy_type', 'statement', 'explanation', 'confidence'])
    )
