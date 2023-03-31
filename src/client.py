import socket
import logging
from time import sleep
from random import randint

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT_NUMBER = 12000


class Client:
    # Client instance constructor
    # self is the current instance
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None

    # create socket and open TCP connection
    # we know it is a TCP connection because we are using SOCK_STREAM constant
    # AF_INET refers to IPV4
    def open_connection(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info("Attempting to connect...")
        self.client_socket.connect((self.host, self.port))
        logging.info("Client connected")

    def close_connection(self):
        socket.close()
        self.client_socket = None

    def send_message(self, message):
        # tests if client_socket connection is open
        if self.client_socket is None:
            logging.info(f'message: {message} not sent. No connection opened')
            return None

        logging.info("Client attempting to send message...")
        self.client_socket.sendall(message.encode('utf-8'))
        logging.info(f'Sent message: {message}')

        response = self.client_socket.recv(1024).decode('utf-8')
        logging.info(f'Received response: {response}')

        # return 0 means all good
        return response


if __name__ == '__main__':
    # define client by IP address and port number and get user input
    client = Client(socket.gethostname(), PORT_NUMBER)
    user_input = input("Enter 1 for 'Hello!' or 2 for 'Howdy!': ")

    # check user input
    if user_input == 1:
        message = "Hello!"
    else:
        message = "Howdy!"

    client.open_connection()
    # wait a random amount of time between 0 and 3 seconds
    sleep(randint(0, 3))
    response = client.send_message(message)
    print(response)
    client.close_connection()

