import pandas as pd
import os as os
import json
import re as r
from pprint import pprint
import unicodedata as uncd
import requests
import rdflib as rdf
from rdflib.namespace import SDO, RDF, RDFS, NamespaceManager
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
import SPARQLWrapper as sw

entities= dict()

with open("dev_data.json/dev_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    #data = uncd.normalize("NFKC", data)

for p in data:
    narrat = p['narration']
    for z in p['entity_ref_dict']:
        ent = z
        eve = p['entity_ref_dict'][z]
        narrat = r.sub(ent, eve, narrat)
    #print(narrat)

LSD = rdf.Namespace("https://github.com/ElleEsseDi/Semantic-Digital-Library-Project")

graph = rdf.Graph()
graph.bind("lsd", LSD)

nm = NamespaceManager(graph)
nm.bind("lsd", LSD, override=False)
graph.namespace_manager = nm

narr_idx = 1
for x in data:    

    narration_unfixed_encoding = x['narration']
    narration_fixed = uncd.normalize("NFKC", narration_unfixed_encoding)
    narration_fixed = "".join(c for c in narration_fixed if uncd.category(c)[0] != "C")

    narration = LSD[f"/narration/{narr_idx}"]
    narr_idx = narr_idx + 1
    main_event = x['Event_Name']
    main_event_triples = dict()

    for y in x['keep_triples']:
        main_event_triples[y[1]] = y[2]

    main_event_triples['type'] = x['types']
    main_event_triples['appears in'] = narration
    entities[main_event] = main_event_triples
    narration_string = narration_fixed
    for z in x['entity_ref_dict']:
        entity = z
        event = x['entity_ref_dict'][z]

        narration_string = r.sub(entity, event, narration_string)
    # print(narration_string)

    for z in x['entity_ref_dict']:
        event = x['entity_ref_dict'][z]
        entities[event] = {'appears in':narration}

    if narration not in entities.keys():
        entities[narration] = {'type':'Context_narration', "label": narration_string}

dictionary_of_objects = dict()
types = set()

id=1
for ent in entities.keys():
    dictionary_of_objects[ent] = LSD[f"/Entity-{id}"]
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
    current_type = LSD['/'+r.sub(' ','_',t)]
    #print(current_type)
    #break
    graph.add((LSD['/'+r.sub(' ','_',t)], RDFS.label, rdf.Literal(t)))
#print(types)
#print(len(types))

for ent in entities.keys():
    info = entities[ent]    
    
    for i in info.keys():
        pred = LSD[f"/{r.sub(' ','_',i)}"]
        obj = info[i]
        
        if "http" in ent:
            #print("here")
            if "type" in pred:
                graph.add((rdf.URIRef(dictionary_of_objects[ent]), RDF.type, LSD[f'/{obj}']))
            elif "label" in pred:
                graph.add((rdf.URIRef(dictionary_of_objects[ent]), RDFS.label, rdf.Literal(obj)))
        
        elif type(info[i]) == rdf.URIRef:
            #print("here")
            #print(dictionary_of_objects[obj])
            graph.add((rdf.URIRef(dictionary_of_objects[ent]), RDFS.label, rdf.Literal(ent)))
            graph.add((rdf.URIRef(dictionary_of_objects[ent]), RDF.type, LSD["Entity"]))
            if obj in types:
                print("here")
                graph.add((rdf.URIRef(dictionary_of_objects[ent]),rdf.URIRef(pred),LSD[f"/{r.sub(' ','_',obj)}"]))

            elif obj not in dictionary_of_objects.keys():
                print("here")
                graph.add((rdf.URIRef(dictionary_of_objects[ent]),rdf.URIRef(pred),rdf.Literal(obj)))

            elif obj in dictionary_of_objects.keys():
                #if "appears_in" in pred:
                    #print(pred)
                graph.add((rdf.URIRef(dictionary_of_objects[ent]),rdf.URIRef(pred),rdf.URIRef(dictionary_of_objects[obj])))

        elif type(info[i]) == list:
            #if len(info[i]) == 1:
            #    graph.add((rdf.URIRef(dictionary_of_objects[ent]), rdf.URIRef(pred), rdf.Literal(info[i][0])))
            #else:
                for t in info[i]:
                    current_type = LSD[f"/{r.sub(' ','_',t)}"]
                    graph.add((current_type, RDF.type, LSD["EntityType"]))
                    graph.add((rdf.URIRef(dictionary_of_objects[ent]), RDF.type, current_type))

graph.serialize(destination="dataFinal.ttl")