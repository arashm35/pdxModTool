import argparse
import pathlib

parser = argparse.ArgumentParser(
    prog='pdxModTool',
    description='build/install pdx mods'
)
parser.add_argument(
    '-p', '--path',
    action='store',
    default=pathlib.Path().cwd(),
    type=pathlib.Path,
    help='path of mod root folder',
    # required=True,
)

subparsers = parser.add_subparsers(help='sub-command help')

parser_build = subparsers.add_parser(
    'build',
    help='build mod package.'
)
parser_build.add_argument(
    '-o', '--output',
    metavar='',
    action='store',
    type=pathlib.Path,
    help='set output directory for build archive.'
)
parser_build.add_argument(
    '-d', '--descriptor',
    action='store_true',
    help='build with exterior descriptor file.'
)

parser_install = subparsers.add_parser(
    'install',
    help='install mod into game mod folder'
)
parser_install.add_argument(
    'game',
    metavar='',
    choices=['eu4', 'stellaris', 'ir', 'hoi4', 'ck2'],
    action='store',
    help='set pdx game title to install mods for.'
)
parser_install.add_argument(
    '-b', '--backup',
    # metavar='',
    action='store_true',
    help='set pdx game title to install mods for.'
)
