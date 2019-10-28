import pathlib
import re
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

IGNORE = [
    '.git',
    '.gitattributes',
]


class PDXMod:

    def __init__(self):
        self.root_path = None
        self.zipFiles = []
        self.descriptor = None
        self.modName = None
        self.supportedVersion = None

    def build(self, mod_dir, desc=False, backup=False):
        mod_path = mod_dir / f'{self.modName}.zip'

        if backup and mod_path.exists():
            print(f'{self.modName}.zip already exists in {mod_dir}.')
            mod_path.replace(mod_dir / f'{mod_path.stem}_{datetime.timestamp(datetime.now())}{mod_path.suffix}')

        with ZipFile(mod_path, 'w', ZIP_DEFLATED) as zipFile:
            for file in self.zipFiles:
                file: pathlib.Path
                zipFile.write(file, file.relative_to(self.root_path))

        if desc:
            desc_path = mod_dir / f'{self.modName}.mod'
            with desc_path.open('w') as desc_file:
                desc_file.write(self.descriptor)
                desc_file.write(f'\narchive=mod/{self.modName}.zip')

    def read_from_dir(self, path: pathlib.Path):
        self.descriptor = self.read_descriptor(path)
        self.root_path = path
        self.populate()
        for p in path.glob('**/*'):
            p = pathlib.Path(p)
            if any(i in p.parts for i in IGNORE):
                continue
            if p.suffix == '.zip':
                continue
            self.zipFiles.append(p)

    @staticmethod
    def read_descriptor(path: pathlib.Path):
        descriptor_path = path / 'descriptor.mod'

        if not descriptor_path.exists():
            raise FileNotFoundError

        with descriptor_path.open('r') as file:
            return file.read()

    def populate(self):
        if not self.descriptor:
            raise AttributeError
        name_match = re.search(r'name="(.*)"', self.descriptor)
        version_match = re.search(r'supported_version="(.*)"', self.descriptor)
        self.modName = name_match.group(1) if name_match else None
        self.supportedVersion = version_match.group(1) if version_match else None