import json
import pathlib
import re

from pdxModTool import config
from pdxModTool.exceptions import ModFolderNotFound


def make_backup(path):
    pass

def get_doc_dir():
    if (docDir := pathlib.Path().home() / 'OneDrive/Documents').exists():
        return docDir
    else:
        return pathlib.Path().home() / 'Documents'


def get_game_dir(game):
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


def get_mod_dir(game):
    return get_game_dir(game) / 'mod'


def update_dlc_load(game, desc_paths):
    dlc_load_path = get_game_dir(game) / 'dlc_load.json'
    with dlc_load_path.open('r') as json_file:
        dlc_load = json.load(json_file)

    dlc_load['enabled_mods'] = desc_paths

    with dlc_load_path.open('w') as json_file:
        json.dump(dlc_load, json_file)


def get_enabled_mods_desc(game):
    dlc_load_path = get_game_dir(game) / 'dlc_load.json'
    with dlc_load_path.open('r') as json_file:
        dlc_load = json.load(json_file)
        return dlc_load['enabled_mods']


def get_mod_path(game, desc_path: pathlib.Path):
    def resolve_path(match):
        if len(match.split('/')) == 2:
            return get_game_dir(game) / match
        else:
            return pathlib.Path(match)

    with desc_path.open('r') as desc_file:
        desc = desc_file.read()

        if archive_match := re.search(r'archive="(.*)"', desc).group(1):
            return resolve_path(archive_match)

        if path_match := re.search(r'path="(.*)"', desc).group(1):
            return resolve_path(path_match)

    raise FileNotFoundError


def get_enabled_mod_paths(game):
    enabled_mods_desc = get_enabled_mods_desc(game)
    game_dir = get_game_dir(game)
    paths = []

    for mod in enabled_mods_desc:
        desc_path = game_dir / mod
        try:
            mod_path = get_mod_path(game, desc_path)
        except FileNotFoundError:
            continue
        paths.append(desc_path)
        paths.append(mod_path)

    return paths


def make_header(*args):
    msg = f'{config.SEPARATOR}'.join(list(map(str, args)))
    return f'{msg:<{config.HEADER_SIZE}}'.encode()
