# Port Scanner
## Usage
Simple scanner to check if ports are open on a machine. 
```
usage: portscan.py [-h] [-p PORT] [-v] [-t TIMEOUT] [-m MAX_THREADS] ip

Network scanner for open ports on a machine.

positional arguments:
  ip                    IP addresses to scan

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Ports to scan. Ex: -p 22; -p 80,443; -p 1-65535
  -v, --verbosity       Increase verbosity of the scanned port messages.
  -t TIMEOUT, --timeout TIMEOUT
                        Connection timeout in seconds. Default: 1s
  -m MAX_THREADS, --max_threads MAX_THREADS
                        Maximum thread count to use when scanning ports.
```

## Example
```
$ ./portscan.py 127.0.0.1
Starting scan of 127.0.0.1...
PORT    STATE
22      OPEN
80      OPEN
443     OPEN
```

# Directory Scanner
## Usage
```
usage: dirscan.py [-h] [-w WORDLIST] [-s INCLUDE_STATUS] [-ns EXCLUDE_STATUS] [-x EXTENSIONS] [-m MAX_THREADS] [-v] url

URL directory scanner. Example: python3 dirscan.py -w common.txt http://localhost:8000/MyWebsite/

positional arguments:
  url                   Base URL to scan.

optional arguments:
  -h, --help            show this help message and exit
  -w WORDLIST, --wordlist WORDLIST
                        Wordlist of paths to try
  -s INCLUDE_STATUS, --include_status INCLUDE_STATUS
                        Comma list of HTTP status codes to include
  -ns EXCLUDE_STATUS, --exclude_status EXCLUDE_STATUS
                        Comma list of status codes to exclude
  -m MAX_THREADS, --max_threads MAX_THREADS
                        Maximum thread count to use when scanning.
  -v, --verbosity       Increase verbosity of the scanned port messages.
```
## Example
```
$ ./dirscan.py -w common.txt http://localhost:8000/MyWebsite/
************************************
URL:            http://localhost:8000/MyWebsite/
Status Codes:   [200, 201, 202, 203, 301, 302, 307, 308, 401, 403]
Word List:      common.txt
Count:          4712
************************************
STATUS          PATH
------------------------------------
200             /css
200             /js
```