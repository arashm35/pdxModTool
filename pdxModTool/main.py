from pdxModTool.cli import parser, parser_build, parser_install
from pdxModTool.pdxmod import PDXMod
from pdxModTool.util import get_mod_dir


def build(args, mod: PDXMod):
    output_dir = args.output if args.output else args.path
    print(f'building {mod.modName} to {output_dir}')
    mod.build(output_dir, desc=args.descriptor)


def install(args, mod: PDXMod):
    print(f'install {mod.modName} to {args.game} mod folder')
    mod_dir = get_mod_dir(args.game)
    mod.build(mod_dir, desc=True, backup=args.backup)


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
