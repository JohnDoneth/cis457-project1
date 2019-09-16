# import socket programming library
import socket
import sys


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect

    try:
        for line in sys.stdin:
            line = line.rstrip()
            print(line)

    except:
        s.close()


if __name__ == '__main__':
    main()
