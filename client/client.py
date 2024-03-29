import base64
import json
import os
import socket
import struct


def require_connection():
    print("A connection must be established first. Use the CONNECT <IP> <PORT> command.")


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


def column_print(columns):
    col_width = max(len(word) for row in columns for word in row) + 2  # padding
    for row in columns:
        print("\t" + "".join(word.ljust(col_width) for word in row))


class FTPClient:
    sock = None

    def __init__(self):
        pass

    def connect(self, address):
        if self.sock:
            print("Already connected")
            return
        try:
            self.sock = socket.create_connection(address)
        except Exception as e:
            print(f"Failed to connect: {e}")
            return

        print(f"Successfully connected to {address[0]}:{address[1]}")

    def disconnect(self):
        if self.sock:
            try:
                self.quit()
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
            send_json(self.sock, {
                "method": "LIST",
            })

            response = recv_json(self.sock)

            files = response["files"]

            if len(files) == 0:
                print("The server does not contain any files at the moment.")
            else:
                print("Files:")
                column_print(response["files"])

        except BrokenPipeError:
            require_connection()

    def send_file(self, filename):
        if self.sock is None:
            require_connection()
            return

        if not os.path.exists(filename):
            print("Error: No such file exists")
            return

        with open(filename, "rb") as infile:
            contents = infile.read()

            # base64 encode the binary file
            contents = base64.b64encode(contents).decode("utf-8")

            try:
                send_json(self.sock, {
                    "method": "STORE",
                    "filename": filename,
                    "contents": contents,
                })

                print(f"Successfully transferred {len(contents)} bytes to remote as {filename}")

            except BrokenPipeError:
                require_connection()

    def retrieve(self, filename):
        if self.sock is None:
            require_connection()
            return

        send_json(self.sock, {
            "method": "RETRIEVE",
            "filename": filename,
        })

        response = recv_json(self.sock)

        error = response.get("error", None)

        if error:
            print(f"Failed to retrieve {filename}: {error}")
            return

        contents = response["contents"]

        with open(filename, "wb") as outfile:
            # base64 decode from the request body
            contents = base64.b64decode(contents)
            outfile.write(contents)

        print(f"Successfully transferred {len(contents)} bytes from remote into {filename}")


    def delete_file(self, filename):
        if self.sock is None:
            require_connection()
            return

        send_json(self.sock, {
            "method": "DELETE",
            "filename": filename,
        })

        response = recv_json(self.sock)

        error = response.get("error", None)

        if error:
            print(f"Failed to delete {filename}: {error}")
            return

        else:
            print("File deleted")


    def quit(self):
        if self.sock is None:
            return

        send_json(self.sock, {
            "method": "QUIT",
        })


def help():
    print("Please enter a valid command.")
    print("Valid commands are:")
    print("\tCONNECT <IP> <PORT>")
    print("\tRETRIEVE <FILENAME>")
    print("\tSTORE <FILENAME>")
    print("\tDELETE <FILENAME>")
    print("\tLIST")
    print("\tQUIT")


def main():
    client = FTPClient()

    # client.connect(("localhost", "12345"))
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
                    print("RETRIEVE requires a single parameter: <FILENAME>")
                else:
                    client.retrieve(cmd[1])

            elif cmd[0].upper() == "STORE":
                if len(cmd) != 2:
                    print("STORE requires a single parameter: <FILENAME>")
                else:
                    client.send_file(cmd[1])

            elif cmd[0].upper() == "DELETE":
                if len(cmd) != 2:
                    print("DELETE requires a single parameter: <FILENAME>")
                else:
                    client.delete_file(cmd[1])

            elif cmd[0].upper() == "LIST":
                client.list()

            elif cmd[0].upper() == "QUIT":
                client.quit()
                break

            elif cmd[0].upper() == "HELP":
                help()

            else:
                help()


    except KeyboardInterrupt:
        # client.disconnect()
        pass

    client.disconnect()


if __name__ == '__main__':
    main()
