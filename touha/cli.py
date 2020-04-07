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
from chibi_requests import Chibi_url
from chibi_command.disk.dd import DD
from chibi_command.disk.mount import Mount, Umount
from chibi_command.disk.format import Ext4, Vfat
from chibi_command.file import Bsdtar

from touha.mount import _mount, _umount
from touha.spell_card import Spell_card

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
        print_backups( touhas[ touha ] )


def print_backups( touha ):
    backups = sorted(
        touha.backups, key=lambda b: b.date, reverse=True )
    for i, backup in enumerate( backups ):
        print( '\t', f"{i}.-", backup.path.file_name )


def _backup( args ):
    touhas = get_touhas( args )
    spell_card = Spell_card( block=args.block, mount_path=args.backup_path, )
    touha = touhas[ spell_card.name ]
    touha.new_backup( args.block )
    return


def _restore( args ):
    touhas = get_touhas( args )
    block = args.block
    args.date = datetime.datetime.strptime( args.date, "%Y-%m-%d" )
    if args.touha:
        touha_name = args.touha
    else:
        spell_card = Spell_card( block=args.block, mount_path=args.backup_path, )
        touha_name = spell_card.name

    try:
        touha = touhas[ touha_name ]
    except KeyError as e:
        logger.info( f"no se encontro la touha {e}" )
        return

    for backup in touha.backups:
        if backup.date == args.date:
            break
    else:
        logger.info( f"no se encontro un backup de la fecha f{args.date}" )
        logger.info( f"backups validos para f{touha.name}"  )
        print_backups( touha )
        return

    logger.info(
        f"iniciando restauracion del backup {backup.path} en {block}" )

    backup.restore( block )


def _format( args ):
    block = args.block
    boot = f"{block}p1"
    root = f"{block}p2"

    Vfat( boot ).run()
    Ext4( root ).run()

    if args.version == "4":
        image_url = Chibi_url(
            'http://os.archlinuxarm.org/os/ArchLinuxARM-rpi-4-latest.tar.gz' )

    else:
        raise NotImplementedError(
            f"la version de rasp {args.version} no esta implementada" )

    image_path = args.backup_path + 'image'
    if not image_path.exists:
        image_path.mkdir()

    image = image_path + image_url.base_name
    if not image.exists:
        image = image_url.download( path=image_path )

    spell_card = Spell_card( block=args.block, mount_path=args.backup_path, )

    Bsdtar( '-xpf', image, '-C', spell_card.root ).run()
    tmp_boot = spell_card.root + 'boot' + '*'
    tmp_boot.move( spell_card.boot )


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

    parser_format = sub_parsers.add_parser( 'format', help='do a format', )
    parser_format.add_argument(
        '--block', '-b', required=True, type=Chibi_path, help='block' )
    parser_format.add_argument(
        '--version', '-v', required=True, help='raspberry pi version' )

    parser_mount = sub_parsers.add_parser( 'mount', help='mount the touha', )
    parser_mount.add_argument(
        '--block', '-b', required=True, type=Chibi_path, help='block' )

    parser_umount = sub_parsers.add_parser( 'umount', help='umount the touha', )


    parser_spell_card = sub_parsers.add_parser(
        'spell_card', help='check the spell card', )
    parser_spell_card.add_argument(
        '--block', '-b', required=True, type=Chibi_path, help='block' )

    spell_card_sub_parser = parser_spell_card.add_subparsers(
        dest='spell_card_command', help='spell_card help' )

    parser_spell_card_print = spell_card_sub_parser.add_parser(
        'list', help='check the spell card', )
    parser_spell_card_print.add_argument(
        '--home', action="store_true", help='decide if is going to print home' )

    parser_spell_card_clone = spell_card_sub_parser.add_parser(
        'backup', help='backup spell card', )
    parser_spell_card_clone.add_argument(
        '--destination', '-d', default='.', type=Chibi_path,
        help='destino' )
    parser_spell_card_clone.add_argument(
        '--home', action="store_true", help='decide if is going to print home' )

    parser_spell_card_restore = spell_card_sub_parser.add_parser(
        'restore', help='backup spell card', )
    parser_spell_card_restore.add_argument(
        '--destination', '-d', default='.', type=Chibi_path,
        help='destino' )
    parser_spell_card_restore.add_argument(
        '--touha', help='nombre de la touha a usar' )

    args = parser.parse_args()

    logging.basicConfig( level=args.log_level, format=logger_formarter )

    if args.command == 'list':
        _list( args )
    elif args.command == 'backup':
        _backup( args )
    elif args.command == 'restore':
        _restore( args )
    elif args.command == 'format':
        _format( args )
    elif args.command == 'mount':
        Spell_card(
            block=args.block, mount_path=args.backup_path,
            unmount_on_dead=False )
    elif args.command == 'umount':
        Spell_card( mount_path=args.backup_path, unmount_on_dead=True )
    elif args.command == 'spell_card':
        spell_card = Spell_card(
            block=args.block, mount_path=args.backup_path,
            unmount_on_dead=True )
        if args.spell_card_command == "list":
            spell_card.check_spell_card( home=args.home )
        if args.spell_card_command == "backup":
            spell_card.clone( path=args.destination, home=args.home, )
        if args.spell_card_command == "restore":
            spell_card.restore( path=args.destination, touha_name=args.touha, )
        else:
            logger.error(
                "spell card commando no encontrado "
                f"{args.spell_card_command}"
            )
    else:
        logger.error( f"commando no encontrado {args.command}" )

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
