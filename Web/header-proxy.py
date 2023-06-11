#! /usr/bin/python3
import argparse
from asyncio import StreamReader,StreamWriter,start_server, open_connection, run
from io import StringIO
from urllib.parse import urlparse, ParseResultBytes
from datetime import datetime

async def get_proxy_request(sr: StreamReader) -> tuple[ParseResultBytes, str]:
        start_line = await sr.readline()
        start_line = start_line.decode()
        method,uri,version = start_line.split(' ')

        if not uri.startswith('http'):
            uri = 'http://' + uri
        url = urlparse(uri)
        resource = url.path or '/'
        if url.query:
            resource += '?' + url.query
            
        # Read in headers
        headers = {}
        content_length = 0
        chunked = False
        while True:
            line = await sr.readline()
            if not line or not line.strip():
                break
            line = line.decode().rstrip()
            header,value = line.split(' ',1)
            headers[header] = value
            if header == 'Content-Length:':
                content_length = int(value)
            if header == 'Transfer-Encoding:' and value == 'chunked':
                chunked = True
        
        # Append injected headers
        if _headers:
            for header,value in _headers:
                headers[header] = value
            
        # Request body
        if chunked:
            lines = []
            while True:
                line = await sr.readline()
                if not line or not line.strip():
                    break
                lines.append(line.decode())
            body = ''.join(lines)
        else:
            body = await sr.readexactly(content_length)
            body = body.decode()

        # rebuild request message
        with StringIO() as req:
            req.write(' '.join([method,resource,version]))
            req.writelines(' '.join([key,headers[key],'\r\n']) for key in headers.keys())
            req.write('\r\n')
            if body:
                req.write(body)
            return url, req.getvalue()

        
async def get_response(sr: StreamReader) -> str:
        start_line = await sr.readline()
        start_line = start_line.decode()         
        # Read in headers
        headers = {}
        content_length = 0
        chunked = False
        while True:
            line = await sr.readline()
            if not line or not line.strip():
                break
            line = line.decode().rstrip()
            header,value = line.split(' ',1)
            headers[header] = value
            if header == 'Content-Length:':
                content_length = int(value)
            if header == 'Transfer-Encoding:' and value == 'chunked':
                chunked = True
        
        # Append injected headers
        if _headers:
            for header,value in _headers:
                headers[header] = value
            
        # Request body
        if chunked:
            lines = []
            while True:
                line = await sr.readline()
                if not line or not line.strip():
                    break
                lines.append(line.decode())
            body = ''.join(lines)
        else:
            body = await sr.readexactly(content_length)
            body = body.decode()

        # rebuild request message
        with StringIO() as req:
            req.write(start_line)
            req.writelines(' '.join([key,headers[key],'\r\n']) for key in headers.keys())
            req.write('\r\n')
            if body:
                req.write(body)
            return req.getvalue()

def write_log(log: str, verbosity=0) -> None:
    if _verbosity > verbosity:
        print(log)

async def handle_request(req_reader: StreamReader,req_writer: StreamWriter) -> None:
        write_log("Connection recieved...",2)
        req_url, request = await get_proxy_request(req_reader)
        
        # Connect to intended resource
        write_log(f"Connecting to {req_url.netloc}...",2)
        resp_reader, resp_writer = await open_connection(req_url.hostname,req_url.port)

        # Send data
        resp_writer.write(request.encode())
        write_log(f"========> [{datetime.now()}] {req_url.netloc}")
        write_log(request,1)
        await resp_writer.drain()

        response = await get_response(resp_reader)
        req_writer.write(response.encode())
        write_log(f"<======== [{datetime.now()}] {req_url.netloc}")
        write_log(response,1)
        await req_writer.drain()
        req_writer.close()
        await req_writer.wait_closed()
        write_log("End Connection",2)

async def main(args) -> None:
    # Parse arguments
    port = args.port
    global _headers
    _headers = args.header
    global _verbosity 
    _verbosity = args.verbosity
    
    # Start listener
    listener = await start_server(handle_request,'127.0.0.1',port)
    print(f"Listening on port {port}...")
    # Start Request Handling
    try:
        async with listener:
            await listener.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        listener.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="An HTTP intercept proxy used to inject request headers.")
    parser.add_argument("-p","--port", type=int, default=9587,
                        help="Port the proxy will listen on.")
    parser.add_argument("-H","--header",nargs='*', action='append',
                        help="Headers to inject. Can be used multiple times to add multiple headers.")
    parser.add_argument("-v","--verbosity",action="count",default=0,
                        help="Increase verbosity.")
    args = parser.parse_args()
    run(main(args))