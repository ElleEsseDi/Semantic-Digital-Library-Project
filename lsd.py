from graph_handler import GraphHandler
from recognition import EL


# Prima di mandare la richiesta ricorda di attivare il database
graphdb_url = "http://localhost:7200" # url per collegamenti esterni: http://DESKTOP-2TOL1V5:7200/repositories/SemDigLib
repostory_id = "SemDigLib"
path_file_triple = "data1.ttl"

# L'utente fa la sua domanda
user_prompt = input("Cosa stai cercando?\n")

# Si riconoscono le entità contenute nella domanda
entities = EL(user_prompt)

# Si trovano i testi del knowledge-graph in base alle entità usando un oggetto GraphHandler
graphHandler = GraphHandler(graphdb_url, repostory_id)
contexts = graphHandler.search_contexts(entities)

# Si inseriscono domanda dell'utente e testi selezionati nel prompt dell'LLM

# Si restituisce la risposta all'utente

