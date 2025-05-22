import os

import requests
from dotenv import load_dotenv

from graph_handler import GraphHandler
from llm_a import LSDAgentInterface
from recognition import EL

# Library Search Dude

# Prima di mandare la richiesta ricorda di attivare il database
graphdb_url = "http://localhost:7200"  # url per collegamenti esterni: http://DESKTOP-2TOL1V5:7200/repositories/SemDigLib
repostory_id = "SemDigLib"
path_file_triple = (
    "data7.ttl"  # Usato da un oggetto GraphHandler per creare il grafo dalle triple
)
# utilizzando il metodo load_triples

# L'utente fa la sua domanda
user_prompt = input("Whadda lookin foa?\n")
print("Lemme cooke broda...")

# Si riconoscono le entità contenute nella domanda
entities = EL(user_prompt)
print(entities)
# Si trovano i testi del knowledge-graph in base alle entità usando un oggetto GraphHandler
graphHandler = GraphHandler(graphdb_url, repostory_id)
contexts = graphHandler.search_contexts(entities)
print(type(contexts))
# print(contexts)

# Si inseriscono domanda dell'utente e testi selezionati nel prompt dell'LLM

load_dotenv()  # loading .env file containing API key

# Getting prompt text
with open("prompt.txt", mode="r", encoding="utf-8") as f:
    sys_prompt = f.read()

# Getting API key
key = os.environ.get("API_KEY")
if key is None:
    raise TypeError("key is None")

# Initalizing agent interface
agent = LSDAgentInterface(
    mode="remote",
    model="qwen/qwen3-235b-a22b:free",  # deepseek/deepseek-r1:free
    sys_prompt=sys_prompt,
    key=key,
)

agent.remote_call(query=user_prompt, contexts=contexts)

response = requests.get(
    url="https://openrouter.ai/api/v1/auth/key",
    headers={"Authorization": f"Bearer {key}"},
)

local = LSDAgentInterface(mode="local", model="deepseek-r1:8b", sys_prompt=sys_prompt)

local.local_call(query=user_prompt, contexts=contexts)
