import os
import json
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("main")

_client = None

current_dir = os.path.dirname(__file__)
ollama_instructions_path = os.path.join(current_dir, "ollama_instructions.txt")
try:
    with open(ollama_instructions_path, "r") as f:
        ollama_instructions = f.read()
except Exception as e:
    logger.error(f"Failed to load ollama_instructions.txt: {e}")

def init_ollama():
    global _client
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not set in environment.")
    _client = Groq(api_key=api_key)
    # lightweight connectivity check
    _client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=1,
    )
    logger.info("Groq (fallacy detection) service ready.")

async def detect_fallacies(full_transcript, new_segments):
    '''
    Analyzes new_segments for fallacies using full_transcript as context.
    Uses Groq's llama-3.1-8b-instant instead of local Ollama.
    '''
    fallacy_list = []

    if _client is None:
        logger.error("Groq client not initialized.")
        return fallacy_list

    if 'ollama_instructions' not in globals():
        logger.error("Ollama instructions not loaded.")
        return fallacy_list

    if not new_segments:
        return fallacy_list

    has_content = any(seg.get('transcript', '').strip() for seg in new_segments)
    if not has_content:
        return fallacy_list

    full_transcript_str = ""
    for d in full_transcript:
        try:
            full_transcript_str += f"{d['speaker']} ({d['start']:.1f}–{d['end']:.1f}s): {d['transcript']}\n"
        except KeyError:
            pass

    new_segments_str = ""
    for d in new_segments:
        try:
            new_segments_str += f"{d['speaker']} ({d['start']:.1f}–{d['end']:.1f}s): {d['transcript']}\n"
        except KeyError:
            pass

    user_content = (
        f"FULL TRANSCRIPT (for context):\n{full_transcript_str}\n"
        f"ANALYZE ONLY THESE NEW STATEMENTS FOR FALLACIES:\n{new_segments_str}"
    )

    try:
        response = _client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": ollama_instructions},
                {"role": "user",   "content": user_content},
            ],
            temperature=0,
        )
        raw = response.choices[0].message.content
        logger.info(f"Groq raw response: {raw}")
        json_response = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error from Groq: {e} — raw: {raw}")
        return fallacy_list
    except Exception as e:
        logger.error(f"Groq error: {e}", exc_info=True)
        return fallacy_list

    if not isinstance(json_response, list):
        json_response = [json_response] if isinstance(json_response, dict) else []

    for fallacy in json_response:
        if _valid_fallacy(fallacy):
            fallacy_list.append(fallacy)

    return fallacy_list

def _valid_fallacy(f):
    return (
        isinstance(f, dict)
        and all(k in f for k in ['speaker', 'fallacy_type', 'statement', 'explanation', 'confidence'])
    )
