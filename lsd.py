from graph_handler import load_triples
from graph_handler import search_contexts
from recognition import EL


# Prima di mandare la richiesta ricorda di attivare il database
graphdb_url = "http://localhost:7200" # url per collegamenti esterni: http://DESKTOP-2TOL1V5:7200/repositories/SemDigLib
repostory_id = "SemDigLib"
path_file_triple = "data1.ttl"

# L'utente fa la sua domanda
user_prompt = input("Cosa stai cercando?\n")

# Si riconoscono le entità contenute nella domanda
entities = EL(user_prompt)

# Si trovano i testi del knowledge-graph in base alle entità
contexts = search_contexts(entities, graphdb_url, repostory_id)

# Si inseriscono domanda dell'utente e testi selezionati nel prompt dell'LLM

# Si restituisce la risposta all'utente

