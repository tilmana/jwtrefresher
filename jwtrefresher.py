# planning to add separate refresh argument

import sys
import requests
import json
import time
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description="""Refresher that helps to check absolute session timeout in applications that refresh tokens to maintain session validity""")
parser.add_argument('-e', '--endpoint', help='Refresh endpoint', required=True)
parser.add_argument('-j', '--jwt', type=str, help='Initial valid JWT to use', required=True)
parser.add_argument('-m', '--method', help='HTTP method (default GET)', required=False)
parser.add_argument('-p', '--proxy', help='Proxy to send requests with', required=False)
parser.add_argument('-d', '--delay', help='Delay in seconds between requests (default 30)', required=False, default=30, type=int)
parser.add_argument('-c', '--cookie', help='Set JWT into Cookie header with specified name instead of Authorization header', required=False)

args = parser.parse_args()

proxies = {
    'http': f'{args.proxy}',
    'https': f'{args.proxy}'
}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

totalRefreshes = 0
totalTime = 0

cookieHeader = None
requestHeader = None

if args.cookie:
    cookieHeader = {
        args.cookie: f'{args.jwt}'
    }
else:
    requestHeader = {
        'Authorization': f'Bearer {args.jwt}'
    }

def make_request(url, method, headers=None, cookies=None, proxy=None):
    http_method = getattr(requests, method.lower())
    res1 = http_method(url, headers=headers, cookies=cookies, proxies=proxy)
    return res1


def refresh(jwt):
    global totalRefreshes
    global totalTime
    if not args.method:
        r1 = make_request(args.endpoint, 'GET', requestHeader, cookieHeader, proxies)
    else:
        r1 = make_request(args.endpoint, args.method, requestHeader, cookieHeader, proxies)
    try:
        response_data = json.loads(r1.text)
    except:
        print(bcolors.WARNING + f"[!] Error while parsing JSON response, exiting... {datetime.now()}" + bcolors.ENDC)
        print(bcolors.BOLD + f'[+] Total refreshes: {totalRefreshes}    Total delay time: {totalTime}')
        sys.exit(-1)
    if 'token' in response_data:
        print(f"[+] New token: " + bcolors.OKCYAN + f"{response_data['token']}" + bcolors.ENDC)
        time.sleep(args.delay)
        refresh(response_data['token'])
        totalRefreshes += 1
        totalTime += args.delay
    else:
        print(bcolors.FAIL + f'[!] Token failed to refresh! {datetime.now()}' + bcolors.ENDC)
        print(bcolors.BOLD + f'[+] Total refreshes: {totalRefreshes}    Total delay time: {totalTime}')
    
print(bcolors.HEADER + f'[+] Starting jwtrefresher.py... {datetime.now()}' + bcolors.ENDC + "\n")
refresh(args.jwt)
