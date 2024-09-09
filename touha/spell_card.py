import logging
from chibi_command.disk.mount import Mount, Umount
from chibi.file import Chibi_path
from chibi_command.rsync import Rsync
from chibi_command.file import Tar

from touha.snippets import get_boot_root, get_backup_date


logger = logging.getLogger( 'touhas.spell_card' )

class Spell_card:
    def __init__(
            self, block=None, mount_path=None, unmount_on_dead=True,
            root_path=None ):
        self._mount_path = mount_path
        self._block = block
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

    @property
    def hostname( self ):
        return self.root + 'etc' + 'hostname'

    @property
    def hosts( self ):
        return self.root + 'etc' + 'hosts'

    @property
    def adhoc_service( self ):
        return self.root + 'etc/systemd/system/network_wireless_adhoc@.service'

    @property
    def wlan0_adhoc_config( self ):
        return self.root + 'etc/conf.d/network_wireless_adhoc@wlan0'

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
        return self.root + 'etc/fstab'

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

    def umount( self ):
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
