import logging
import pathlib
import socket
# import threading

from tqdm import tqdm

from pdxModTool import config
from pdxModTool.util import make_header


class Server:
    # LOCK = threading.Lock()

    def __init__(self, game, host_ip=None, port=None):
        self._local_socket: socket.socket = None
        self._host_ip = host_ip if host_ip else config.localHost
        self._port = port if port else config.default_port
        self._game = game

        self._connections = []
        self.files = []

    @property
    def address(self):
        return self._host_ip, self._port

    def close(self):
        self._local_socket.close()

    def start(self):
        logging.info(f'listening on {self._host_ip}:{self._port}')
        self._local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._local_socket.bind(self.address)
        self._local_socket.listen()

        while True:
            try:
                client_socket, client_addr = self._local_socket.accept()
                self.handle(client_socket, client_addr)
                # conn = threading.Thread(target=self.handle, args=(client_socket, client_addr,))
                # conn.daemon = True
                # conn.start()
            except KeyboardInterrupt:
                logging.info('KeyboardInterrupt: server terminating')
            finally:
                self.close()
                break

    def handle(self, client_socket: socket.socket, addr):
        logging.info(f'client connected from {addr}')
        # self.LOCK.acquire()
        try:
            self.make_connection(client_socket)
            for path in self.files:
                self.send_file(client_socket, path)
        finally:
            # self.LOCK.release()
            client_socket.close()

    def make_connection(self, client_socket):
        header = make_header(len(self.files), self._game)
        logging.debug(f'send header: {header}')
        client_socket.sendall(header)

    @staticmethod
    def send_file(client_socket, path: pathlib.Path):
        name_header = make_header(path.name)
        size_header = make_header(path.lstat().st_size)
        logging.debug(f'send file header: {name_header, size_header}')
        client_socket.sendall(name_header + size_header)  # TODO: potential fuck up, separate

        progress = tqdm(range(int(size_header)), f"Sending {path.name}", unit='B', unit_scale=True,
                        unit_divisor=1024)
        # size = int(size_header)
        # size_sent = 0
        with path.open('rb') as outFile:
            for _ in progress:
                # buffer_size = config.BUFFER_SIZE if config.BUFFER_SIZE < size - size_sent else size - size_sent
                # if size_sent == size:
                #     break
                bytes_read = outFile.read(config.BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)
                progress.update(len(bytes_read))
