import argparse
import pathlib

parser = argparse.ArgumentParser(
    prog='pdxModTool',
    description='build/install pdx mods'
)

subparsers = parser.add_subparsers(help='sub-command help')

# add sub-parsers
parser_build = subparsers.add_parser(
    'build',
    help='build mod package.'
)
parser_install = subparsers.add_parser(
    'install',
    help='install mod into game mod folder.'
)
parser_send = subparsers.add_parser(
    'send',
    help='send active mods on pdx game to client.'
)
parser_recv = subparsers.add_parser(
    'recv',
    help='receive mods from server.'
)

# build arguments
parser_build.add_argument(
    '-p', '--path',
    action='store',
    default=pathlib.Path().cwd(),
    type=pathlib.Path,
    help='path of mod root folder.',
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

# install arguments
parser_install.add_argument(
    '-p', '--path',
    action='store',
    default=pathlib.Path().cwd(),
    type=pathlib.Path,
    help='path of mod root folder.',
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
    action='store_true',
    help='set flag for backup.'
)

# send arguments
parser_send.add_argument(
    '-i', '-ip',
    metavar='',
    action='store',
    help='set server ip. default="0.0.0.0".'
)
parser_send .add_argument(
    '-p', '--port',
    metavar='',
    action='store',
    type=int,
    help='set server port. default=65432.'
)
parser_send.add_argument(
    'game',
    metavar='',
    choices=['eu4', 'stellaris', 'ir', 'hoi4', 'ck2'],
    action='store',
    help='set pdx game title to send mods for.'
)

# recv arguments
parser_recv.add_argument(
    '-i', '-ip',
    metavar='',
    action='store',
    help='set server ip. default="0.0.0.0".'
)
parser_recv.add_argument(
    '-p', '--port',
    metavar='',
    action='store',
    type=int,
    help='set server port. default=65432.'
)
