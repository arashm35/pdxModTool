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

    def __repr__(self):
        return f'{type(self).__name__}({self.path})'

    def get_descriptor(self):
        raise NotImplementedError

    def get_name(self, desc):
        if match := re.search(r'name="(.*)"', desc):
            return match.group(1)
        logging.error(f'name not found in {self.path}')
        raise LookupError

    def get_data(self):
        raise NotImplementedError

    @staticmethod
    def build(mod_path, data):
        progress = tqdm(f'packing "{mod_path.name}"', total=sum(map(lambda x: len(x[1]), data)), unit='B',
                        unit_scale=True, unit_divisor=1024)

        with ZipFile(mod_path, 'w', ZIP_DEFLATED) as zipFile:
            for zip_info, bytes_data in data:
                if type(zip_info) == pathlib.WindowsPath:
                    zip_info = zip_info.as_posix()
                # logging.debug(f'writing {len(bytes_data) / 1000}kb as {zip_info}')
                zipFile.writestr(zip_info, bytes_data)
                progress.update(len(bytes_data))
            progress.close()

    def close(self):
        raise NotImplementedError


class PathHandler(BaseHandler):
    IGNORE = {'.git', '.gitattributes'}

    def get_descriptor(self):
        desc_path = self.path / 'descriptor.mod'

        if not desc_path.exists():
            logging.error(f'no descriptor.mod found in {desc_path}')
            raise FileNotFoundError

        with desc_path.open('r') as desc_file:
            return desc_file.read()

    def get_data(self):
        paths = list(pathlib.Path(p) for p in self.path.glob('**/*'))
        paths = list(filter(lambda x: not any(i in x.parts for i in self.IGNORE), paths))
        paths = list(filter(lambda x: x.suffix != '.zip', paths))
        paths = list(filter(lambda x: not x.is_dir(), paths))
        data = []
        for path in paths:
            with path.open('rb') as file:
                data.append((path.relative_to(self.path), file.read()))
        return data

    def close(self):
        return


class BinHandler(BaseHandler):

    def __init__(self, path):
        super(BinHandler, self).__init__(path)
        self.binFile = ZipFile(path, 'r')

    def get_descriptor(self):
        desc = ''
        for line in self.binFile.read('descriptor.mod').decode().splitlines():
            if not line.startswith('archive='):
                desc += f'{line}\n'
        return desc

    def get_data(self):
        data = []
        for file in self.binFile.filelist:
            data.append((file, self.binFile.read(file)))
        return data

    def close(self):
        self.binFile.close()
        self.binFile = None
        return
