import pathlib
import re
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

from pdxModTool.cli import parser, parser_build, parser_install

IGNORE = [
    '.git',
    '.gitattributes',
]


class ModFolderNotFound(Exception):

    def __init__(self, game):
        print(f'mod folder not found for <{game}> game.')


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


class Config:

    def __init__(self):
        self.game = None


def build(args, mod: PDXMod):
    output_dir = args.output if args.output else args.path

    print(f'building {mod.modName} to {output_dir}')
    mod.build(output_dir, desc=args.descriptor)


def get_doc_dir():
    if (docDir := pathlib.Path().home() / 'OneDrive/Documents').exists():
        return docDir
    else:
        return pathlib.Path().home() / 'Documents'


def get_mod_dir(game):
    pdx_dir = get_doc_dir() / 'Paradox Interactive'
    pdx_dict = {
        'eu4': 'Europa Universalis IV',
        'ir': 'Imperator',
        'hoi4': 'Hearts of Iron IV',
        'stellaris': 'Stellaris'
    }
    if (modDir := pdx_dir / pdx_dict.get(game)).exists():
        return modDir
    raise ModFolderNotFound(game)


def install(args, mod: PDXMod):
    print(f'install {mod.modName} to {args.game} mod folder')
    mod_dir = get_mod_dir(args.game) / 'mod'
    mod.build(mod_dir, desc=True, backup=args.backup)


def main():
    parser_build.set_defaults(func=build)
    parser_install.set_defaults(func=install)

    mod = PDXMod()
    args = parser.parse_args()

    if args.path.exists():
        mod.read_from_dir(args.path)

    args.func(args, mod)


if __name__ == '__main__':
    main()
