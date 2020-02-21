import os
import argparse
import sys
import datetime


from touha import Touhas
import logging
import random
from argparse import ArgumentParser

from chibi.file import Chibi_path
from chibi.file.temp import Chibi_temp_path
from chibi_command.disk.dd import DD
from chibi_command.disk.mount import Mount, Umount

logger_formarter = '%(levelname)s %(name)s %(asctime)s %(message)s'
logger = logging.getLogger( 'touhas.cli' )


def get_touhas( args ):
    backups = args.backup_path + 'touhas'
    if backups.exists:
        backups.mkdir()
    touhas = Touhas( backups )
    return touhas


def find_hostname_on_block( block, mnt ):
    parts = block.dir_name.find( f'{block.base_name}.+' )
    try:
        for block in  parts:
            hostname = find_hostname_on_part( block, mnt )
            if hostname:
                return hostname
    except PermissionError as e:
        logger.warning( str( e ) )


def find_hostname_on_part( block, mnt ):
    logger.info( f"revisando si {block} es root" )
    if not mnt.exists:
        mnt.mkdir()
    if os.path.ismount( str( mnt ) ):
        umount = Umount()( mnt )
        logger.info( str( umount ) )

    result = Mount()( block, mnt )
    if not result:
        raise PermissionError( result.error )

    hostname = mnt + 'etc' + 'hostname'
    if hostname.exists:
        hostname = hostname.open().read().strip()
        hostname = hostname.replace( '-', '_' )
        return hostname

    logger.info( str( Umount()( mnt ) ) )


def _list( args ):
    touhas = get_touhas( args )
    for touha in touhas:
        print( touha )
        print_backups( touhas[ touhas ] )


def print_backups( touha ):
    backups = sorted(
        touha.backups, key=lambda b: b.date, reverse=True )
    for i, backup in enumerate( backups ):
        print( '\t', f"{i}.-", backup.path.file_name )


def _backup( args ):
    touhas = get_touhas( args )
    parts = args.block.dir_name.find( f'{args.block.base_name}.+' )
    try:
        for block in  parts:
            hostname = find_hostname_on_part(
                block, args.backup_path + 'mnt' )
            if hostname:
                logger.info( f"se encontro la touha {hostname}" )
                touha = touhas[ hostname ]
                touha.new_backup( args.block,  )
                break
    except PermissionError as e:
        logger.warning( str( e ) )


def _restore( args ):
    touhas = get_touhas( args )
    block = args.block
    args.date = datetime.datetime.strptime( args.date, "%Y-%m-%d" )
    if args.touha:
        touha_name = args.touha
    else:
        touha_name = find_hostname_on_block(
            block, args.backup_path + 'mnt' )
    try:
        touha = touhas[ touha_name ]
    except KeyError as e:
        print( f"no se encontro la touha {e}" )
        return

    backup = False
    for backup in touha.backups:
        if backup.date == args.date:
            break
        else:
            backup = False
    if not backup:
        print( f"no se encontro un backup de la fecha f{args.date}" )
        print( f"backups validos para f{touha.name}"  )
        print_backups( touha )
        return

    logger.info(
        f"iniciando restauracion del backup {backup.path} en {block}" )
    try:
        backup.restore( block )
    except PermissionError as e:
        logger.warning( str( e ) )


def main():
    parser = argparse.ArgumentParser(
        "tool for backup and restore rasberry pi sd cards" )
    parser.add_argument(
        "--log_level", dest="log_level", default="INFO",
        help="nivel de log", )

    parser.add_argument(
        "-b", "--backup", type=Chibi_path, default='.', dest="backup_path",
        help="backup path" )

    sub_parsers = parser.add_subparsers(
        dest='command', help='sub-command help' )

    parser_list = sub_parsers.add_parser( 'list', help='list the backups', )

    parser_backup = sub_parsers.add_parser( 'backup', help='do a backup', )
    parser_backup.add_argument(
        '--block', '-b', required=True, type=Chibi_path, help='block' )

    parser_restore = sub_parsers.add_parser( 'restore', help='do a restore', )
    parser_restore.add_argument(
        '--block', '-b', required=True, type=Chibi_path, help='block' )
    parser_restore.add_argument(
        '--touha', '-t', required=False, type=Chibi_path, help='touha' )

    parser_restore.add_argument(
        '--date', '-d', required=True, help='date' )

    args = parser.parse_args()

    logging.basicConfig( level=args.log_level, format=logger_formarter )

    if args.command == 'list':
        _list( args )
    elif args.command == 'backup':
        _backup( args )
    elif args.command == 'restore':
        _restore( args )
    else:
        logger.error( f"commando no encontrado {args.command}" )

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
