import logging
import pathlib
import socket

from tqdm import tqdm

from pdxModTool import config
from pdxModTool.util import get_mod_dir, make_backup


class Client:

    def __init__(self):
        self._local_socket = None
        self.game = None
        self.desc_paths = []

    def connect(self, server_ip, port=None):
        if not port:
            port = config.default_port

        logging.info(f'connecting to server at {server_ip}:{port}')
        self._local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._local_socket.connect((server_ip, port))

        except ConnectionRefusedError:
            logging.info(f'No connection could be made to {server_ip}, {port}')
            return

        self.__make_connection()

    def __make_connection(self):
        header = self.get_header().strip()
        logging.debug(f'received header: {header.strip()}')
        count, self.game = header.split(config.SEPARATOR)

        for i in range(int(count)):
            self.__receive_file()

        self._local_socket.close()

    def __receive_file(self):
        name_header = self.get_header()
        size_header = self.get_header()
        logging.debug(f'received file header: {name_header.strip(), size_header.strip()}')

        path: pathlib.Path = get_mod_dir(self.game) / name_header.strip()
        if path.exists():
            make_backup(path)

        logging.debug(f'download file to {path}')

        progress = tqdm(range(int(size_header)), f"Receiving {name_header}", unit="B", unit_scale=True,
                        unit_divisor=1024)
        size = int(size_header)
        size_received = 0

        with path.open('wb') as inFile:
            for _ in progress:
                buffer_size = config.BUFFER_SIZE if config.BUFFER_SIZE < size - size_received else size - size_received
                # if size_received == size:
                #     break
                bytes_read = self._local_socket.recv(buffer_size)
                if not bytes_read:
                    break
                size_received += len(bytes_read)

                inFile.write(bytes_read)
                progress.update(len(bytes_read))

        if path.suffix == '.mod':
            self.desc_paths.append(f'mod/{path.name}')

    def get_header(self):
        return self._local_socket.recv(config.HEADER_SIZE).decode()
