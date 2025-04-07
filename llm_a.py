import requests


# Modelli utilizzabili:
# deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B (spesso occupato)
# meta-llama/Llama-3.2-3B-Instruct
# prova a vedere anche mistral

url= ""
token = "" # Inserire token personale per fare richiesta

def llm(query, injection):
    parameters = {
        "max_new_tokens": 5000,
        "temperature": 0.01,
        "top_k": 50,
        "top_p": 0.95,
        "return_full_text": False
        }
    
    prompt = """DOCUMENT:
            (document text)

            QUESTION:
            (users question)

            INSTRUCTIONS:
            Answer the users QUESTION using the DOCUMENT text above.
            Keep your answer ground in the facts of the DOCUMENT.
            If the DOCUMENT doesn't contain the facts to answer the QUESTION return {NONE}"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    prompt = prompt.replace("{query}", query)
    
    payload = {
        "inputs": prompt,
        "parameters": parameters
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response_text = response.json()[0]['generated_text'].strip()

    return response_text
