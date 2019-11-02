import pathlib

from pdxModTool import config
from pdxModTool.exception import ModFolderNotFound


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
        return modDir / 'mod'
    raise ModFolderNotFound(game)


def make_header(msg):
    return f'{msg:<{config.HEADER_SIZE}}'
