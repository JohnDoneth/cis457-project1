# import socket programming library
import socket

import json

import struct

# import thread module
from _thread import *
import threading

import os

print_lock = threading.Lock()

def threaded_print(arg: str):
    print_lock.acquire()
    print(arg)
    print_lock.release()


def recv_json(socket):
    raw_length = socket.recv(4)
    length = struct.unpack('>I', raw_length)[0]
    
    body = socket.recv(length)
    body = body.decode("utf-8")
    return json.loads(body)

def send_json(socket, body): 
    
    # encode the data as stringified-json
    encoded = json.dumps(body)
    encoded = encoded.encode("utf-8")

    # get the size of the encoded body
    size = struct.pack('>I', len(encoded))
   
    print(size)

    # write the size
    socket.send(size)

    # write the encoded body
    socket.send(encoded)


# thread function
def threaded(client):
    while True:
        # data received from client
        # data = client.recv(1024)
        #if not data:
        #    threaded_print("a client has disconnected")
        #    break

        request = recv_json(client)

        print(request)

        if not request["method"]:
            print("Invalid Request: missing method field.")
            continue
    
        if request["method"].upper().startswith("LIST"):
            threaded_print("Processing LIST command")

            files = [f for f in os.listdir('.') if os.path.isfile(f)]

            response = {
                "files": files,
            }

            send_json(client, response)

        elif request["method"].upper().startswith("RETRIEVE"):
            threaded_print("Processing RETRIEVE command")

            _, filename = data.split()

            if os.path.exists(filename) == False:
                client.send("file does not exist")
                continue

            with open(filename, "r") as myfile:
                contents = myfile.read()

                encoded = contents.encode("utf-8")

                msg = struct.pack('>I', len(encoded)) + encoded

                client.send(msg)

        elif request["method"].upper().startswith("STORE"):
            threaded_print("Processing STORE command")

            #filename = data.split()[1]
            #header = data.split()[2].encode("utf-8")
            #print(header[:4])
            #len = struct.unpack(">I", header[:4])
            #print(len)

            filename = request["filename"]

            with open(filename, "w") as myfile:
                
                myfile.write(request["contents"])

                #encoded = contents.encode("utf-8")
                #msg = struct.pack('>I', len(encoded)) + encoded
                #client.send(msg)

                # encoded = contents.encode("utf-8")
                # msg = struct.pack('>I', len(encoded)) + encoded
                #c.send(msg)

        elif request["method"].upper().startswith("QUIT"):
            threaded_print("a client has quit")
            break
        else:
            client.send("Invalid command\n".encode("utf-8"))

    c.close()


def main():
    host = ""

    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket bound to port", port)

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    try:
        # a forever loop until client wants to exit
        while True:
            # establish connection with client
            c, addr = s.accept()

            # lock acquired by client
            # print_lock.acquire()
            # print('Connected to :', addr[0], ':', addr[1])

            # Start a new thread and return its identifier
            start_new_thread(threaded, (c,))

    except:
        s.close()


if __name__ == '__main__':
    main()
