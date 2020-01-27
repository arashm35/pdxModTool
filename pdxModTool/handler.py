import logging
import pathlib
import re
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Queue
from zipfile import ZipFile, ZipInfo, ZIP_STORED

from tqdm import tqdm


class BaseHandler:

    def __init__(self, path, max_workers=None):
        if not path.exists():
            raise FileNotFoundError

        self.path = path
        self.size = None

        self.queue = Queue(maxsize=20)
        self.max_workers = max_workers if max_workers else 4
        self.threads = []

    def __repr__(self):
        return f'{type(self).__name__}({self.path})'

    def get_name(self, desc):
        if match := re.search(r'name="(.*)"', desc):
            name = match.group(1)
            name = name.lower().replace(' - ', '_')
            name = name.replace(' ', '_')
            name = "".join(c for c in name if c.isalnum() or c in ['.', '_']).rstrip()
            return name
        logging.error(f'name not found in {self.path}')
        raise LookupError

    def build(self, path):

        try:
            write_lock = threading.Lock()

            with ZipFile(path, 'w', ZIP_STORED) as zipFile:
                progress = tqdm(f'packing "{path.name}"', total=self.size, unit='B', unit_scale=True,
                                unit_divisor=1024)
                with ThreadPoolExecutor(max_workers=self.max_workers) as e:
                    for zipInfo in self.infolist:
                        self.threads.append(e.submit(self.write, write_lock, zipFile, progress))
                        self.threads.append(e.submit(self.read, zipInfo))

                while True:
                    if all(t.done for t in self.threads):
                        break

        except FileNotFoundError as e:
            logging.error(f'{e}: invalid write path: {path}')
        except PermissionError as e:
            logging.error(f'writing and reading on same path: {path}')
        finally:
            progress.close()

    def read(self, zip_info):
        bytes_read = self._read(zip_info)
        self.queue.put((zip_info, bytes_read))

    def write(self, lock, zip_file, progress):
        zip_info, bytes_data = self.queue.get()
        with lock:
            zip_file.writestr(zip_info, bytes_data, compress_type=ZIP_STORED)
        progress.update(zip_info.file_size)

    def get_descriptor(self):
        raise NotImplementedError

    def get_size(self):
        raise NotImplementedError

    @property
    def infolist(self):
        raise NotImplementedError

    def _read(self, zip_info):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class PathHandler(BaseHandler):
    IGNORE = {'.git', '.gitattributes'}

    def __init__(self, path, max_workers=None):
        super(PathHandler, self).__init__(path, max_workers)
        self.src_paths = self.get_paths()
        self.size = self.get_size()

    def get_paths(self):
        paths = list(pathlib.Path(p) for p in self.path.glob('**/*'))
        paths = list(filter(lambda x: not any(i in x.parts for i in self.IGNORE), paths))
        paths = list(filter(lambda x: x.suffix != '.zip', paths))
        paths = list(filter(lambda x: not x.is_dir(), paths))
        return paths

    def get_descriptor(self):
        desc_path = self.path / 'descriptor.mod'

        if not desc_path.exists():
            logging.error(f'no descriptor.mod found in {desc_path}')
            raise FileNotFoundError

        with desc_path.open('r') as desc_file:
            return desc_file.read()

    def get_size(self):
        return sum(map(lambda x: x.stat().st_size, self.src_paths))

    @property
    def infolist(self):
        for path in self.src_paths:
            zip_info = ZipInfo.from_file(path, arcname=path.relative_to(self.path))
            zip_info.orig_filename = path
            yield zip_info

    def _read(self, zip_info):
        path: pathlib.Path = zip_info.orig_filename
        with path.open('rb') as file:
            return file.read()

    def close(self):
        self.src_paths = None
        return


class BinHandler(BaseHandler):

    def __init__(self, path, max_workers=None):
        super(BinHandler, self).__init__(path, max_workers)
        self.binFile = ZipFile(path, 'r')
        self.size = self.get_size()

    def get_descriptor(self):
        desc = ''
        for line in self.binFile.read('descriptor.mod').decode().splitlines():
            if not line.startswith('archive='):
                desc += f'{line}\n'
        return desc

    def get_size(self):
        return sum(map(lambda x: x.file_size, self.binFile.infolist()))

    @property
    def infolist(self):
        for zip_info in self.binFile.filelist:
            yield zip_info

    def _read(self, zip_info):
        return self.binFile.read(zip_info)

    def close(self):
        self.binFile.close()
        self.binFile = None
        return
