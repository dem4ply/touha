import logging

from chibi.snippet.dict import remove_nones
from chibi_atlas import Chibi_atlas
from chibi_atlas.multi import Chibi_atlas_multi
from chibi.file import Chibi_path

from touha.phases import Phase
from touha.snippets import is_in_level
from chibi_command.archilinux import Pacman as Pacman_command
from touha.phases.liver import Phase_simple_command
from chibi_command import Result_error
from chibi_command import Command


logger = logging.getLogger( "touha.phase.liver.pacman" )


class Pacman_key_command( Command ):
    command = 'pacman-key'

    @classmethod
    def init( cls ):
        return cls( '--init' )

    @classmethod
    def refresh( cls ):
        return cls( '--refresh-keys' )

    @classmethod
    def populate( cls ):
        return cls( '--populate', 'archlinuxarm' )


class Pacman_key( Phase_simple_command ):
    name = "pacman_key"
    command = Pacman_key_command.init()

    @property
    def ssh( self ):
        ssh = super().ssh
        ssh.sudo_command = 'su'
        return ssh


class Pacman_key_populate( Phase_simple_command ):
    name = "pacman_key_populate"
    command = Pacman_key_command.populate()

    @property
    def ssh( self ):
        ssh = super().ssh
        ssh.sudo_command = 'su'
        return ssh


class Pacman( Phase_simple_command ):
    name = "pacman"
    command = Pacman_command.upgrade()

    @property
    def ssh( self ):
        ssh = super().ssh
        ssh.sudo_command = 'su'
        return ssh


class Pacman_package( Phase_simple_command ):
    name = "pacman install"
    sudo = 'sudo'

    def build_command( self ):
        if not self.package:
            raise NotImplementedError(
                "se tiene que definir el comando de la "
                f"clase {type(self)}.package" )
        return Pacman_command.install( self.package )

    def run_command( self, command, sudo=None ):
        ssh = self.ssh
        if sudo:
            ssh.sudo_command = sudo
        ssh.append( command )
        result = ssh.run()
        return result

    def run( self ):
        command = self.build_command()
        self.run_command( command, sudo=self.sudo )

    @property
    def status( self ):
        check_command = Pacman_command.info( self.package )
        try:
            result = self.run_command( check_command )
        except Result_error:
            return "no instalado"
        return "instalado"
