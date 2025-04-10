import pandas as pd
import os as os
import json
import re as r
from pprint import pprint
import unicodedata as uncd
import requests
import rdflib as rdf
from rdflib.namespace import SDO, RDF, RDFS
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
import SPARQLWrapper as sw


# extracting entities and objects from dataset
entities= dict()

with open("dev_data.json/dev_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for x in data:
    narration_unfixed_encoding = x['narration']
    narration_fixed = uncd.normalize("NFKC", narration_unfixed_encoding)
    narration_fixed = "".join(c for c in narration_fixed if uncd.category(c)[0] != "C")

    narration = narration_fixed
    main_event = x['Event_Name']
    main_event_triples = dict()

    for y in x['keep_triples']:
        main_event_triples[y[1]] = y[2]

    main_event_triples['type'] = x['types']
    main_event_triples['appears in'] = narration
    entities[main_event] = main_event_triples

    for z in x['entity_ref_dict']:
        entity = z
        event = x['entity_ref_dict'][z]

        narration = r.sub(entity, event, narration)

    for z in x['entity_ref_dict']:
        event = x['entity_ref_dict'][z]
        entities[event] = {'appears in':narration}

    if narration not in entities.keys():
        entities[narration] = {'type':'context_narration'}


# create graph and serialize as turtle 

base_uri = "https://github.com/ElleEsseDi/Semantic-Digital-Library-Project"

graph = rdf.Graph()

dictionary_of_objects = dict()
types = set()

id=1
for ent in entities.keys():
    dictionary_of_objects[ent] = f"{base_uri}/{id}"
    id+=1

for ent in entities.keys():
    info = entities[ent]
    for i in info.keys():
        #print(i)
        if i == 'type':
            if type(info[i]) == str:
                types.add(info[i])
                #types.add(base_uri+'/'+r.sub(' ','_',info[i]))
            elif type(info[i]) == list:
                for t in info[i]:
                    types.add(t)
    for t in types:
        graph.add((rdf.URIRef(base_uri+'/'+r.sub(' ','_',t)), RDFS.label, rdf.Literal(t)))
print(types)

for ent in entities.keys():
    info = entities[ent]
    for i in info.keys():
        pred = f"{base_uri}/{r.sub(' ','_',i)}"
        obj = info[i]
        if type(info[i]) == str:
            graph.add((rdf.URIRef(dictionary_of_objects[ent]), RDFS.label, rdf.Literal(ent)))

            if obj in types:
                graph.add((rdf.URIRef(dictionary_of_objects[ent]),rdf.URIRef(pred),rdf.URIRef(base_uri+'/'+r.sub(' ','_',obj))))

            elif obj not in dictionary_of_objects.keys():
                graph.add((rdf.URIRef(dictionary_of_objects[ent]),rdf.URIRef(pred),rdf.Literal(obj)))
                graph.add((rdf.URIRef(dictionary_of_objects[obj]), RDFS.label, rdf.Literal(obj)))

            elif obj in dictionary_of_objects.keys():
                graph.add((rdf.URIRef(dictionary_of_objects[ent]),rdf.URIRef(pred),rdf.URIRef(dictionary_of_objects[obj])))

        elif type(info[i]) == list:
            #if len(info[i]) == 1:
            #    graph.add((rdf.URIRef(dictionary_of_objects[ent]), rdf.URIRef(pred), rdf.Literal(info[i][0])))
            #else:
                for t in info[i]:
                    graph.add((rdf.URIRef(dictionary_of_objects[ent]), RDF.type, rdf.URIRef(base_uri+'/'+r.sub(' ','_',t))))


graph.serialize(destination="data2.ttl")