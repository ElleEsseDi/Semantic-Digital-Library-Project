import requests
import json


class GraphHandler():
    def __init__(self, db_url: str, repo_id: str):
        self.db_url = db_url
        self.repo_id = repo_id
        self.basic_endpoint = f"{db_url}/repositories/{repo_id}"

    def make_query(self, entity) -> list|None:
        prefixes = """
            prefix ns1: <https://github.com/ElleEsseDi/Semantic-Digital-Library-Project/>
            prefix ns2: <https://github.com/ElleEsseDi/Semantic-Digital-Library-Project/number_of_matches_played/races/>
            prefix ns3: <https://github.com/ElleEsseDi/Semantic-Digital-Library-Project/number_of_points/goals/>
            prefix ns4: <https://github.com/ElleEsseDi/Semantic-Digital-Library-Project/number_of_draws/>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            """

        query = prefixes + """
            SELECT ?context
            WHERE {
                ?s rdfs:label ?o
                FILTER( regex(?o, "[\D\d]*%s[\D\d]*", "i"))

                ?s ns1:appears_in ?context
                FILTER(isLiteral(?context))
            }
            """% entity
        
        

        # Set the headers
        headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/sparql-query'
        }

        # Send the query to the repository
        response = requests.post(self.basic_endpoint, data=query, headers=headers)

        # Check if the operation was successful
        if response.status_code == 200:
            print("Query executed successfully.")
            data = json.loads(response.json())
            contexts = [ context["value"] for context in data["results"]["bindings"] ]
            return contexts
        else:
            print(f"Failed to execute query: {response.status_code}")
            print(response.text)

    def search_contexts(self, entities) -> list:
        prompt_contexts = []
        for entity in entities:
            entity_contexts = self.make_query(entity)
            prompt_contexts.extend(entity_contexts)
        return prompt_contexts

    def load_triples(self, file_path) -> None:
        # mappatura estensioni file e valore corrispondete dell'header Content Type
        formats = {
            ".ttl":"application/x-turtle",
            ".nt":"application/n-triples",
            ".rdf":"application/rdf+xml",
            ".jsonld":"application/ld+json",
            ".n3":"text/rdf+n3",
            ".trig":"application/x-trig",
            ".trix":"application/trix",
            ".nq":"application/n-quads",
        }
        load_endpoint = self.basic_endpoint + "/statements"
        with open(file_path, 'rb') as file:
            triple = file.read()

        # Questo passaggio serve a generalizzare l'inserimento del valore di Content Type
        # di modo che sia valido per ogni tipo di formato di file che contiene le triple
        file_ext = file_path[file_path.find("."):]
        headers = {
            f"Content-Type": {formats[file_ext]}
        }

        response = requests.post(load_endpoint, headers=headers, data=triple)

        # Check if the operation was successful
        if response.status_code == 204:
            print("Data loaded successfully.")
        else:
            print(f"Failed to load data: {response.status_code}")
            print(response.text)
