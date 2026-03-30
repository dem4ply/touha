import logging
from chibi_atlas import Chibi_atlas
from chibi.file import Chibi_path
from chibi.file.other import Chibi_systemd, Chibi_conf_env
from chibi.file.temp import Chibi_temp_path
from chibi_command.disk.mount import Mount, Umount
from chibi_command.rsync import Rsync
from chibi_command.file import Tar
from chibi_command.disk.lsblk import Lsblk
from chibi_fstab import Chibi_fstab

from touha.snippets import get_boot_root, get_backup_date
from touha.phases.wireless_adhoc import Wireless_adhoc
from touha.phases.wireless_common import Wireless_common
from touha.phases.sshd import Sshd


logger = logging.getLogger( 'touhas.spell_card' )

class Spell_card:
    def __init__(
            self, block=None, mount_path=None, unmount_on_dead=True,
            root_path=None, home=None ):
        self._mount_path = mount_path
        self._block = block
        self._home = home
        if block is not None:
            self.mount()
            self._prepare()
        self.unmount_on_dead = unmount_on_dead
        if root_path is None:
            root_path = Chibi_path( '.' ) + 'touhas'
        self.root_path = Chibi_path( root_path )

    @property
    def name( self ):
        try:
            return self._name
        except AttributeError:
            if not self.hostname.exists:
                return "no-name"
            self._name = self.hostname.open().read().replace(
                '-', '_' ).strip()
            return self._name

    @name.setter
    def name( self, value ):
        if not self.hostname.exists:
            raise OSError(
                "No existe el archivo de hostnamae '{self.hostname}'" )
        host = self.hostname.open()
        new_name = value.replace( '_', '-' ).strip()
        host.write( new_name )
        logger.info( f"se cambio el nombre de la touha por {new_name}" )
        # si no tiene le nombre en caache ignora la excepcion
        try:
            del self._name
        except:
            pass

    @property
    def hostname( self ):
        return self.root + 'etc' + 'hostname'

    @property
    def hosts( self ):
        return self.root + 'etc' + 'hosts'

    @property
    def adhoc_service( self ):
        path = self.root + 'etc/systemd/system/network_wireless_adhoc@.service'
        path = Chibi_path( path, chibi_file_class=Chibi_systemd )
        return path

    @property
    def wlan0_adhoc_config( self ):
        path = self.root + 'etc/conf.d/network_wireless_adhoc@wlan0'
        path = Chibi_path( path, chibi_file_class=Chibi_conf_env )
        return path

    @property
    def torrc( self ):
        return self.root + 'etc/tor/torrc'

    @property
    def torrc_sshd( self ):
        return self.root + 'var/lib/tor/sshd'

    @property
    def wpa_supplicant( self ):
        return self.root + 'etc/wpa_supplicant'

    @property
    def sshd_config( self ):
        return self.root + 'etc/ssh/sshd_config'

    @property
    def fstab( self ):
        result = self.root + 'etc/fstab'
        result = Chibi_path( result, chibi_file_class=Chibi_fstab )
        return result

    @property
    def all( self ):
        return (
            self.hostname, self.hosts, self.adhoc_service, self.fstab,
            self.wlan0_adhoc_config, self.torrc, self.torrc_sshd,
            self.wpa_supplicant, self.sshd_config,
        )

    @property
    def home( self ):
        return self.root + 'home'

    @property
    def root_home( self ):
        return self.root + 'root'

    @property
    def phases( self ):
        """
        contrulle el dicionario de phases para la spell card
        """
        phases_list = [
            Wireless_adhoc( self ),
            Wireless_common( self ),
            Sshd( self ),
        ]
        return Chibi_atlas( { p.name: p for p in phases_list } )

    def check_phases( self ):
        """
        imprime el status de la face de la spell card
        """
        for phase in self.phases.values():
            print( f"{phase.name}: {phase.status}" )

    def check_spell_card( self, home=False ):
        for spell in self.all:
            print( spell, spell.exists )
            if spell.is_a_folder:
                if spell.exists:
                    for r_spell in spell.find():
                        print( r_spell, r_spell.exists )
        if home:
            for spell in self.home.find():
                print( spell, spell.exists )
                if spell.is_a_folder:
                    if spell.exists:
                        for r_spell in spell.find():
                            print( r_spell, r_spell.exists )

    def clone( self, path, home=False, clean=True ):
        from touha import Touhas
        path = path + 'touhas'
        touhas = Touhas( path )
        touha = touhas[ self.name ]
        folders = self.all
        if home:
            folders = ( *folders, self.home, self.root_home )
        path = touha.path + 'spell_card'
        if clean and path.exists:
            path.delete()
            path.mkdir()
        for folder in folders:
            dest = path + folder.dir_name
            if not dest.exists:
                dest.mkdir()
            Rsync.clone_dir().ignore().verbose().run( folder, dest )

    def restore( self, path, touha_name ):
        from touha import Touhas
        path = path + 'touhas'
        touhas = Touhas( path )
        touha = touhas[ touha_name ]
        backup_path = touha.path + 'spell_card' + 'root/'
        #rsync = Rsync.clone_dir().verbose().ignore()
        rsync = Rsync.archive_mode().checksum().verbose()
        rsync.run( backup_path, self.root )

    def _prepare( self ):
        logger.info( f"se encontro la spell card de {self.name}" )

    def mount( self ):
        boot, root = get_boot_root( self._block )

        if not self.boot.exists:
            self.boot.mkdir()
        if not self.root.exists:
            self.root.mkdir()

        if not Mount( boot, self.boot ).run():
            raise OSError( f"no se pudo montar {boot}" )
        if not Mount( root, self.root ).run():
            raise OSError( f"no se pudo montar {root}" )

        if self._home:
            if not self._home.exists:
                raise NotImplemented(
                    f"no existe el bloque de home '{self._home}'" )
            if not Mount( self._home, self.home ).run():
                raise OSError( f"no se pudo montar {self._home}" )

    def umount( self ):
        if self._home:
            if not Umount( self.home ).run():
                logger.warning( f"no se pudo desmontar {self.home}" )

        if not Umount( self.boot ).run():
            logger.warning( f"no se pudo desmontar {self.boot}" )
        if not Umount( self.root ).run():
            logger.warning( f"no se pudo desmontar {self.root}" )


    @property
    def boot( self ):
        return self._mount_path + 'boot'

    @property
    def root( self ):
        return self._mount_path + 'root'

    def __del__( self ):
        if self.unmount_on_dead:
            self.umount()

    def backups( self ):
        return self.touha_path.ls()

    def build_new_backup( self ):
        date = get_backup_date()
        if not self.backup_folder.exists:
            self.backup_folder.mkdir()
        root = Tar.compress().create().file(
            self.backup_folder + f'{date}__root.tar.gz' )
        root = root.input_directory( self.root )

        boot = Tar.compress().create().file(
            self.backup_folder + f'{date}__boot.tar.gz' )
        boot = boot.input_directory( self.boot )

        root.run()
        boot.run()

    @property
    def backup_folder( self ):
        return self.touha_path + 'backups'

    @property
    def touha_path( self ):
        return self.root_path + self.name

    def print_fstab( self ):
        from chibi_fstab.snippets import to_line
        fstab = self.fstab.open().read()
        for fs in fstab:
            print( to_line( fs ) )

    def add_block_in_fstab( self, block ):
        path_block = Chibi_path( block )
        if not path_block.exists:
            logging.error( f"no se encontro el bloque '{block}'" )
            raise OSError( f"no se encontro el bloque '{block}'" )
        # blocks = Lsblk( block ).run()
        blocks = Lsblk( '-o', '+SIZE', block ).run().result
        partitions = blocks[ path_block.base_name ].childs
        by_label = { p.label: p for p in partitions }
        try:
            tmp = by_label[ 'TMP' ]
            var = by_label[ 'VAR' ]
            home = by_label[ 'HOME' ]
        except KeyError as e:
            logger.error(
                "las particiones no tienen asignado las etiquetas, "
                f"usa e2label {block}X {e}"
            )
            raise
        tmp_fstab = Chibi_atlas( {
            'uuid': tmp.uuid,
            'mount': '/tmp',
            'fstype': tmp.fstype,
            'options': 'rw,relatime',
            'required': 0,
            'fs_passno': 2
        } )
        var_fstab = Chibi_atlas( {
            'uuid': var.uuid,
            'mount': '/var',
            'fstype': var.fstype,
            'options': 'rw,relatime',
            'required': 0,
            'fs_passno': 2
        } )
        home_fstab = Chibi_atlas( {
            'uuid': home.uuid,
            'mount': '/home',
            'fstype': home.fstype,
            'options': 'rw,relatime',
            'required': 0,
            'fs_passno': 2
        } )
        fstab_file = self.fstab.open()
        fstab_content = fstab_file.read()
        fstab_by_uuid = { fs.uuid: fs for fs in fstab_content }
        if tmp_fstab.uuid not in fstab_by_uuid:
            fstab_content.append( tmp_fstab )
        else:
            logger.info(
                f"block {tmp.name} con uuid {tmp_fstab.uuid} "
                "ya se encuentra en fstab" )
        if var_fstab.uuid not in fstab_by_uuid:
            fstab_content.append( var_fstab )
        else:
            logger.info(
                f"block {var.name} con uuid {var_fstab.uuid} "
                "ya se encuentra en fstab" )
        if home_fstab.uuid not in fstab_by_uuid:
            fstab_content.append( home_fstab )
        else:
            logger.info(
                f"block {home.name} con uuid {home_fstab.uuid} "
                "ya se encuentra en fstab" )

        block_home = path_block.dir_name + home.name
        block_var = path_block.dir_name + var.name

        tmp_home_mount = Chibi_temp_path( delete_on_del=False )
        tmp_var_mount = Chibi_temp_path( delete_on_del=False )


        if not Mount( block_home, tmp_home_mount ).run():
            raise OSError( f"no se pudo montar {block_home}" )
        if not Mount( block_var, tmp_var_mount ).run():
            raise OSError( f"no se pudo montar {block_var}" )

        rsync = Rsync.archive_mode().verbose().ignore_existing()
        rsync.run( self.root + 'var', tmp_var_mount )
        rsync.run( self.root + 'home', tmp_home_mount )

        if not Umount( block_home ).run():
            raise OSError( f"no se pudo desmontar {block_home}" )
        if not Umount( block_var ).run():
            raise OSError( f"no se pudo desmontar {block_var}" )

        tmp_home_mount.delete()
        tmp_var_mount.delete()

        fstab_file.write( fstab_content )
