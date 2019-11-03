import logging
import pathlib
import subprocess

from pdxModTool import CURRENT_VERSION
from pdxModTool.cli import parser, parser_build, parser_install, parser_send, parser_recv, parser_update, parser_mkLocal
from pdxModTool.client import Client
from pdxModTool.pdxmod import PDXMod
from pdxModTool.server import Server
from pdxModTool.util import get_mod_dir, get_enabled_mod_paths, update_dlc_load, files_from_bin
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
    try:
        subprocess.run(
            [
                'python.exe', '-m', 'pipx', 'upgrade', '--spec',
                f'git+https://github.com/arashm35/pdxModTool{args.branch}#egg=pdxModTool', 'pdxModTool'
            ],
            shell=True
        )
    except subprocess.CalledProcessError:
        return


def mk_local(args):
    # # get all none descriptor files for enabled mods
    # mods = list(filter(lambda x: x.suffix != '.mod', get_enabled_mod_paths(args.game)))
    # # remove all local mods from list
    # mods = list(filter(lambda x: x.parent.name != 'mod', mods))
    # logging.info(f'making local copies for {len(mods)} mods')
    # for path in mods:
    #     print(path)
    #     if path.is_dir():
    #         mod = PDXMod()
    #         mod.read_from_dir(path)
    #         mod.build(get_mod_dir(args.game), desc=True, backup=True)

    mods = get_enabled_mod_paths(args.game, ordered=True)
    mods = list(filter(lambda x: x[1].parent.name != 'mod', mods))
    end_descriptors = list(filter(lambda x: x.suffix == '.mod', get_enabled_mod_paths(args.game)))
    end_descriptors = list(filter(lambda x: x not in [m[0] for m in mods], end_descriptors))
    logging.info(f'making local copies for {len(mods)} mods')
    for item in mods:
        desc_path, src_path = item
        src_path: pathlib.Path
        desc_path: pathlib.Path

        if src_path.is_dir():
            mod = PDXMod()
            mod.read_from_dir(src_path)
            desc_path = mod.build(get_mod_dir(args.game), desc=True, backup=args.backup)

        if src_path.suffix == '.bin':
            mod = PDXMod()
            mod.read_from_bin(src_path)
            desc_path = mod.build(get_mod_dir(args.game), desc=True, backup=args.backup)

        if desc_path:
            end_descriptors.append(desc_path)

    # update_dlc_load(args.game, end_descriptors)


def main():
    parser_build.set_defaults(func=build)
    parser_install.set_defaults(func=install)
    parser_send.set_defaults(func=send)
    parser_recv.set_defaults(func=recv)
    parser_update.set_defaults(func=update)
    parser_mkLocal.set_defaults(func=mk_local)

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
