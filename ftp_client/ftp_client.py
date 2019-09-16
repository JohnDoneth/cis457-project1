import socket
import sys
import struct


def require_connection():
    print("A connection must be established first. Use the CONNECT <IP> <PORT> command.")


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
            self.sock.send("LIST".encode("utf-8"))
            response = self.sock.recv(1024).decode("utf-8")
            print(f"Files: {response}")

        except BrokenPipeError:
            require_connection()

    def retrieve(self, filename):
        if self.sock is None:
            require_connection()
            return

        try:
            self.sock.send(f"RETRIEVE {filename}".encode("utf-8"))
            raw_length = self.sock.recv(4)
            length = struct.unpack('>I', raw_length)[0]

            buffer = b""
            while len(buffer) != length:
                buffer += self.sock.recv(1024)

            print(buffer.decode("utf-8"))

        except BrokenPipeError:
            require_connection()

    def store(self):
        pass


def main():
    client = FTPClient()

    try:
        for line in sys.stdin:
            line = line.rstrip()
            cmd = line.split()

            if len(cmd) == 0:
                continue

            if cmd[0].upper() == "CONNECT":
                if len(cmd) < 3:
                    print("CONNECT requires 2 parameters: <IP> <PORT>")
                else:
                    client.connect((cmd[1], cmd[2]))

            if cmd[0].upper() == "RETRIEVE":
                if len(cmd) < 2:
                    print("RETRIEVE requires a parameter: <FILENAME>")
                else:
                    client.retrieve(cmd[1])

            if cmd[0].upper() == "LIST":
                client.list()

    except:
        client.disconnect()


if __name__ == '__main__':
    main()
