import logging

from chibi.snippet.dict import remove_nones
from chibi_atlas import Chibi_atlas
from chibi_atlas.multi import Chibi_atlas_multi
from chibi.file import Chibi_path

from touha.phases import Phase
from touha.snippets import is_in_level
from touha.phases.liver.pacman import Pacman_package
from chibi_command import Command
from chibi_command.common import Cd
from touha.phases.liver import Phase_chain_commands


logger = logging.getLogger( "touha.phase.liver.chibi" )


class Git( Pacman_package ):
    name = "git"
    package = "git"
    sudo = 'su'


class Base_devel( Pacman_package ):
    name = "base_devel"
    package = "base-devel"
    sudo = 'su'


class Yay( Phase_chain_commands ):
    name = "yay"

    @property
    def status( self ):
        from chibi_command.archilinux import Pacman as Pacman_command
        check_command = Pacman_command.info( 'yay' )
        try:
            result = self.run_command( check_command )
        except Result_error:
            return "no instalado"
        return "instalado"

    def run( self ):
        ssh = self.ssh
        for command in self.build_command():
            ssh.append( command )
        #ssh.sudo_command = 'su'
        ssh.run()

    def build_command( self ):
        cd = Cd( '/tmp/' )
        yield cd
        yield Command( '[ -d "yay" ] && rm -rf yay' )
        clone = Command(
            'git', 'clone', 'https://aur.archlinux.org/yay.git' )
        yield clone
        #yield Command( 'chown -R alarm:alarm yay' )
        cd = Cd( 'yay' )
        yield cd
        #yield Command( "su alarm -c 'makepkg -s'" )
        #yield Command( 'pacman -U yay*.pkg.tar.zst' )
        yield Command( 'makepkg', '-si',)
