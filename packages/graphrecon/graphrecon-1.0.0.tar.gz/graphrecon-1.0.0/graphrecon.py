#!/usr/bin/env python3
import argparse
import asyncio
import aiohttp
from urllib.parse import urljoin
__version__ = "1.0.0"

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[38;5;32m'
RESET = '\033[0m'

ENDPOINTS = [
    "api", "graphql", "api/graphql", "v1/graphql", "v2/graphql",
    "api/v1/graphql", "api/v2/graphql",
    "v1/api/graphql", "v2/api/graphql"
]


def Banner():
    print(r"""
  ________                    .__   __________                            
 /  _____/___________  ______ |  |__\______   \ ____   ____  ____   ____  
/   \  __\_  __ \__  \ \____ \|  |  \|       _// __ \_/ ___\/  _ \ /    \ 
\    \_\  \  | \// __ \|  |_> >   Y  \    |   \  ___/\  \__(  <_> )   |  \
 \______  /__|  (____  /   __/|___|  /____|_  /\___  >\___  >____/|___|  /
        \/           \/|__|        \/       \/     \/     \/           \/ 
                                                                v{}
                               {}@memirhan{}""".format(__version__, BLUE, RESET))


async def GraphQLScanner(url):
    foundURL = set()
    url = url if url.startswith(("http://", "https://")) else "http://" + url

    PAYLOAD = {"query": "{ __typename }"}
    HEADERS = {"Content-Type": "application/json"}

    semaphore = asyncio.Semaphore(15)
    timeout = aiohttp.ClientTimeout(total=6)
    connector = aiohttp.TCPConnector(ssl=False, limit=50)

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        headers=HEADERS
    ) as session:

        try:
            async with session.get(url, allow_redirects=True) as resp:
                if resp.status in (200, 301, 302):
                    print(f"{BLUE}[+] Site reachable ({resp.status}){RESET}")
        except aiohttp.ClientConnectorError:
            print(f"{RED}[-] Site not reachable{RESET}")
            return
        except asyncio.TimeoutError:
            print(f"{RED}[-] Site timed out{RESET}")
            return

        async def scan(ep):
            fullURL = urljoin(url.rstrip("/") + "/", ep).rstrip("/")
            async with semaphore:
                try:
                    async with session.post(fullURL, json=PAYLOAD) as resp:
                        if "application/json" in resp.headers.get("Content-Type", ""):
                            data = await resp.json()
                            if "data" in data or "errors" in data:
                                if fullURL not in foundURL:
                                    foundURL.add(fullURL)
                                    print(f"{GREEN}[+] GraphQL FOUND → {fullURL}{RESET}")
                except:
                    pass

        await asyncio.gather(*(scan(ep) for ep in ENDPOINTS))

    if not foundURL:
        print(f"{RED}[-] GraphQL NOT FOUND{RESET}")


def main():
    Banner()
    parser = argparse.ArgumentParser(description="Fast async GraphQL scanner")
    parser.add_argument("-u", "--url", required=True, help="Target site URL")
    args = parser.parse_args()

    print(f"{YELLOW}[*] Scanning is starting{RESET}")
    asyncio.run(GraphQLScanner(args.url))


if __name__ == "__main__":
    main()