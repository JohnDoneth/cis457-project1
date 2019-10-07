import socket
import sys
import struct
import json


def require_connection():
    print("A connection must be established first. Use the CONNECT <IP> <PORT> command.")


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

    # write the size
    socket.send(size)

    # write the encoded body
    socket.send(encoded)


class FTPClient:
    sock = None

    def __init__(self):
        pass

    def connect(self, address):

        try:
            self.sock = socket.create_connection(address)
        except Exception as e:
            print(f"Failed to connect: {e}")
            return

        print(f"Successfully connected to {address[0]}:{address[1]}")

    def disconnect(self):
        if self.sock is None:
            require_connection()
            return

        try:
            self.sock.send("QUIT".encode("utf-8"))
        except BrokenPipeError:
            # Ignore the exception saying the socket is already closed if it is.
            # We just want to make sure.
            pass
        finally:
            self.sock.close()

    def list(self):
        if self.sock is None:
            require_connection()
            return

        try:
            msg = {
                "method": "LIST",
            }

            send_json(self.sock, msg)

            response = recv_json(self.sock)

            print("Files:")
            for filename in response["files"]:
                print(filename)

        except BrokenPipeError:
            require_connection()

    def send_file(self, filename):
        if self.sock is None:
            require_connection()
            return

        try:
            with open(filename, "r") as myfile:
                contents = myfile.read()

                msg = {
                    "method": "STORE",
                    "filename": filename,
                    "contents": contents,
                }

                try:
                    send_json(self.sock, msg)

                except BrokenPipeError:
                    require_connection()
        except FileNotFoundError:
            print("Error: No such file exists")

    def retrieve(self, filename):
        if self.sock is None:
            require_connection()
            return

        try:

            msg = {
                "method": "RETRIEVE",
                "filename": filename,
            }

            send_json(self.sock, msg)

            response = recv_json(self.sock)

            error = response["error"]

            if error:
                print(f"Failed to retrieve {filename}: {error}")
                return

            print(response["contents"])

        except BrokenPipeError:
            require_connection()

    def quit(self):
        send_json(self.sock, {
            "method": "QUIT",
        })

    def store(self):
        pass


def main():
    client = FTPClient()

    client.connect(("localhost", "12345"))
    # client.send_file("testfile.txt")

    try:
        while True:
            line = input("> ")
            line = line.rstrip()
            cmd = line.split()

            if len(cmd) == 0:
                continue

            if cmd[0].upper() == "CONNECT":
                if len(cmd) != 3:
                    print("CONNECT requires 2 parameters: <IP> <PORT>")
                else:
                    client.connect((cmd[1], cmd[2]))

            elif cmd[0].upper() == "RETRIEVE":
                if len(cmd) != 2:
                    print("RETRIEVE requires a parameter: <FILENAME>")
                else:
                    client.retrieve(cmd[1])

            elif cmd[0].upper() == "STORE":
                if len(cmd) != 2:
                    print("STORE requires a parameter: <FILENAME>")
                else:
                    client.send_file(cmd[1])

            elif cmd[0].upper() == "LIST":
                client.list()

            elif cmd[0].upper() == "QUIT":
                client.quit()
                break

            else:
                print("Please enter a valid command.")
                print("Valid commands are:")
                print("\tCONNECT <IP> <PORT>")
                print("\tRETRIEVE <FILENAME>")
                print("\tSTORE <FILENAME>")
                print("\tLIST")
                print("\tQUIT")

    except KeyboardInterrupt:
        # client.disconnect()
        pass

    client.disconnect()


if __name__ == '__main__':
    main()
