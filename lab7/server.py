from rdt import Socket
import time



def main():
    server = Socket(syn=1)
    server.bind(('127.0.0.1', 8080))
    while True:
        data, addr = server.recvfrom()

if __name__ == '__main__':
    main()