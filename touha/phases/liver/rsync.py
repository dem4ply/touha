import logging

from chibi.snippet.dict import remove_nones
from chibi_atlas import Chibi_atlas
from chibi_atlas.multi import Chibi_atlas_multi
from chibi.file import Chibi_path

from touha.phases import Phase
from touha.snippets import is_in_level
from chibi_command.archilinux import Pacman
from chibi_command import Command
from touha.phases.liver.pacman import Pacman_package


logger = logging.getLogger( "touha.phase.liver.chibi" )


class Rsync( Pacman_package ):
    name = "rsync"
    package = "rsync"
    sudo = 'sudo'
