import os
import json
from fhirpathpy import evaluate


def process_binding(category,ig_name,profile,value_set_dict):
    with open(profile) as f:
       data = json.load(f)
    if data and data["resourceType"] == "StructureDefinition":         
        snapshot = evaluate(data,f"{category}.element") 
        for el in snapshot:
            id = el["id"]
            vs_description = vs_strength = vs_canonical = ""
            if "binding" in el:              
                if "valueSet" in el["binding"]:
                    vs = el["binding"]["valueSet"]
                    if '|' in vs:
                        vs_canonical, vs_version = vs.split('|',1)
                    else:
                        vs_canonical = vs
                if "strength" in el["binding"]:
                    vs_strength = el["binding"]["strength"]
                if "description" in el["binding"]:
                    vs_description = el["binding"]["description"]
                vs_binding = [ ig_name, category, data["name"], id, vs_strength, vs_description ]
                value_set_dict.setdefault(vs_canonical, []).append(vs_binding)
            #    print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}'.format(vs_canonical,ig_name,category,data["name"],id,vs_canonical,vs_strength,vs_description))               
        return value_set_dict

def process_profile(ig_name,profile,value_set_dict):
    value_set_dict = process_binding("snapshot",ig_name,profile,value_set_dict)
    value_set_dict = process_binding("differential",ig_name,profile,value_set_dict)
    return value_set_dict


def process_ig(ig,value_sets):
    # Check if the folder exists
    folder_path=ig['folder']
    ig_name=ig['name']
    if os.path.exists(folder_path):
        # Iterate through files in the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.startswith("StructureDefinition") and file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    value_sets = process_profile(ig_name,file_path,value_sets)
        return value_sets



# Improvement - download a fhir npm package froma repo first, but to get this going 
# I have downloaded AU Base to /Users/osb074/data/npm/hl7.fhir.au.base@4.2.0-preview/node_modules
# and AU Core to /Users/osb074/data/npm/hl7.fhir.au.core@0.3.0-ballot/node_modules

def get_ig_vs():
    """
    Processes downloaded copies of AU FHIR IGs looking for bound ValueSets
    The canonical vs url is key to the returned dict 
    """
    with open('ig.json','r') as config_file:
        igs = json.load(config_file)
    value_sets = {}
    for ig in igs:
        print("Processing {0}".format(ig['name']))
        value_sets = process_ig(ig,value_sets)
   
    return value_sets