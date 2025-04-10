import requests
import ollama
from typing import Literal


# Modelli utilizzabili:
# deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B (spesso occupato)
# meta-llama/Llama-3.2-3B-Instruct
# prova a vedere anche mistral
class LSDAgentInterface:

    def __init__(self,
                 mode: Literal["remote", "local"],  
                 model : str,
                 prompt : str,
                 settings: dict,
                 sys_prompt = None,
                 key : str = None, 
                 endpoint : str = None
                 ):
        
        self.model = model
        self.sys_p = sys_prompt
        self.prompt = prompt
        self.settings = settings

        # Remote mode
        if mode == "remote": # Storing attributes to perform API calls to a remote LLM agent service
            if not (key and endpoint):
                raise TypeError("Specify a valid API key and an endpoint if you want to use a remote model")
            self.key = key
            self.endpoint = endpoint
            self.headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }
        # Local mode
        else:  
            if self._check_ollama_reqs(): # checking that ollama is running locally and the model was downloaded (pulled)
                self.client = ollama.Client() 
                if self.sys_p: # setting system prompt if specified
                    self.client.chat(model=self.model, messages=[{"role" : "system", "content" : self.sys_p}], options=self.settings)
            
            
    def _check_ollama_reqs(self):

        try:
            models_list = [info.model for info in ollama.list()["models"]]
            if not self.model in models_list:
                print(f"Model {self.model} not found. Please pull it with 'ollama pull {self.model}'")
                return False
            return True
        except requests.exceptions.ConnectionError:
            print("Ollama is not running. Please start Ollama service.")
            return False


    def remote_call(self, query):

        parameters = {
            "max_new_tokens": 5000,
            "temperature": 0.01,
            "top_k": 50,
            "top_p": 0.95,
            "return_full_text": False
            } #TODO: usare settings passati all'oggetto invece di questi paramateri
        
        
        prompt = self.prompt.replace("{query}", query)
        
        payload = {
            "inputs": self.prompt,
            "parameters": parameters
        }
        
        response = requests.post(self.endpoint, headers=self.headers, json=payload)
        response_text = response.json()[0]['generated_text'].strip()

        return response_text

    def local_call(self, query):

        prompt = self.prompt.format(QUERY=query)
        response = self.client.generate(model=self.model, prompt=prompt, options=self.settings)
        response_text = response["response"]

        return response_text
    
    
