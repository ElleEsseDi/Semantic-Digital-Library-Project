import json
import os

import requests


class GraphHandler:
    def __init__(self, db_url: str, repo_id: str):
        self.db_url = db_url
        self.repo_id = repo_id
        self.basic_endpoint = f"{db_url}/repositories/{repo_id}"

    def make_query(self, entities: list) -> list | None:
        entities_joint = "'" + "' '".join(entities) + "'"

        prefixes = """
            prefix ns1: <https://github.com/ElleEsseDi/Semantic-Digital-Library-Project/>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            """

        query = (
            prefixes
            + """
            SELECT ?context
            WHERE {                
                VALUES ?linked_ent { %s } 

	            ?entity rdfs:label ?entityLabel;
	                    ns1:appears_in / rdfs:label ?context . 

	            FILTER(CONTAINS(LCASE(STR(?entityLabel)), LCASE(?linked_ent)))
            }
            """
            % entities_joint
        )

        # Set the headers
        headers = {
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/sparql-query",
        }

        # Send the query to the repository
        response = requests.post(self.basic_endpoint, data=query, headers=headers)

        # Check if the operation was successful
        if response.status_code == 200:
            print("Query executed successfully.")
            data = response.json()
            contexts = [d["context"]["value"] for d in data["results"]["bindings"]]
            return contexts
        else:
            print(f"Failed to execute query: {response.status_code}")
            print(response.text)

    def search_contexts(self, entities: list) -> list:
        if not entities:
            return []
        entity_contexts = self.make_query(entities)
        # prompt_contexts.extend(entity_contexts)
        return entity_contexts  # prompt_contexts

    def load_triples(self, file_path) -> None:
        # mappatura estensioni file e valore corrispondete dell'header Content Type
        formats = {
            ".ttl": "application/x-turtle",
            ".nt": "application/n-triples",
            ".rdf": "application/rdf+xml",
            ".jsonld": "application/ld+json",
            ".n3": "text/rdf+n3",
            ".trig": "application/x-trig",
            ".trix": "application/trix",
            ".nq": "application/n-quads",
        }
        load_endpoint = self.basic_endpoint + "/statements"
        with open(file_path, "rb") as file:
            triple = file.read()

        # Questo passaggio serve a generalizzare l'inserimento del valore di Content Type
        # di modo che sia valido per ogni tipo di formato di file che contiene le triple
        root, file_ext = os.path.splitext(file_path)
        headers = {f"Content-Type": {formats[file_ext]}}

        response = requests.post(load_endpoint, headers=headers, data=triple)

        # Check if the operation was successful
        if response.status_code == 200:
            print("Data loaded successfully.")
        else:
            print(f"Failed to load data: {response.status_code}")
            print(response.text)
