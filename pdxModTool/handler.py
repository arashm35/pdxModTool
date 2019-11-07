import logging
import pathlib
import re
from zipfile import ZipFile, ZIP_DEFLATED

from tqdm import tqdm


class BaseHandler:

    def __init__(self, path):
        if not path.exists():
            raise FileNotFoundError

        self.path = path
        self.size = None

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
        progress = tqdm(f'packing "{path.name}"', total=self.size, unit='B', unit_scale=True,
                        unit_divisor=1024)
        try:
            with ZipFile(path, 'w', ZIP_DEFLATED) as zipFile:
                for info, bytes_data in self.data:
                    if type(info) == pathlib.WindowsPath:
                        info = info.as_posix()
                    # logging.debug(f'writing {len(bytes_data) / 1000}kb as {zip_info}')
                    zipFile.writestr(info, bytes_data)
                    progress.update(len(bytes_data))
        except FileNotFoundError as e:
            logging.error(f'{e}: invalid write path: {path}')
        except PermissionError as e:
            logging.error(f'writing and reading on same path: {path}')
        finally:
            progress.close()

    def get_descriptor(self):
        raise NotImplementedError

    def get_size(self):
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class PathHandler(BaseHandler):
    IGNORE = {'.git', '.gitattributes'}

    def __init__(self, path):
        super(PathHandler, self).__init__(path)
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
    def data(self):
        for path in self.src_paths:
            with path.open('rb') as file:
                yield path.relative_to(self.path), file.read()

    def close(self):
        self.src_paths = None
        return


class BinHandler(BaseHandler):

    def __init__(self, path):
        super(BinHandler, self).__init__(path)
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
    def data(self):
        for zip_info in self.binFile.filelist:
            yield zip_info, self.binFile.read(zip_info)

    def close(self):
        self.binFile.close()
        self.binFile = None
        return
