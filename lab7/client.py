from rdt import Socket
import time
def main():
    client = Socket()
    client.start_sender()
    client.start_receiver()
        # DATA = (input(''))
    with open("alice.txt") as f:
        for line in f:
            client.sendto(line, ('127.0.0.1', 8080))
    print("out")
        # DATA =line.rstrip()

        # client.sendto(DATA, ('127.0.0.1', 8080))



if __name__ == '__main__':
    main()