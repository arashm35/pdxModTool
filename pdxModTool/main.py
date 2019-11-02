import logging
import pathlib
import subprocess
import sys

from pdxModTool import CURRENT_VERSION
from pdxModTool.cli import parser, parser_build, parser_install, parser_send, parser_recv, parser_update
from pdxModTool.client import Client
from pdxModTool.pdxmod import PDXMod
from pdxModTool.server import Server
from pdxModTool.util import get_mod_dir, get_enabled_mod_paths, update_dlc_load
from pdxModTool.version import VERSION_NAME


def build(args):
    output_dir = args.output if args.output else args.path
    mod = PDXMod()
    if args.path.exists:
        mod.read_from_dir(args.path)

    mod.build(output_dir, desc=args.descriptor)


def install(args):
    mod = PDXMod()
    if args.path.exists:
        mod.read_from_dir(args.path)

    mod_dir = get_mod_dir(args.game)
    mod.build(mod_dir, desc=True, backup=args.backup)


def send(args):
    server = Server(args.game, args.ip, args.port)

    for path in get_enabled_mod_paths(args.game):
        server.files.append(path)
    logging.info(f'preparing {len(server.files)} to send')
    server.start()


def recv(args):
    client = Client()
    client.connect(args.server_ip, args.port)
    update_dlc_load(client.game, client.desc_paths)


def update(args):
    venv_path = pathlib.Path(sys.executable)
    uri = f'https://github.com/arashm35/pdxModTool{args.branch}#egg=pdxModTool'
    print(venv_path)
    subprocess.Popen([venv_path.as_posix(), '-m', 'pip', 'install', '-U', '-e', f'git+{uri}'])


def main():
    parser_build.set_defaults(func=build)
    parser_install.set_defaults(func=install)
    parser_send.set_defaults(func=send)
    parser_recv.set_defaults(func=recv)
    parser_update.set_defaults(func=update)

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    if args.version:
        logging.info(f'pdxModTool v{CURRENT_VERSION} "{VERSION_NAME}"')

    try:
        args.func(args)
    except AttributeError:
        if not args.version:
            parser.parse_args(['-h'])


if __name__ == '__main__':
    main()
