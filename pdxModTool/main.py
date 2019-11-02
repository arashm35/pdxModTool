import logging

from pdxModTool.cli import parser, parser_build, parser_install, parser_send, parser_recv
from pdxModTool.pdxmod import PDXMod
from pdxModTool.server import Server
from pdxModTool.util import get_mod_dir


def build(args):
    output_dir = args.output if args.output else args.path
    mod = PDXMod()
    if args.path.exists:
        mod.read_from_dir(args.path)

    print(f'building {mod.modName} to {output_dir}')
    mod.build(output_dir, desc=args.descriptor)


def install(args):
    mod = PDXMod()
    if args.path.exists:
        mod.read_from_dir(args.path)

    print(f'install {mod.modName} to {args.game} mod folder')
    mod_dir = get_mod_dir(args.game)
    mod.build(mod_dir, desc=True, backup=args.backup)


def send(args):
    print(args)
    server = Server(args.ip, args.port)
    server.start()


def recv(args):
    pass


def main():
    logging.basicConfig(level=logging.INFO)

    parser_build.set_defaults(func=build)
    parser_install.set_defaults(func=install)
    parser_send.set_defaults(func=send)
    parser_recv.set_defaults(func=recv)

    args = parser.parse_args()

    args.func(args)


if __name__ == '__main__':
    main()
