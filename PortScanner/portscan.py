#! /usr/bin/python3
import argparse
import ipaddress
import socket
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

class State(Enum):
    """
    State of the port
    """
    OPEN = 0
    CLOSED = 1

    def __str__(self):
        return self.name

def main(args):

    ip = ipaddress.ip_address(args.ip).exploded
    ports = get_ports(args.port)
    global verbosity
    verbosity = args.verbosity
    timeout = args.timeout
    # Scan ports
    print(f"Starting scan of {ip}...")

    results = {}
    with ThreadPoolExecutor(args.max_threads) as executor:
        future_to_port = {executor.submit(scan_port,ip,port,timeout): port for port in ports}
        try:
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                result = future.result()
                results[port] = result
        except KeyboardInterrupt:
            executor.shutdown(wait=False,cancel_futures=True)
            print("\n\rScan terminiated by user...\n\r")
            

    if verbosity >= 2:
        print("PORT\tSTATE\tMESSAGE")
    else:
        print("PORT\tSTATE")    
    
    for port in sorted(results):
        print_status(port,results[port][0],results[port][1])

def get_ports(arg_ports):
    """
    Generate an array of ports to scan. Ports can be a comma separated list or an inclusive range denoted by start-end.
    If no ports are provided then default to the list of most common ports.
    """
    ports = []
    if arg_ports and (not arg_ports.isspace()):
        for port in arg_ports.split(','):
            if port.find('-') != -1:
                (start,end) = [int(r) for r in port.split('-')]
                for p in range(start,end+1):
                    ports.append(p)
            else:
                ports.append(int(port))
    else:
        for p in range(1,10001):
            ports.append(p)
    return set(ports)

def scan_port(ip, port,timeout):
    """
    Checks if the port is open for the ip address
    """
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
        client.settimeout(timeout)
        try:
            client.connect((ip,port))
            return (State.OPEN,"")
        except Exception as ex:
            return (State.CLOSED,ex)
        finally:
            client.close()

def print_status(port, state, message = None):
    """
    Prints the status of the port
    """
    if verbosity == 0 and state == State.OPEN:
        print(f"{port}\t{state}")
    if verbosity == 1:
        print(f"{port}\t{state}")
    if verbosity >= 2:
        if message:
            print(f"{port}\t{state}\t{message}")
        else:
            print(f"{port}\t{state}")
    

################################
if __name__ == "__main__":
    # Define arguments
    parser = argparse.ArgumentParser(description="Network scanner for open ports on a machine.")
    parser.add_argument("ip",
                        help="IP addresses to scan")
    parser.add_argument("-p","--port",
                        help="Ports to scan.\n\rEx: -p 22; -p 80,443; -p 1-65535")
    parser.add_argument("-v","--verbosity",action="count",default=0,
                        help="Increase verbosity of the scanned port messages.")
    parser.add_argument("-t","--timeout",type=float, default=1.0,
                        help="Connection timeout in seconds. Default: 1s")
    parser.add_argument("-m","--max_threads",default=1000,type=int,
                        help="Maximum thread count to use when scanning ports.")
    # Parse arguments
    args = parser.parse_args()
    main(args)    