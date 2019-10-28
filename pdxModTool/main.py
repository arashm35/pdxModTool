import pathlib
import re
from zipfile import ZipFile, ZIP_DEFLATED

from pdxModTool.cli import parser, parser_build, parser_install

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

    def build(self, path, desc=False):
        with ZipFile(path, 'w', ZIP_DEFLATED) as zipFile:
            for file in self.zipFiles:
                file: pathlib.Path
                zipFile.write(file, file.relative_to(self.root_path))

        if desc:
            desc_path = path.parent / f'{self.modName}.mod'
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
    output_path = args.output if args.output else args.path
    output_path = output_path / f'{mod.modName}.zip'

    print(f'building {mod.modName} to {output_path}')
    mod.build(output_path, desc=args.descriptor)


def install(args, mod: PDXMod):
    print(f'install {mod.modName} to {args.game} mod folder')
    print(args.path)
    return


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
