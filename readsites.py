import requests
import base64
import sys
import os.path
import json
#Add in API ID and Key from apikey.py file
from apikey import headers, accountID


#function to poll imperva to pull the site_id
#def find_site_id(domain,accountID):
#        global headers
#        print("Pulling data")
#        for pageNum in range(0,4):
#                url = f'https://my.imperva.com/api/prov/v1/sites/list?account_id={accountID}&page_size=100&page_num={pageNum}'
#                listResponse = requests.post(url, headers=headers, timeout=20)
#                jsonListResponse = json.loads(listResponse.text)
#                sites = jsonListResponse['sites']
#                dns = jsonListResponse['dns']
#		for site in jsonListResponse['sites']:
#                        if site["domain"] == domain:
#                                return site['site_id']

#print("Pulling data")
#header = ['Site ID', 'Domain','Origin Server IP(s)', 'Site Status(Active/Bypass)']
#print(header)
for pageNum in range(1):
	url = f'https://my.imperva.com/api/prov/v1/sites/list?account_id={accountID}&page_size=2&page_num={pageNum}'
	listResponse = requests.post(url, headers=headers)
	jsonListResponse = json.loads(listResponse.text)
	for site in jsonListResponse['sites']:
		url = f"https://my.imperva.com/api/prov/v1/sites/status?site_id={site['site_id']}&tests=domain_validation,services,dns"
		statusResponse = requests.request("POST", url, headers=headers)
		jsonStatusObject = json.loads(statusResponse.text)
		stringIps = ' | '.join(map(str, jsonStatusObject['ips']))
#		print(jsonStatusObject.keys())
		cl = (str, jsonStatusObject['dns'])
#		cname = cl.split()
#		print(cl[0])
#		print(cl[1])
		print(len(jsonStatusObject['dns']))
#		cname = cl[:2]
#		for x in cname:
#			print(x)
#		print(type(cname))
#		row = (f"{jsonStatusObject['site_id']} {jsonStatusObject['domain']} {stringIps} {cname} {jsonStatusObject['active']}").split()
#		print(type(cname))
#		print(jsonStatusObject)
#		print(row)


exit()
