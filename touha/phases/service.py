import logging

from chibi.snippet.dict import remove_nones
from chibi_atlas import Chibi_atlas
from chibi_atlas.multi import Chibi_atlas_multi

from touha.phases import Phase
from touha.snippets import is_in_level


logger = logging.getLogger( "touha.spell_card.phase.service" )


class Service( Phase ):
    name = "systemctl service"

    @property
    def service( self ):
        raise NotImplementedError

    @property
    def config_file( self ):
        raise NotImplementedError

    @property
    def status( self ):
        if self.service.exists and self.config_file.exists:
            if self.config_file.is_empty:
                return "empty config"
            return "exists"
        elif not self.service.exists and self.config_file.exists:
            return "missing service"
        elif self.service.exists and not self.config_file.exists:
            return "missing config"
        return "OK"

    def full_status( self, f_logger=None, level="info" ):
        if not f_logger:
            f_logger = print
        else:
            raise NotImplementedError
        if is_in_level( level, 'info' ):
            if self.service.exists:
                status = "exists"
            else:
                status = "missing"
            f_logger( f"{self.service}: {status}" )
            if self.config_file.exists:
                status = "exists"
            else:
                status = "missing"
            f_logger( f"{self.config_file}: {status}" )
        if is_in_level( level, 'debug' ):
            f_logger( f"Contenido del archivo '{self.service}'" )
            f = self.service.open()
            text = f.file.read()
            print( text )

            f_logger( f"Contenido del archivo '{self.config_file}'" )
            f = self.config_file.open()
            text = f.file.read()
            print( text )

    def run( self, force=False, **kw ):
        if not force and self.service.exists:
            logger.info(
                f"el servicio {self.service} existe en el "
                "spellcard, se omite la creacion" )
        else:
            self.service.open().write( self.service_content )

        if not force and self.config_file.exists:
            logger.info(
                f"el config file de {self.config_file} existe en el "
                "spellcard, se omite la creacion" )
        else:
            self.config_file.touch()

        if self.validate_args( kw ):
            config_data = self.build_config_data( kw )
            self.write_config_data( config_data, force=force )

    def build_config_data( self ):
        raise NotImplementedError

    def write_config_data( self, config_data, force=False ):
        if config_data:
            config.write( config_data )
        else:
            raise NotImplementedError

    @property
    def service_content( self ):
        raise NotImplementedError
