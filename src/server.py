# Authors: Tomas Diaz-Wahl, Tamanna Zahir, Liam Cristescu, Guy Allgood
# Date: 2023-04-02
# Description: Server accepts connection from N clients, but the logic is only for two client, as per the assignment
# The order of clients is recorded in a list. Once all clients connect, threads are spawned to handle the client
# messages. Threads are needed to handle simultaneous messages. The message times are recorded using time.time
# and the server returns the order in which the clients connected as well as the messages that each client sent.

import socket
import threading
import logging
import time

#55555

DEBUG = False
# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def print_dict(d: dict):
    if DEBUG:
        logging.info('----------- Printing dict {')
        for item in d.items():
            logging.info(item)
        logging.info('} # End printing dict ----------')


class Server:
    # Server constructor
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # client list will get client socket and client IP address for each client
        self.clients = []
        self.client_messages = []
        self.server_socket = None
        self.threads = []
        self.SOCKET_INDEX = 0
        self.ADDRESS_INDEX = 1
        # global semaphore allowing access to protected list of clients
        self.semaphore = threading.Semaphore(1)

    # this method starts the server and opens a TCP connection
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # setsockopt allows for reuse of socket addresses that are not currently in use
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        logging.info(f'Server listening on {self.host}:{self.port}')

    # this method spawns a thread to listen to up to n number of clients
    def listen_for_clients(self, max_clients):
        # accept client connection and create client list in order of connection
        self.accept_client_connections(max_clients)

        self.sync_clients()

        # spawn threads to handle all clients
        for client_counter in range(max_clients):
            # creates concurrent threads spawned for each client
            client_thread = threading.Thread(target=self.handle_client, args=(client_counter,))
            client_thread.start()
            # add the threads to the thread list
            self.threads.append(client_thread)

        # wait for all clients to finish
        for thread in self.threads:
            thread.join()

        with self.semaphore:
            for i, d in enumerate(self.clients):
                print_dict(d)
    # END listen_for_clients

    def accept_client_connections(self, max_clients):
        # gather all the clients before spawing threads
        # let all clients create a connection and join the server
        # self.server_socket.settimeout(300)
        for i in range(max_clients):
            try:
                logging.info("Server about to accept client connection...")
                client_socket, client_address = self.server_socket.accept()
                logging.info(f'Client {client_address} connected')
                # dictionary (similar to hashmap) to hold our client information to pass into each thread
                # the threads will write to the message field using some wizardry
                client_entry = {"socket": client_socket,
                                "address": client_address,
                                "client_id": i,
                                "msg": None,
                                "msg_time": None}
                with self.semaphore:
                    # we append the dictionary to the list
                    # now each entry in the list contains a dictionary with all the client info
                    self.clients.append(client_entry)
            except socket.timeout:
                logging.info(f'Connection timeout. Client {i} failed to connect.')

    def sync_clients(self):
        with self.semaphore:
            for client in self.clients:
                client_socket = client['socket']
                # this message is only for synchronization and ignored
                message = client_socket.recv(1024).decode('utf-8')
                sync_message = str(client['client_id'])
                client_socket.sendall(sync_message.encode('utf-8'))

    def build_response(self):
        with self.semaphore:
            x = self.clients[0]
            y = self.clients[1]

        if x["msg_time"] < y["msg_time"]:
            response_msg = "X: " + x["msg"] + ", Y: " + y["msg"]
        else:
            response_msg = "Y: " + y["msg"] + ", X: " + x["msg"]

        return response_msg

    def respond_to_clients(self):
        response_msg = self.build_response()
        with self.semaphore:
            for client in self.clients:
                client_socket = client["socket"]
                logging.info("Attempting to send response to client...")
                client_socket.sendall(response_msg.encode('utf-8'))
                logging.info(f'sent message to {client_socket}: {response_msg.encode("utf-8")}')

    def handle_client(self, client_id):
        with self.semaphore:
            client = dict(self.clients[client_id])
        print_dict(client)
        client_socket = client["socket"]
        client_address = client["address"]

        message = client_socket.recv(1024).decode('utf-8')
        logging.info(f'Received message from {client_id}: {message}')
        with self.semaphore:
            self.clients[client_id]["msg"] = message
            self.clients[client_id]["msg_time"] = time.time()
        logging.info(f'This message added to client {client_id}: {message}')

    def close_connection(self):
        logging.info("Closing server socket...")
        self.server_socket.close()
        logging.info("Server socket closed")


if __name__ == '__main__':
    server = Server('', 12000)
    server.start_server()
    number_of_clients = 2
    # should return boolean to check if everyone connected
    server.listen_for_clients(number_of_clients)
    if len(server.clients) != number_of_clients:
        logging.info(f'One or more clients failed to establish connection')
        exit(-1)
    server.respond_to_clients()
    server.close_connection()



