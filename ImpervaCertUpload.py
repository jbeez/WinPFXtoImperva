import requests
import base64
import sys
import os.path
import json
#Add in API ID and Key from apikey.py file
from apikey import headers, accountID

#Usage statement
argumentList = sys.argv
script = sys.argv[0]

if len(sys.argv) == 1:
        print('Usage: python3', script, ' domain site_id_number(optional, required if supplying password on command line) password(optional)')
        print('Have the key and pem file in the same directory')
        exit()


#Set the domain variable from command line argument
domain = (sys.argv[1])

#Set site_id if given on the command line
if len(sys.argv) >2:
        site_id = (sys.argv[2])

##Set pw if supplied on command line
if len(sys.argv) >3:
        pw = (sys.argv[3])
        
##Check if pw is set, if not prompt for it
if not 'pw' in locals():
        pw = input('Enter Key Password: ')


#function to poll imperva to pull the site_id
def find_site_id(domain,accountID):
        global headers
        print("This may take upto a minute to pull the siteID for", domain)
        for pageNum in range(0,4):
                url = f'https://my.imperva.com/api/prov/v1/sites/list?account_id={accountID}&page_size=100&page_num={pageNum}'
                listResponse = requests.post(url, headers=headers, timeout=20)
                jsonListResponse = json.loads(listResponse.text)
                data = jsonListResponse['sites']
                for site in jsonListResponse['sites']:
                        if site["domain"] == domain:
                                return site['site_id']

if not 'site_id' in locals():
        site_id = find_site_id(domain,accountID)


#check for pem file, if doesn't exist use pfx
#convert to b64 encoded strings to upload
pemfile = os.path.isfile('{}.pem'.format(domain))
if pemfile:
        with open('{}.pem'.format(domain), "rb") as mycert:
                b64c = base64.b64encode(mycert.read()).decode('utf-8')
        with open('{}.key'.format(domain), "rb") as mycert:
                pk = base64.b64encode(mycert.read()).decode('utf-8')
        payload = {
                "certificate": b64c,
                "passphrase": pw,
                "private_key": pk,
                "auth_type": "RSA"
                }
else:
        with open('{}.pfx'.format(domain), "rb") as mycert:
             b64c = base64.b64encode(mycert.read()).decode('utf-8')
        payload = {
                  "certificate": b64c,
                  "passphrase": pw,
                  "auth_type": "RSA"
                  }

#Upload the certificate
url = f"https://my.imperva.com/api/prov/v2/sites/{site_id}/customCertificate"
response = requests.request("PUT", url, headers=headers, json=payload)
jsonResponse = response.json()
if jsonResponse["res_message"] == "OK":
        print("Certificate installed for", domain)    
else:
        print("Status: ", jsonResponse["res_message"])
        jdebug = jsonResponse["debug_info"]
        for key in jdebug:
                if key != "id-info":
                        print(key, ":", jdebug[key])

exit()
