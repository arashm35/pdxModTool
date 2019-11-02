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
parser_update = subparsers.add_parser(
    'update',
    help='update to latest version of pdxModTool from github.'
)
# version argument for main parser
parser.add_argument(
    '-v', '--version',
    action='store_true',
    help='show version'
)
parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help='enable debug mode'
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
    metavar='game',
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
    'game',
    metavar='game',
    choices=['eu4', 'stellaris', 'ir', 'hoi4', 'ck2'],
    action='store',
    help='set pdx game title to send mods for.'
)
parser_send.add_argument(
    '-i', '--ip',
    metavar='',
    action='store',
    help='set server ip. default="0.0.0.0".'
)
parser_send.add_argument(
    '-p', '--port',
    metavar='',
    action='store',
    type=int,
    help='set server port. default=65432.'
)

# recv arguments
parser_recv.add_argument(
    'server_ip',
    metavar='server_ip',
    action='store',
    help='set target server ip. '
)
parser_recv.add_argument(
    '-p', '--port',
    metavar='',
    action='store',
    type=int,
    help='set server port. default=65432.'
)

# update arguments
parser_update.add_argument(
    '-b', '--branch',
    metavar='',
    action='store',
    default='',
    type=str,
    help='set branch. e.g. "@branch-name"'
)
