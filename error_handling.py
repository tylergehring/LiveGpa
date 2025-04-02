import json
import requests
import test_key

from student import DotDict

def load_apiKeys(apiKey_filename):
    with open(apiKey_filename, 'r') as openfile:
        apiKeys = json.load(openfile)
        return apiKeys

def load_errors(error_cache_filename):
    with open(error_cache_filename, 'r') as openfile:
        errors_dict = json.load(openfile)
        return errors_dict

class Errors:
    def __init__(self):
        """goes through keys in error_cache and removes them from apiKeys if it is a bad key"""
        pass
        #self.filter_keys()
    

    def filter_keys(self, apiKey_list, apiKey_filename):
        """runs a test on the key and removes it from file if the key is bad"""
        apiKey_dict = load_apiKeys(apiKey_filename)
        
        for key in apiKey_list:
            t = test_key.Tests(key)
            err = t.key_test()
            if err == 'expired_token':
                for entry in apiKey_dict:
                    if entry['apiKey'] == key:
                        apiKey_dict.remove(entry)
                print(f"Expired_token: removed: {key}")

            elif err == 'revoked_access':
                for entry in apiKey_dict:
                    if entry['apiKey'] == key:
                        apiKey_dict.remove(entry)
                print(f"Revoked access: removing: {key}")

        with open(apiKey_filename, 'w') as outfile:
            json.dump(apiKey_dict, outfile)

if __name__=="__main__":
    err_handling = Errors()
    key_dict = load_apiKeys("apiKeys.json")
    apiKey_list = list()
    for entry in key_dict:
        apiKey_list.append(entry['apiKey'])
    
    err_handling.filter_keys(apiKey_list, "apiKeys.json")