import os
import argparse
import sys
import datetime
import time


from touha import Touhas
import logging
import random
from argparse import ArgumentParser

from chibi_atlas import Chibi_atlas
from chibi.file import Chibi_path
from chibi.file.temp import Chibi_temp_path
from chibi_requests import Chibi_url
from chibi_command.disk.lsblk import Lsblk
from chibi_command.disk.dd import DD
from chibi_command.disk.mount import Mount, Umount
from chibi_command.disk.format import Ext4, Vfat
from chibi_command.file import Bsdtar

from touha.mount import _mount, _umount
from touha.spell_card import Spell_card
from touha.snippets import get_boot_root, parse_phase_execute_args

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
    spell_card.build_new_backup()
    #touha = touhas[ spell_card.name ]
    #touha.new_backup( args.block )
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
    boot, root = get_boot_root( block )
    #boot = f"{block}p1"
    #root = f"{block}p2"

    if not args.only_install:
        logger.info( f"formateando {boot}" )
        Vfat( boot ).run()
        logger.info( f"formateando {root}" )
        Ext4( root ).run()
        logger.info( "esperando 10 segundos antes de la instalacion" )
        time.sleep( 10 )

    if args.version == "4":
        if args.arch == '64':
            image_url = Chibi_url(
                'http://os.archlinuxarm.org/os/ArchLinuxARM-rpi'
                '-aarch64-latest.tar.gz' )
        else:
            image_url = Chibi_url(
                'http://os.archlinuxarm.org/os/ArchLinuxARM-rpi'
                '-armv7-latest.tar.gz' )
    elif args.version == '3':
        if args.arch == '64':
            image_url = Chibi_url(
                'http://os.archlinuxarm.org/os/'
                'ArchLinuxARM-rpi-aarch64-latest.tar.gz' )
        else:
            image_url = Chibi_url(
                'http://os.archlinuxarm.org/os/ArchLinuxARM'
                '-rpi-armv7-latest.tar.gz' )
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

    Bsdtar( '-v', '-xpf', image, '-C', spell_card.root ).run()
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

    parser_format = sub_parsers.add_parser(
        'format', help='format the devices and install the clean image', )
    parser_format.add_argument(
        '--block', '-b', required=True, type=Chibi_path, help='block' )
    parser_format.add_argument(
        '--version', '-v', required=True, help='raspberry pi version' )
    parser_format.add_argument(
        '--arch', '-a', required=False, help='raspberry pi arch' )
    parser_format.add_argument(
        '--only_install', required=False,
        default=False, action="store_true",
        help='no formaterara las particiones y solo instalara la imagen' )

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

    parser_spell_card_rename = spell_card_sub_parser.add_parser(
        'rename', help='cambia el nomrbe de la spell card o hostname', )
    parser_spell_card_rename.add_argument(
        "new_name",
        help="nuevo nombre de la touha", )

    parser_spell_card_fstab = spell_card_sub_parser.add_parser(
        'phase', help='phases de la spellcard', )

    parser_spell_card_phase_sub_parser = (
        parser_spell_card_fstab.add_subparsers(
            dest='spell_card_phase_command',
            help='subcomando para las fases', )
    )
    parser_spell_card_phase_exe = (
        parser_spell_card_phase_sub_parser.add_parser(
        'execute', help='ejecuta fases del spellcard', )
    )
    parser_spell_card_phase_exe.add_argument(
        "phase", help="nombre de la fase que se ejecutara", )

    parser_spell_card_phase_exe.add_argument(
        "--arg", dest="args", nargs="*", type=parse_phase_execute_args,
        help=(
            "parametros tipo tuplas separados por por un simbolo de ="
            "'ip=200.200.200.1 MASK=24'" ), )

    parser_spell_card_phase_exe.add_argument(
        "--force", dest="force", default=False, action="store_true",
        help="nombre de la fase que se ejecutara", )

    parser_spell_card_phase_status = (
        parser_spell_card_phase_sub_parser.add_parser(
        'status', help='revisa el status de la fase', )
    )
    parser_spell_card_phase_status.add_argument(
        "phase", help="nombre de la fase", )

    parser_spell_card_phase_status.add_argument(
        "--level", default="info",
        help="nivel de impresion del status, info, debug", )


    parser_spell_card_fstab = spell_card_sub_parser.add_parser(
        'fstab', help='lee o cambia el fstab', )

    parser_spell_card_fstab_sub_parser = (
        parser_spell_card_fstab.add_subparsers(
            dest='spell_card_fstab_command', help='agrega bloques al fstab', )
    )
    parser_spell_card_fstab_add = parser_spell_card_fstab_sub_parser.add_parser(
        'add', help='lee o cambia el fstab', )

    parser_spell_card_fstab_add.add_argument(
        "dev_block",
        help="bloque de fs en dev/sd*", )

    parser_blocks = sub_parsers.add_parser( 'blocks', help='print lsblk', )

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
        elif args.spell_card_command == "backup":
            spell_card.clone( path=args.destination, home=args.home, )
        elif args.spell_card_command == "restore":
            spell_card.restore( path=args.destination, touha_name=args.touha, )
        elif args.spell_card_command == "rename":
            spell_card.name = args.new_name
        elif args.spell_card_command == "phase":
            if args.spell_card_phase_command:
                if args.spell_card_phase_command == 'status':
                    spell_card.phases[ args.phase ].full_status(
                        level=args.level )
                if args.spell_card_phase_command == 'execute':
                    if not args.args:
                        phase_args = Chibi_atlas()
                    else:
                        phase_args = Chibi_atlas( dict( args.args ) )
                    if args.phase == 'all':
                        for phase in spell_card.phases.values():
                            phase.run( force=args.force, **phase_args )
                    else:
                        spell_card.phases[ args.phase ].run(
                            force=args.force, **phase_args )
            else:
                spell_card.check_phases()
        elif args.spell_card_command == "fstab":
            if args.spell_card_fstab_command:
                if args.spell_card_fstab_command == 'add':
                    spell_card.add_block_in_fstab( args.dev_block )
                else:
                    logger.error(
                        "spell card commando de fstab no encontrado "
                        f"{args.spell_card_fstab_command}"
                    )

            else:
                spell_card.print_fstab()
        else:
            logger.error(
                "spell card commando no encontrado "
                f"{args.spell_card_command}"
            )
    elif args.command == 'blocks':
        blocks = Lsblk( '-o', '+SIZE', ).run().result
        for name, block in blocks.items():
            print( name )
            if block.childs:
                for c in block.childs:
                    print(
                        f"\t{c.name} {c.fstype} "
                        f"{c.size} "
                        f"{c.uuid} "
                    )
    else:
        logger.error( f"commando no encontrado {args.command}" )

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
