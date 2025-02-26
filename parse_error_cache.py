import json

def parse_error_cache(filename):
        with open(filename, 'r') as openfile:
            errors = json.load(openfile)
            for error in errors:
                try:
                     print(error[0]['expired_apiKey_error'])
                except Exception as e:
                    pass

if __name__=="__main__":
     parse_error_cache("error_cache.json")