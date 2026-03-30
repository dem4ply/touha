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


logger = logging.getLogger( "touha.phase.liver.stato" )



class Alarm_password( Phase_simple_command ):
    name = "alarm_password"
    command = Command( "echo 'password' | passwd --stdin alarm" )

    @property
    def ssh( self ):
        ssh = super().ssh
        ssh.sudo_command = 'su'
        return ssh
