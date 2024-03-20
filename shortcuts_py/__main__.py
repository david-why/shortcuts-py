import json
import plistlib
import sys
from argparse import ArgumentParser

from shortcuts_py.utils import download_shortcut, sign_shortcut


def main(argv: list[str]):
    ap = ArgumentParser(prog='shortcuts-py')
    sp = ap.add_subparsers(
        metavar='COMMAND', help='subcommand to execute', dest='command'
    )

    sign = sp.add_parser('sign', help='sign a shortcut')
    sign.add_argument('shortcut', help='path to the shortcut file')
    sign.add_argument('output', help='path to the output file')
    sign.add_argument(
        '-j',
        '--json',
        action='store_true',
        help='whether the shortcut file is in JSON format',
    )

    download = sp.add_parser('download', help='download a shortcut from iCloud')
    download.add_argument('url', help='sharing URL of the shortcut')
    download.add_argument('output', help='path to the output file')
    download.add_argument(
        '-s', '--signed', action='store_true', help='download signed shortcut'
    )

    args = ap.parse_args(argv)

    if args.command == 'sign':
        with open(args.shortcut, 'rb') as f:
            data = f.read()
            if args.json:
                data = plistlib.dumps(json.loads(data), fmt=plistlib.FMT_BINARY)
            signed = sign_shortcut(data)
        with open(args.output, 'wb') as f:
            f.write(signed)

    elif args.command == 'download':
        data = download_shortcut(args.url, signed=args.signed)
        with open(args.output, 'wb') as f:
            f.write(data)


if __name__ == '__main__':
    main(sys.argv[1:])
