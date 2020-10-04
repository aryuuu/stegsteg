import requests
import json

api_url = 'https://api.kripkrip.aryuuu.ninja/api/v1'

plain = 'hello'
key = 'test'

req = requests.post(
    api_url+'/extended-vigenere/enc', 
    data = {
        'plain': plain,
        'key': key
     })

res = json.loads(req.text)

print(res['message'])