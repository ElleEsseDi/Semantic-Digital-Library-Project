import requests

API_URL = "https://rel.cs.ru.nl/api"

# The result is a list of lists. Each sublist contains all the information about the entity
# example [
#           [32, 6, 'Brunei', 'Brunei', 0.41698815739999634, 0.9571365714073181, 'LOC'],
#           [46, 33, '2013 World Aquatics Championships', '2013_World_Aquatics_Championships', 0.9093679332527397, 0.8765866309404373, 'MISC'],
#         ]
def EL(text) -> list:
    el_result = requests.post(API_URL, json={
        "text": text,
        "spans": []
    }).json()
    entities = []
    if el_result:
        for r in el_result:
            entities.append(r[2])
    return entities