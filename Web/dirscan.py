#! /usr/bin/python3

import argparse
import requests
import threading
import queue
from urllib.parse import urlparse

def main(args):
    # Test Connection
    try:
        requests.get(url=args.url)
    except:
        print(f"Error connecting to url: {args.url}")
        return

    global status_codes
    status_codes = [int(s.strip()) for s in args.include_status.split(',')]
    status_codes_exclude = [int(s.strip()) for s in args.exclude_status.split(',')]
    for c in status_codes_exclude:
        if c in status_codes:
            status_codes.remove(c)
    
    #extensions = [''] + [(e.strip() for e in args.extensions.split(','))]

    # Get wordlist
    wordlist = open(args.wordlist,'r')
    global work_queue
    work_queue = queue.Queue()
    path_count = 0
    for path in wordlist:
        path_count += 1
        url = '/'.join(p.strip('/') for p in [args.url,path.strip('\n')])
        work_queue.put(url)

    # Print header
    print("************************************")
    print(f"URL:\t\t{args.url}")
    print(f"Status Codes:\t{status_codes}")
    print(f"Word List:\t{args.wordlist}")
    print(f"Count:\t\t{path_count}")
    print("************************************")
    print("STATUS\t\tPATH")
    print("------------------------------------")
    
    for _ in range(0,args.max_threads):
        t = threading.Thread(target=worker,daemon=True)
        t.start()

    work_queue.join()


def worker():
    while True:
        url = work_queue.get()
        checkUrl(url,'')
        work_queue.task_done()

def checkUrl(url,extension):
    if extension != '':
        url += '.' + extension

    try:
        r = requests.get(url=url)
        if r.status_code in status_codes:
            path = urlparse(url).path
            print(f"{r.status_code}\t\t{path}")
    except:
        pass




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='URL directory scanner. Example: python3 dirscan.py -w common.txt http://localhost:8000/MyWebsite/')
    parser.add_argument('url',
                        help='Base URL to scan.')
    parser.add_argument('-w','--wordlist',
                        help='Wordlist of paths to try')
    parser.add_argument('-s','--include_status',
                        default='200,201,202,203,301,302,307,308,401,403',
                        help='Comma list of HTTP status codes to include')
    parser.add_argument('-ns','--exclude_status',
                        help='Comma list of status codes to exclude')
    # parser.add_argument('-x','--extensions', help='Comma list of extensions to try.') #TODO: add support for this
    parser.add_argument('-m','--max_threads',default=25,type=int,
                        help='Maximum thread count to use when scanning.') 
    parser.add_argument('-v','--verbosity',action='count',default=0,
                        help='Increase verbosity of the scanned port messages.')                   
    args = parser.parse_args()
    main(args)