# -*- coding: utf-8 -*-
import argparse
import sys


from touha import Touhas
import logging
import random
from argparse import ArgumentParser

from chibi.file import Chibi_path



def _list( args ):
    import pdb
    pdb.set_trace()
    pass



def main():
    parser = argparse.ArgumentParser(
        "tool for backup and restore rasberry pi sd cards" )

    parser.add_argument(
        "-b", "--backup", type=Chibi_path, default='.', dest="backup_path",
        help="backup path" )

    sub_parsers = parser.add_subparsers( dest='command',
        help='sub-command help' )
    parser_list = sub_parsers.add_parser( 'list', help='list the backups', )

    args = parser.parse_args()

    if args.command == 'list':
        _list( args )

    import pdb
    pdb.set_trace()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
