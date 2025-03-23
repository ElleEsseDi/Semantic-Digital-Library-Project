import requests
import json


def make_query(query, entity, db_url, repo_id):
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
            %s ns1:appears_in ?context
            FILTER(isLiteral(?context))
        }
        """% entity
    
    endpoint = f"{db_url}/repositories/{repo_id}"

    # Set the headers
    headers = {
        'Accept': 'application/sparql-results+json',
        'Content-Type': 'application/sparql-query'
    }

    # Send the query to the repository
    response = requests.post(endpoint, data=query, headers=headers)

    # Check if the operation was successful
    if response.status_code == 200:
        print("Query executed successfully.")
        data = json.loads(response.json())
        contexts = [ context["value"] for context in data["results"]["bindings"] ]
        return contexts
    else:
        print(f"Failed to execute query: {response.status_code}")
        print(response.text)


def load_triples(file_path, db_url, repo_id):
    # Send the file to the repository
    endpoint = f"{db_url}/repositories/{repo_id}/statements"
    with open(file_path, 'rb') as file:
        triple = file.read()

    headers = {
        "Content-Type": "application/x-turtle"
    }

    response = requests.post(endpoint, headers=headers, data=triple)

    # Check if the operation was successful
    if response.status_code == 204:
        print("Data loaded successfully.")
    else:
        print(f"Failed to load data: {response.status_code}")
        print(response.text)