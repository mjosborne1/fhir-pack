import os, shutil
import json
import urllib
import unittest
import fetcher
from fhirclient.models import valueset as vs
from fhirpathpy import evaluate

API_ENDPOINT='https://tx.ontoserver.csiro.au/fhir'

def create_test_folder():
    homedir=os.environ['HOME']
    npm_dir = os.path.join(homedir,"tmp","ncts-npm-test")       
    if os.path.exists(npm_dir): 
        shutil.rmtree(npm_dir)
    os.makedirs(npm_dir) 
    return npm_dir

vs2="https://healthterminologies.gov.au/fhir/ValueSet/reason-vaccine-not-administered-3"

class TestFetcher(unittest.TestCase):    

    def test_get_valueset_fails(self):
        """
        Test that expand_values() returns a fails-to-expand message on this Valueset
        """
        npm_dir = create_test_folder()
        vs_url = "https://www.healthterminologies.gov.au/fhir/ValueSet/australian-dhs-modifications-pbs-mbs-dva-item-1"
        endpoint=API_ENDPOINT       
        max_values=40000
        resource_type = "ValueSet"
        resource_name = "australian-dhs-modifications-pbs-mbs-dva-item-1"
        resource_version = "1.0.2"
        resource_file_stem = os.path.join(npm_dir,f"{resource_type}_{resource_name}_{resource_version}")        
        result =  fetcher.expand_values(endpoint, vs_url, max_values, resource_file_stem)
        self.assertIn("ERROR: Unable to expand vs:", result)

    def test_get_valueset_succeeds(self):
        """
        Test that expand_values() returns a success message
        """
        npm_dir = create_test_folder()
        vs_url = "https://healthterminologies.gov.au/fhir/ValueSet/reason-vaccine-not-administered-3"
        endpoint=API_ENDPOINT       
        max_values=40000
        resource_type = "ValueSet"
        resource_name = "reason-vaccine-not-administered-3"
        resource_version = "3.0.0"
        resource_file_stem = os.path.join(npm_dir,f"{resource_type}_{resource_name}_{resource_version}")
        result =  fetcher.expand_values(endpoint, vs_url, max_values, resource_file_stem)
        self.assertIn("Created file for ", result)