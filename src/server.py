import socket
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Server:
    # Server constructor
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # client list will get client socket and client IP address for each client
        self.clients = []
        self.client_id = 0
        self.server_socket = None

    # this method starts the server and opens a TCP connection
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # setsockopt allows for reuse of socket addresses that are not currently in use
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        logging.info(f'Server listening on {self.host}:{self.port}')

    def listen_for_clients(self, max_clients):
        while len(self.clients) < max_clients:
            client_socket, client_address = self.server_socket.accept()
            logging.info(f'Client {client_address} connected')
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        if len(self.clients) == 0:
            identifier = 'X'
            self.client_id = 0
        elif len(self.clients) == 1:
            identifier = 'Y'
            self.client_id = 1
        else:
            self.client_id += 1
            identifier = self.client_id

        self.clients.append((client_socket, client_address))

        message = client_socket.recv(1024).decode('utf-8')
        logging.info(f'Received message from {identifier}: {message}')

        if len(self.clients) == 2:
            response = f"{identifier}: '{message}', "
            other_identifier = 'Y' if identifier == 'X' else 'X'
            other_socket, _ = self.clients[0] if identifier == 'Y' else self.clients[1]
            other_message = other_socket.recv(1024).decode('utf-8')
            response += f"{other_identifier}: '{other_message}'"
            logging.info(f'Sending response to both clients: {response}')

            for socket, _ in self.clients:
                socket.sendall(response.encode('utf-8'))
                socket.close()


if __name__ == '__main__':
    server = Server()
    server.start_server()
