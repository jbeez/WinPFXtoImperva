import requests
import base64
import sys
import os.path


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

#Set pw if supplied on command line
if len(sys.argv) >3:
        pw = (sys.argv[3])

#Check if pw is set, if not prompt for it
if not 'pw' in locals():
        pw = input('Enter Key Password: ')

#Check for domain.site_id file, prompt if we don't have site_id yet
sid = os.path.isfile('sites/{}.site_id'.format(domain))
if not 'site_id' in locals():
        if sid:
                setting_data = open('sites/{}.site_id'.format(domain), 'r')
                lines = setting_data.readlines()
                site_id = ''
                for i in lines:
                  site_id = site_id + i
        else:
                       site_id = input('Enter Numerical SiteID: ')

#Check for pfx file, if doesn't exist use pem and key            
#convert to b64 encoded strings for upload            
pfxfile = os.path.isfile('{}.pfx'.format(domain))
if pfxfile:
  with open('{}.pfx'.format(domain), "rb") as mycert:
     b64c = base64.b64encode(mycert.read()).decode('utf-8')
  payload = {
    "certificate": b64c,
    "passphrase": pw,
    "auth_type": "RSA"
    }
else:
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

  
#Add in API ID and Key from apikey.py file
from apikey import headers

#create sites directory in current directory if it doesn't exist
dirname = ("sites")
dir = os.path.isdir(dirname)
if not dir:
        os.makedirs(dirname)

#write out the site_id file if it doesn't exist
if not sid:
        with open ('sites/{}.site_id'.format(domain), 'x') as f:
                f.write(str(site_id))
        f.close()

for id in site_id.split(' '):
    url = f"https://my.imperva.com/api/prov/v2/sites/{id}/customCertificate"
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

