import ollama

messages = [
        {'role': 'system', 'content': 'You are an expert on logical fallacies and debate. '
        'Given this transcript, try to detect fallacies from either speaker. If no fallacy is detected, then respond with nothing. '
        'If a fallacy is detected, respond with JSON that provides the speaker who committed the fallacy, the type of fallacy, '
        'the statement which caused the fallacy, an explanation of why it is a fallacy, and a confidence level (between 0 and 1) for how likely it is to be a fallacy.'
        'The names of the fields are "speaker", "fallacy_type", "statement", "explanation", "confidence".'
        'Use the entire transcript for context, but only look for fallacies in the last couple dialogues or in relatively recent history.'},
        {'role': 'user', 'content': "Speaker 1 (0–5s): I think investing in public transportation is essential—it reduces traffic, cuts pollution, and makes cities more accessible for everyone."
        "Speaker 2 (5–9.5s): But if we spend more money on buses and trains, the government will end up raising taxes so high that people wont even be able to afford to live here anymore"
        "Speaker 1 (9.5–14s): The long-term savings and environmental benefits outweigh the upfront costs, and improved transit could boost the economy by increasing mobility and job access."}
        ]
    
response = ollama.chat(model='llama3.1:8b', messages=messages)
assistant_response = response['message']['content']
print(f"Assistant: {assistant_response}")