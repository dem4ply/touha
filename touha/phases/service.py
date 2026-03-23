import logging

from chibi.snippet.dict import remove_nones
from chibi_atlas import Chibi_atlas
from chibi_atlas.multi import Chibi_atlas_multi
from chibi.file import Chibi_path

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
        if not self.config_file:
            return self.status_without_config

        if self.service.exists and self.config_file.exists:
            if self.config_file.open().is_empty:
                return "empty config"
            return "exists"
        elif not self.service.exists and self.config_file.exists:
            return "missing service"
        elif self.service.exists and not self.config_file.exists:
            return "missing config"
        return "OK"

    @property
    def status_without_config( self ):
        if self.service.exists:
            return "exists"
        elif not self.service.exists:
            return "missing service"
        return "OK"

    def full_status( self, f_logger=None, level="info" ):
        if not self.config_file:
            return self.full_status_without_config(
                f_logger=f_logger, level=level )

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

            check = self.wanted_service_link
            if check.exists:
                status = "enabled"
            else:
                status = "disabled"
            f_logger( f"{check}: {status}" )
        if is_in_level( level, 'debug' ):
            f_logger( f"Contenido del archivo '{self.service}'" )
            f = self.service.open()
            text = f.file.read()
            print( text )

            f_logger( f"Contenido del archivo '{self.config_file}'" )
            f = self.config_file.open()
            text = f.file.read()
            print( text )

    def full_status_without_config( self, f_logger=None, level="info" ):
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
        if is_in_level( level, 'debug' ):
            f_logger( f"Contenido del archivo '{self.service}'" )
            f = self.service.open()
            text = f.file.read()
            print( text )

    def run( self, force=False, **kw ):
        if not self.config_file:
            return self.run_without_config( force=force, **kw )
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

        if self.validate_args( force=force, **kw ):
            config_data = self.build_config_data( **kw )
            self.write_config_data( config_data, force=force )

    def run_without_config( self, force=False, **kw ):
        if not force and self.service.exists:
            logger.info(
                f"el servicio {self.service} existe en el "
                "spellcard, se omite la creacion" )
        else:
            self.service.open().write( self.service_content )

    def enable( self ):
        if not self.wanted_path.exists:
            raise NotImplementedError(
                f'el path de wanted no existe "{self.wanted_path}"' )
        full_wanted_name = self.wanted_service_link
        if full_wanted_name.exists:
            raise NotImplementedError(
                f'el servicio ya esta habilitado "{full_wanted_name}"' )
        absolut_path_in_sd = (
            Chibi_path( '/' )
            + full_wanted_name.relative_to( self.spell_card.root )
        )
        absolute_path_service_in_sd = (
            Chibi_path( '/' )
            + self.service.relative_to( self.spell_card.root )
        )
        absolute_path_service_in_sd.link( full_wanted_name )

    def validate_args( self, **kw ):
        raise NotImplementedError

    def build_config_data( self, **kw ):
        raise NotImplementedError

    def write_config_data( self, config_data, force=False ):
        if config_data:
            self.config_file.open().write( config_data )
        else:
            raise NotImplementedError

    @property
    def service_content( self ):
        raise NotImplementedError

    @property
    def wanted_path( self ):
        return (
            self.spell_card.root + "etc/systemd/system/" +
            f'{self.wanted_by}.wants'
        )

    @property
    def wanted_service_link( self ):
        return (
            self.wanted_path
            + self.service.base_name.replace( "@", "@wlan0" ) )

    @property
    def wanted_by( self ):
        service = self.service.open().read()
        result = service.install.WantedBy
        if not result:
            raise NotImplementedError
        return result
