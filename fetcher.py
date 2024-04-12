import os
import json
import requests

import fhirclient.models.bundle as bundle

def write_json_data(endpoint, token, outfile):
    headers = {
        'Authorization': f"{token['token_type']} {token['access_token']}",
        'Accept': 'application/fhir+json'
    }
    response = requests.get(endpoint, headers=headers)
    with open(outfile, 'wb') as f:
        f.write(response.content)
   
def unbundle(args,node_folder,file):
    print(f"Unbundling {file}")
    
    with open(file, 'r') as f:
        data = json.load(f)
        bundle_entry = bundle.Bundle(data)
        
        for entry in bundle_entry.entry:
            resource = entry.resource
            resource_type = resource.resource_type
            resource_name = resource.name
            resource_version = resource.version
            resource_file = os.path.join(node_folder,f"{resource_type}_{resource_name}_{resource_version}.json")
             
            # Create a file for each resource in the bundle named after the resource type and the ID
            with open(resource_file, 'w') as output_file:
                json.dump(resource.as_json(), output_file, indent=2)
                print(f"Created file for {resource_type} with ID {resource_name}")

   