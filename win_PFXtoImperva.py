import requests
import base64

from thiscert import *

with open(pemfile, "rb") as mycert:
     b64c = base64.b64encode(mycert.read()).decode('utf-8')
with open(keyfile, "rb") as mycert:
     pk = base64.b64encode(mycert.read()).decode('utf-8')

#Add in API ID and Key from apikey.py file
from apikey import headers

payload = {
  "certificate": b64c,
  "passphrase": pw,
  "private_key": pk,
  "auth_type": "RSA"
}

for id in site_id: 
    url = f"https://my.imperva.com/api/prov/v2/sites/{id}/customCertificate"
    response = requests.request("PUT", url, headers=headers, json=payload)
    print(response.text)

