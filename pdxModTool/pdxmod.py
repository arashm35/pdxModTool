import logging

from pdxModTool.handler import PathHandler, BaseHandler, BinHandler
from pdxModTool.util import make_backup


class PDXMod:
    HANDLER = {
        lambda x: x.is_dir(): PathHandler,
        lambda x: x.suffix == '.bin': BinHandler
    }

    def __init__(self, src_path):
        self.path = src_path
        self.handler = None

        self.name = None
        self.descriptor = None
        self.data = []

    def __enter__(self):
        for condition, handler in self.HANDLER:
            if condition(self.path):
                self.handler = handler(self.path)

        self.descriptor = self.handler.get_descriptor()
        self.name = self.handler.get_name(self.descriptor)
        self.data = self.handler.get_data()

    def build(self, mod_dir, desc=False, backup=False):
        mod_path = mod_dir / f'{self.name}.zip'

        if backup and mod_path.exists():
            make_backup(mod_path)

        logging.info(f'building {self.name} to {mod_path}')
        self.handler.build(mod_path,"" self.data)

        if desc:
            desc_path = mod_dir / f'{self.name}.mod'
            with desc_path.open('w') as desc_file:
                desc_file.write(self.descriptor)
                desc_file.write(f'\narchive="mod/{mod_path.name}"')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.handler.close()
        self.descriptor = None
        self.data = None
