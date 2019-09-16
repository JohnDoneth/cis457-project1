# import socket programming library
import socket

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


# thread fuction
def threaded(c):
    while True:
        # data received from client
        data = c.recv(1024)
        if not data:
            threaded_print("a client has disconnected")
            break

        data = data.decode('utf-8')
        print(data)

        if data.upper().startswith("LIST"):

            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            response = ", ".join(files)
            response += "\n"

            c.send(response.encode('utf-8'))

        elif data.upper().startswith("RETRIEVE"):
            # threaded_print(data)

            _, filename = data.split()

            with open(filename, "r") as myfile:
                contents = myfile.read()

                encoded = contents.encode("utf-8")

                msg = struct.pack('>I', len(encoded)) + encoded

                c.send(msg)

        elif data.upper().startswith("QUIT"):
            threaded_print("a client has quit")
            break
        else:
            c.send("Invalid command\n".encode("utf-8"))

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
