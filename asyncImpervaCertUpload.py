import asyncio
import httpx
import requests
import base64
import sys
import ujson
import argparse

#Add in API ID and Key from apikey.py file
from apikey import headers, accountID


async def main():
    title = 'Imperva Cert Upload'
    footer = 'Please ensure the key and pem file are in the same directory!'

    p = argparse.ArgumentParser(description=title, epilog=footer, add_help=True, usage=f'{sys.argv[0]} <domain>|-h')
    p.add_argument('domain', type=str, help='domain.tld')
    p.add_argument(
        '-s', '--site_id',
        type=int,
        help='site id number (requires password)',
        required=False
    )
    p.add_argument(
        '-p', '--password',
        type=str,
        help='keyfile password (will be prompted for if not provided!)',
        required=False
    )
    args = p.parse_args()

    if not args.site_id:
        args.site_id = await find_site_id(args.domain)
        if not args.site_id:
            print("Provide a `site_id`")
            sys.exit(-1)

    payload = read_certstore(args.domain, args.password)
    upload_cert(args.domain, args.site_id, payload)


async def get_page(session, url):
    resp = await session.post(url)
    try:
        json_response = resp.json()
    except Exception as e:
        print(f"\t-> Error: {resp.text}({resp.status_code})")
        return []

    if not json_response.get('sites'):
        print(f"\t-> Error: {json_response['res_message']} -> ({resp.url})")
        return []

    return json_response['sites']


#function to poll imperva to pull the site_id
async def find_site_id(domain):
    print(f"This may take upto a minute to pull the siteID for '{domain}...")
    async with httpx.AsyncClient(base_url="https://my.imperva.com/api/prov/v1/sites", headers=headers) as session:
        pages = []
        for page in range(0,4):
            url = f'/list?account_id={accountID}&page_size=100&page_num={page}'
            pages.append(asyncio.ensure_future(get_page(session, url)))

        pages_json = await asyncio.gather(*pages)
        for sites in pages_json:
            if sites == []:
                continue
            print("\t-> Found list, searching for site_id")
            site_id = next((site['site_id'] for site in sites if site['domain'] == domain), None)
            if site_id:
                print(f"\t-> site_id: {site_id}")
                return site_id

        # shouldn't get here
        return None


#check for pem file, if doesn't exist use pfx
#convert to b64 encoded strings to upload
def read_certstore(domain, pw):
    # Python is more 'ask forgivness later'
    try:
        # Look for a .pfx file
        with open('{domain}.pfx', "rb") as file:
             b64c = base64.b64encode(file.read()).decode('utf-8')

        return {
            "certificate": b64c,
            "passphrase": pw,
            "auth_type": "RSA"
        }
    except (FileNotFoundError, OSError) as e:
        # If not a .pfx, look for .pem and .key
        try:
            with open(f'{domain}.pem', "rb") as file:
                b64c = base64.b64encode(file.read()).decode('utf-8')
            with open(f'{domain}.key', "rb") as file:
                pk = base64.b64encode(file.read()).decode('utf-8')

            return {
                "certificate": b64c,
                "passphrase": pw,
                "private_key": pk,
                "auth_type": "RSA"
            }
        except (FileNotFoundError, OSError) as e:
            print("Please, put the files where they belong: {e}")
            sys.exit(-1)


def upload_cert(site_id, domain, payload):
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


if __name__ == "__main__":
    asyncio.run(main())
