# import socket programming library
import base64
import json
import os
import socket
import struct
import threading
from _thread import *

print_lock = threading.Lock()


# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def threaded_print(arg: str):
    print_lock.acquire()
    print(arg)
    print_lock.release()


def recv_json(socket):
    raw_length = socket.recv(4)
    length = struct.unpack('>I', raw_length)[0]

    body = bytes()
    while len(body) != length:
        body += socket.recv(length)

    body = body.decode("utf-8")
    return json.loads(body)


def send_json(socket, body):
    # encode the data as stringified-json
    encoded = json.dumps(body)
    encoded = encoded.encode("utf-8")

    # get the size of the encoded body
    size = struct.pack('>I', len(encoded))

    # write the size
    socket.send(size)

    # write the encoded body
    socket.send(encoded)


def send_response(socket, body):
    send_json(socket, body)

    threaded_print("<- Sent Response:")
    threaded_print(json.dumps(body, indent=4, sort_keys=True))


def filter_files(path):
    _, extension = os.path.splitext(path[0])

    if extension == ".py":
        return False
    else:
        return True


# thread function
def threaded(client):
    while True:

        request = recv_json(client)

        if request is None:
            threaded_print("a client has disconnected")
            break

        threaded_print("-> Received Request:")
        threaded_print(json.dumps(request, indent=4, sort_keys=True))

        if not request["method"]:
            print("Invalid Request: missing method field.")
            continue

        if request["method"].upper().startswith("LIST"):
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            file_sizes = [sizeof_fmt(os.path.getsize(f)) for f in os.listdir('.') if os.path.isfile(f)]

            files = list(zip(files, file_sizes))

            files = filter(filter_files, files)

            files = list(files)

            send_response(client, {
                "files": files,
            })

        elif request["method"].upper().startswith("RETRIEVE"):
            filename = request["filename"]

            if not os.path.exists(filename):
                send_response(client, {
                    "error": "file does not exist"
                })
                continue

            with open(filename, "rb") as infile:
                contents = infile.read()

                # base64 encode the binary file
                contents = base64.b64encode(contents).decode("utf-8")

                send_response(client, {
                    "filename": filename,
                    "contents": contents
                })

        elif request["method"].upper().startswith("STORE"):
            filename = request["filename"]

            with open(filename, "wb") as outfile:
                # base64 decode from the request body
                contents = base64.b64decode(request["contents"])
                outfile.write(contents)

            threaded_print("-> Store Complete")

        elif request["method"].upper().startswith("QUIT"):
            threaded_print("-> Client disconnected via QUIT")
            break

        elif request["method"].upper().startswith("DELETE"):
            
            filename = request["filename"]

            if not os.path.exists(filename):
                send_response(client, {
                    "error": "file does not exist"
                })
            else:
                os.remove(filename)
                send_response(client, {
                    "success": "file removed"
                })

        else:
            send_response(client, {
                "error": "Unsupported command"
            })

    client.close()


def main():
    host = ""

    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("FTP Server bound to port", port)

    # put the socket into listening mode
    s.listen(5)
    print("FTP Server is listening for connections")

    try:
        # a forever loop until client wants to exit
        while True:
            # establish connection with client
            c, addr = s.accept()

            # lock acquired by client
            # print_lock.acquire()
            threaded_print(f"Client connected from {addr[0]}:{addr[1]}")

            # Start a new thread and return its identifier
            start_new_thread(threaded, (c,))

    except:
        s.close()


if __name__ == '__main__':
    main()
