import os
import subprocess
import json
import urllib
import requests
from fhirpathpy import evaluate
import fhirclient.models.bundle as bundle
import fhirclient.models.codesystem as cs
import fhirclient.models.valueset as vs
import fhirclient.models.conceptmap as cm
import logging

logger = logging.getLogger(__name__)

def write_bundle_data(endpoint, token, outfile):
    """
    Write the syndicated bundles to outfile
    """
    headers = {
        'Authorization': f"{token['token_type']} {token['access_token']}",
        'Accept': 'application/fhir+json'
    }
    response = requests.get(endpoint, headers=headers)
    with open(outfile, 'wb') as f:
        f.write(response.content)


def count_valueset(vs_endpoint, valueset_url):
    """
    Count the total number of values in a ValueSet using a direct query 
    pass parameter count=1 to trick the query into expanding and including the total 
    even if it's >50K in size.
    """
    vsexp=vs_endpoint+'/ValueSet/$expand?url='
    query=vsexp+urllib.parse.quote(valueset_url,safe='')
    query = f"{query}&count=1"
    command = ['curl', '-H "Accept: application/fhir+json" ' , '--location', query]
    
    result = subprocess.run(command, capture_output=True)
    data =  json.loads(result.stdout)
    try:
      total_list = evaluate(data,"expansion.total")
    except Exception as e:
        logger.error(f'Failed to retrieve total for ValueSet: {e}')
        return -1
    total=-1
    if len(total_list) != 0:
        total = total_list[0]
    return total


def expand_valueset(vs_endpoint,offset,resource_file_stem):
    headers = {
        'Accept': 'application/fhir+json'
    } 
    response = requests.get(vs_endpoint, headers=headers)
    data = response.content
    resource_file = f"{resource_file_stem}-{offset}.json"
    with open(resource_file, 'wb') as output_file:
        output_file.write(data)
    output_file.close()
    return f"Created file for {resource_file} against {vs_endpoint}"


def expand_values(endpoint, vs_url, max_values, resource_file_stem):           
    """
    For ValueSets > 50K, create smaller files and indicate the offset in the filename
    Otherwise, just create the json file as per the valueset name passed from main
    """
    result = ""
    total = count_valueset(endpoint, vs_url)
    if total < 0:       
        return f"ERROR: Unable to expand vs: {vs_url} against server: {endpoint}"
    vs_total = int(total)
    offset = 0
    if vs_total > int(max_values):
        while offset < int(vs_total):
            params = f"count={max_values}&offset={offset}&includeDesignations=true&includeDefinition=true"
            vs_endpoint = f"{endpoint}/ValueSet/$expand?url="+urllib.parse.quote(f"{vs_url}",safe='')
            vs_endpoint = f"{vs_endpoint}&{params}"
            result = expand_valueset(vs_endpoint,offset,resource_file_stem)
            offset += int(max_values)
    else:
        params = f"includeDesignations=true&includeDefinition=true"
        vs_endpoint=f"{endpoint}/ValueSet/$expand?url="+urllib.parse.quote(f"{vs_url}",safe='')
        vs_endpoint = f"{vs_endpoint}&{params}"
        result = expand_valueset(vs_endpoint,offset,resource_file_stem)
    return result


def unbundle(endpoint,node_folder,max_values,file,ncts_vs):
    """
    Unbundle a bundled resource and expand any contents within
    """
    logger.info(f"Unbundling {file}")
    with open(file, 'r') as f:
        data = json.load(f)
        bundle_entry = bundle.Bundle(data)
        
        for entry in bundle_entry.entry:
            resource = entry.resource
            resource_type = resource.resource_type
            resource_name = resource.name
            resource_version = resource.version
            resource_file_stem = os.path.join(node_folder,f"{resource_type}_{resource_name}_{resource_version}")
            # Create a file for each expanded resource in the bundle named after the resource type and the ID
            if resource_type == "ValueSet":
                vs_url = resource.url
                if vs_url != None and (vs_url in ncts_vs):
                    result = expand_values(endpoint,vs_url,max_values,resource_file_stem)
                    logger.info(result)
            elif resource_type == "CodeSystem":
                logger.info(f"...writing CodeSystem: {resource.url}")
                #CodeSystems are complete in the bundle so simply write to file
                code_system_file = f'{resource_file_stem}.json'
                with open(code_system_file, "w") as f:
                    json.dump(resource.as_json(), f, indent=2)
            elif resource_type == "ConceptMap":
                logger.info(f"...writing ConceptMap: {resource.url}")
                concept_map_file = f'{resource_file_stem}.json'
                with open(concept_map_file, "w") as f:
                    json.dump(resource.as_json(), f, indent=2)
 