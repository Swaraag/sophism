
# messages = [
#         {'role': 'system', 'content': 'You are an expert on logical fallacies and debate. '
#         'Given this transcript, try to detect fallacies from either speaker. If no fallacy is detected, then respond with nothing. '
#         'If a fallacy is detected, respond with JSON that can be read as a Python dictionary that provides the speaker who committed the fallacy, the type of fallacy, '
#         'the statement which caused the fallacy, an explanation of why it is a fallacy, and a confidence level (between 0 and 1) for how likely it is to be a fallacy.'
#         'The names of the fields are "speaker", "fallacy_type", "statement", "explanation", "confidence".'
#         'Use the entire transcript for context, but only look for fallacies in the last couple dialogues or in relatively recent history.'},
#         {'role': 'user', 'content': "Speaker 1 (0–5s): I think investing in public transportation is essential—it reduces traffic, cuts pollution, and makes cities more accessible for everyone."
#         "Speaker 2 (5–9.5s): But if we spend more money on buses and trains, the government will end up raising taxes so high that people wont even be able to afford to live here anymore"
#         "Speaker 1 (9.5–14s): The long-term savings and environmental benefits outweigh the upfront costs, and improved transit could boost the economy by increasing mobility and job access."}
#         ]

# messages = [
#         {'role': 'system', 'content': ollama_instructions},
#         {'role': 'user', 'content': "Speaker 1 (0–5s): I believe implementing a four-day workweek could improve employee well-being and productivity, since studies show people accomplish more with better rest."
#         "Speaker 2 (5–9.5s): That’s a fair point, but some industries might struggle with reduced hours—customer service and healthcare, for example, need continuous coverage."
#         "Speaker 1 (9.5–14s): True, but we could pilot the model in sectors where it's more feasible first, then assess results before expanding it more broadly."}
#         ]
import ollama
import json

with open("backend/services/ollama_instructions.txt", "r") as f:
    ollama_instructions = f.read()
with open("backend/services/sample_debate_transcript.txt", "r") as f:
    debate_transcript = f.read()


messages = [
        {'role': 'system', 'content': ollama_instructions},
        {'role': 'user', 'content': debate_transcript}
        ]

response = ollama.chat(model='llama3.1:8b', messages=messages, options={'temperature': 0})
assistant_response = response['message']['content']
#print(assistant_response)
response_dict = json.loads(assistant_response)

print(type(response_dict))
print(response_dict)
