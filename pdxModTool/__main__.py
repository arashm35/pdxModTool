import logging
import pathlib
import subprocess
import sys

from pdxModTool.cli import parser, parser_build, parser_install, parser_send, parser_recv, parser_update, parser_mkLocal
from pdxModTool.client import Client
from pdxModTool.pdxmod import PDXMod
from pdxModTool.server import Server
from pdxModTool.util import get_mod_dir, get_enabled_mod_paths, update_dlc_load
from pdxModTool.version import VERSION_NAME, CURRENT_VERSION


def build(args):
    output_dir = args.output if args.output else args.path
    try:
        with PDXMod(args.path) as mod:
            mod.build(output_dir, desc=args.descriptor)
    except FileNotFoundError as e:
        logging.error(f'{e}: mod source not found: {args.path}')


def install(args):
    output_dir = get_mod_dir(args.game)
    with PDXMod(args.path) as mod:
        mod.build(output_dir, desc=True, backup=args.backup)


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
    uri = f'https://github.com/arashm35/pdxModTool{args.branch}#egg=pdxModTool'
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-U', '-e', f'git+{uri}'])


def mk_local(args):
    mods = get_enabled_mod_paths(args.game, ordered=True)
    mods = list(filter(lambda x: x[1].parent.name != 'mod', mods))
    end_descriptors = list(filter(lambda x: x.suffix == '.mod', get_enabled_mod_paths(args.game)))
    end_descriptors = list(filter(lambda x: x not in [m[0] for m in mods], end_descriptors))
    logging.info(f'making local copies for {len(mods)} mods')
    for desc_path, src_path in mods:
        src_path: pathlib.Path
        desc_path: pathlib.Path
        logging.debug(f'making local of {src_path}, {desc_path}')

        try:
            with PDXMod(src_path) as mod:
                mod.build(get_mod_dir(args.game), desc=True, backup=args.backup)
                desc_path = get_mod_dir(args.game) / f'{mod.name}.mod'
                end_descriptors.append(desc_path)
        except FileNotFoundError:
            logging.error(f'Could not make copy of {src_path}')

    end_descriptors = list(f'{desc.parent.name}/{desc.name}' for desc in end_descriptors)
    if args.dlc_load:
        update_dlc_load(args.game, end_descriptors)


def main():
    parser.set_defaults(func=lambda _: parser.print_help())
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
        return

    # if len(vars(args)) <= 2:
    #     parser.print_help()
    #     return

    try:
        args.func(args)
    except KeyboardInterrupt:
        logging.warning(f'KeyboardInterrupt')
        quit()


if __name__ == '__main__':
    main()
