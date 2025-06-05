import os

import requests
from dotenv import load_dotenv

from graph_handler import GraphHandler
from llm_a import LSDAgentInterface
from recognition import EL


def run_test(user_prompt, test_id: str, log_path: str = "./"):

    graphdb_url = "http://localhost:7200"
    repostory_id = "SemDigLib"
    path_file_triple = (
        "data7.ttl"  # Usato da un oggetto GraphHandler per creare il grafo dalle triple
    )
    # utilizzando il metodo load_triples

    # Si riconoscono le entità contenute nella domanda
    try:

        entities = EL(user_prompt)
        print(entities)

    except requests.exceptions.JSONDecodeError:
        print(
            "An error occurred while communicating with the EL API. Try running the query again"
        )
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
        model="deepseek/deepseek-r1:free",
        sys_prompt=sys_prompt,
        key=key,
    )

    try:
        response = remote_agent.remote_call(query=user_prompt, contexts=contexts)
    except requests.exceptions.HTTPError as e:
        print(f"Failed to connect to the LLM service. \n{e}")
        return

    local_agent = LSDAgentInterface(
        mode="local", 
        model="deepseek-r1:8b", 
        sys_prompt=sys_prompt
    )

    try:
        local_response = local_agent.local_call(query=user_prompt, contexts=contexts)
    except Exception as e:
        print(
            f"A problem occurred while connecting to the remote model.\n{type(e)}: {e}."
        )
        return

    with open(os.path.join(log_path, "test_log.txt"), mode="a", encoding="utf-8") as f:
        highlighter_char = "#" * 5
        f.write("\n" * 3 + highlighter_char + f"TEST {test_id }" + highlighter_char)
        f.write("\n" + query + "\n")
        f.write("***Remote Answer***")
        f.write(response)
        f.write("\n***Local Answer***")
        f.write(local_response)


if __name__ == "__main__":

    QUERIES = [
        "What are the Pacific Games and the Olympic games? Perform a comparative analysis of the two."
        # "Tell me about the stock-market crash happened in 2001",
        # "What were historical relations between japanese and portuguese?",
        # "What was the most brutal terrorist attack in the latest centurty?",
        # "Who is Osama Bin Laden? What was his nationality?",
        # "Tell me about japanese art",
    ]

    for test_id, query in enumerate(QUERIES):
        print(f"TESTING QUERY: {query}")
        run_test(query, str(test_id))
