# Port Scanner

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

Example
```
$ ./portscan.py 127.0.0.1
Starting scan of 127.0.0.1...
PORT    STATE
22      OPEN
80      OPEN
443     OPEN
```
