import asyncio
import textwrap
from getpass import getpass
import httpx
import base64
import sys
import argparse
from urllib.request import getproxies

#Add in API ID and Key from apikey.py file
from apikey import headers, accountID

try:
    import winreg
except ImportError:
    pass



async def main():
    title = 'Imperva Cert Upload'
    footer = 'Must be called with either `pfx` or `key` options'

    p = argparse.ArgumentParser(description=title, epilog=footer, add_help=True)

    identifier_p = p.add_mutually_exclusive_group(required=True)
    identifier_p.add_argument('--domain', type=str, help='domain.tld')
    identifier_p.add_argument(
        '--site_id',
        type=int,
        help='site id number (requires password)',
    )

    sub_p = p.add_subparsers(help="Cert and Key Store Location help")
    pfx_p = sub_p.add_parser('pfx', help='PFX Store Type')
    pfx_p.add_argument(
        '--pfx_file',
        type=argparse.FileType('rb'),
        required=True
    )
    pfx_p.add_argument(
        '--password',
        type=str,
        help='keyfile password (will be prompted for if not provided!)',
        required=False
    )

    key_p = sub_p.add_parser('key', help='CertFile and KeyFile Store Type help')
    key_p.add_argument(
        '--key_file',
        type=argparse.FileType('r'),
        required=True,
    )
    key_p.add_argument(
        '--cert_file',
        type=argparse.FileType('r'),
        required=True,
    )
    key_p.add_argument(
        '--password',
        type=str,
        help='keyfile password (will be prompted for if not provided!)',
        required=False,
    )
    args = p.parse_args()

    if not hasattr(args, 'pfx_file') and not hasattr(args, 'key_file'):
        print("**You must specify either `pfx` or `key`**\n")
        pfx_p.print_help()
        print("\n--or--\n")
        key_p.print_help()
        return False

    if not args.password:
        # Securely read in password if one wasn't provided
        args.password = getpass(prompt='Private Key Password: ')

    payload = read_certstore(args)
    if not payload:
        # if we couldn't read in the files, exit
        happy_fun_times()
        return False

    if not args.site_id:
        args.site_id = await find_site_id(args.domain)
        if not args.site_id:
            print("Provide a valid `domain` or `site_id` next time")
            happy_fun_times()
            return False

    await upload_cert(args.site_id, payload)


async def get_page(session, url):
    try:
        resp = await session.post(url)
        json_response = resp.json()
    except TimeoutError as e:
        print(f"\t-> Timeout connecting to -> ({url})")
        return []

    except httpx.ConnectError as e:
        print(f"\t-> Connection failure to -> ({url})")
        return []

    except Exception as e:
        print(f"\t-> Error: {resp.text}({resp.status_code})")
        return []

    if not json_response.get('sites'):
        print(f"\t-> Error: {json_response['res_message']} -> ({resp.url})")
        return []

    return json_response['sites']


async def upload_cert(site_id, payload):
    print(f"Uploading Certificate for [{site_id}]")
    async with httpx.AsyncClient(base_url="https://my.imperva.com/api/prov/v2/sites", headers=headers, proxies=proxies) as session:
        url = f'{site_id}/customCertificate'
        resp = await session.put(url, json=payload)
        json_response = resp.json()

    if json_response["res_message"] == "OK":
        print(f"\t-> Certificate successfully installed for [{site_id}]")
    else:
        print("Status: ", json_response["res_message"])
        jdebug = json_response["debug_info"]
        for key in jdebug:
            if key != "id-info":
                print(f'\t{key}:{jdebug[key]}')


def get_proxies():
    # get local proxies (if any)
    dirty_proxies = getproxies()
    print(f"Dirty Proxies: {dirty_proxies}")
    clean_proxies = {}
    for proxy in dirty_proxies:
        if not proxy.endswith('://'):
            clean_proxies[f'{proxy}://'] = dirty_proxies[proxy]
        else:
            clean_proxies[proxy] = dirty_proxies[proxy]

    try:
        internetSettings = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
        print(f"Internet Settings: {internetSettings}")
    except OSError as e:
        print(f"Failed to read registry: {e}")

    return clean_proxies


async def find_site_id(domain):
    # function to poll imperva to pull the site_id
    print(f"Looking up siteID for [{domain}]...")
    async with httpx.AsyncClient(base_url="https://my.imperva.com/api/prov/v1/sites", headers=headers, proxies=proxies) as session:
        pages = []
        for page in range(0,4):
            url = f'/list?account_id={accountID}&page_size=100&page_num={page}'
            pages.append(asyncio.ensure_future(get_page(session, url)))

        pages_json = await asyncio.gather(*pages)
        for sites in pages_json:
            if sites == []:
                continue
            print("\t-> searching for site_id")
            site_id = next((site['site_id'] for site in sites if site['domain'] == domain), None)
            if site_id:
                print(f"\t-> site_id: {site_id}")
                return site_id

        # shouldn't get here
        return None


def read_certstore(args):
    #convert to b64 encoded strings to upload

    payload = {
        "passphrase": args.password,
        "auth_type": "RSA"
    }

    if hasattr(args, 'pfx_file'):
        try:
            # Look for a .pfx file
            b64c = base64.b64encode(args.pfx_file.read()).decode('utf-8')
            payload["certificate"] = b64c
        except (FileNotFoundError, OSError) as e:
            print(f"Put the files where they belong: {e}")
            return False
        finally:
            args.pfx_file.close()

    else:
        # If not a .pfx, look for .pem and .key
        try:

            b64c = base64.b64encode(args.cert_file.read()).decode('utf-8')
            pk = base64.b64encode(args.key_file.read()).decode('utf-8')
            payload["certificate"] = b64c
            payload["private_key"] = pk
        except (FileNotFoundError, OSError) as e:
            print(f"Put the files where they belong: {e}")
            return False
        finally:
            args.key_file.close()
            args.cert_file.close()

    return payload


def happy_fun_times():
    smile = """
    RXJyb3I=
    """
    print(base64.b64decode(smile).decode('utf-8'))


if __name__ == "__main__":
    proxies = get_proxies()
    print(f"Proxies: {proxies}")

    # Hack for issues with Windows event loop
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # don't quit if someone ctrl-c's me
        pass
