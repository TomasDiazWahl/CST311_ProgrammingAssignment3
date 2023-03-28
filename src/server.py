import socket
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        logging.info(f'Server listening on {self.host}:{self.port}')

        while len(self.clients) < 2:
            client_socket, client_address = server_socket.accept()
            logging.info(f'Client {client_address} connected')
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        identifier = 'X' if len(self.clients) == 0 else 'Y'
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
    server.start()
