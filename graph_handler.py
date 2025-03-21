import requests

# Define the server URL and repository ID
server_url = "http://localhost:7200" # url per collegamenti esterni: http://DESKTOP-2TOL1V5:7200/repositories/SemDigLib
repo_id = "SemDigLib"

# Define the SPARQL query
query = """SELECT ?s ?p ?o WHERE { ?s ?p ?o . }"""


def make_query(query):
    # Set the headers
    headers = {
        'Accept': 'application/sparql-results+json',
        'Content-Type': 'application/sparql-query'
    }

    # Send the query to the repository
    response = requests.post(f"{server_url}/repositories/{repo_id}/query", data=query, headers=headers)

    # Check if the operation was successful
    if response.status_code == 200:
        print("Query executed successfully.")
        print(response.json())
    else:
        print("Failed to execute query.")


def load_triples(file_path):
    # Send the file to the repository
    with open(file_path, 'rb') as file:
        response = requests.post(f"{server_url}/repositories/{repo_id}/statements", data=file, headers=headers)

    # Check if the operation was successful
    if response.status_code == 204:
        print("Data loaded successfully.")
    else:
        print("Failed to load data.")