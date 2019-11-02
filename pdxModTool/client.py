import logging
import pathlib
import socket

from tqdm import tqdm

from pdxModTool import config


class Client:

    def __init__(self):
        self._local_socket = None

    def connect(self, server_ip, port):
        logging.info(f'connecting to server at {server_ip}:{port}')
        self._local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._local_socket.connect((server_ip, port))

        except ConnectionRefusedError:
            logging.info(f'No connection could be made to {server_ip}, {port}')
            return

        self.make_connection()

    def make_connection(self):
        header = self._local_socket.recv(config.HEADER_SIZE).decode()
        logging.debug(f'received header: {header}')

        for i in range(int(header)):
            self.receive_file()

    def receive_file(self):
        name_header = self._local_socket.recv(config.HEADER_SIZE).decode()
        size_header = self._local_socket.recv(config.HEADER_SIZE).decode()
        logging.debug(f'received file header: {name_header, size_header}')

        path = pathlib.Path(f'in/{name_header}')
        progress = tqdm(range(int(size_header)), f"Receiving {name_header}", unit="B", unit_scale=True,
                        unit_divisor=1024)
        size = int(size_header)
        size_received = 0

        with path.open('wb') as inFile:
            for _ in progress:
                buffer_size = config.BUFFER_SIZE if config.BUFFER_SIZE < size - size_received else size - size_received
                bytes_read = self._local_socket.recv(buffer_size)
                size_received += len(bytes_read)
                if not bytes_read:
                    break
                inFile.write(bytes_read)
                progress.update(len(bytes_read))