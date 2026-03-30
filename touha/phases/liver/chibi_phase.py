import logging

from chibi.snippet.dict import remove_nones
from chibi_atlas import Chibi_atlas
from chibi_atlas.multi import Chibi_atlas_multi
from chibi.file import Chibi_path

from touha.phases import Phase
from touha.snippets import is_in_level
from chibi_command.archilinux import Yay
from touha.phases.liver import Phase_chain_commands
from chibi_command import Result_error


logger = logging.getLogger( "touha.phase.liver.chibi" )


class Chibi_phase( Phase_chain_commands ):
    name = "chibi"

    @property
    def ssh( self ):
        ssh = self.spell_card.ssh
        ssh.raise_on_fail = True
        return ssh

    @property
    def status( self ):
        from chibi_command.archilinux import Pacman as Pacman_command
        check_command = Pacman_command.info( 'python-chibi' )
        try:
            result = self.run_command( check_command )
        except Result_error:
            return "chibi no instalado"
        check_command = Pacman_command.info( 'python-chibi-command' )
        try:
            result = self.run_command( check_command )
        except Result_error:
            return "chibi command no instalado"
        return "instalado"


    def build_command( self ):
        yield Yay.install( 'python-chibi', 'python-chibi-command' )
