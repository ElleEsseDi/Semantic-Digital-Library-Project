import os

import requests
from dotenv import load_dotenv

from graph_handler import GraphHandler
from llm_a import LSDAgentInterface
from recognition import EL

# Library Search Dude

def main():
    # Prima di mandare la richiesta ricorda di attivare il database
    graphdb_url = "http://localhost:7200"
    repostory_id = "SemDigLib"

    # utilizzando il metodo load_triples

    # L'utente fa la sua domanda
    user_prompt = input("Hi! What are interested in?")
    print("Just a moment...")

    # Si riconoscono le entità contenute nella domanda
    try:
        entities = EL(user_prompt)
        print(entities)

    except requests.exceptions.JSONDecodeError:
        print("An error occurred while communicating with the EL API. Try running the query again")
        return
    except Exception as e:
        print(f"An error occurred during the EL step...\n{type(e): {e}}")
        return

    # Si trovano i testi del knowledge-graph in base alle entità usando un oggetto GraphHandler
    graphHandler = GraphHandler(graphdb_url, repostory_id)
    contexts = graphHandler.search_contexts(entities)
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
    remote_agent = LSDAgentInterface(
        mode="remote",
        model="deepseek/deepseek-r1:free",  # deepseek/deepseek-r1:free qwen/qwen3-235b-a22b:free
        sys_prompt=sys_prompt,
        key=key,
    )

    try:
        response = remote_agent.remote_call(query=user_prompt, contexts=contexts)
    except requests.exceptions.HTTPError as e:
        print(f"Failed to connect to the LLM service. \n{type(e)}: {e}.")
        return

    local_agent = LSDAgentInterface(mode="local", model="deepseek-r1:8b", sys_prompt=sys_prompt)

    try:
        local_response = local_agent.local_call(query=user_prompt, contexts=contexts)
    except Exception as e:
        print(f"A problem occurred while connecting to the remote model.\n{type(e)}: {e}.")
   
    return response

if __name__ == "__main__":
    main()
