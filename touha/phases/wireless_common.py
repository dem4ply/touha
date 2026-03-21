import logging

from chibi.snippet.dict import remove_nones
from chibi_atlas import Chibi_atlas
from chibi_atlas.multi import Chibi_atlas_multi

from touha.phases import Phase
from touha.snippets import is_in_level


logger = logging.getLogger( "touha.spell_card.phase.wireless_adhoc" )


class Wireless_adhoc( Phase ):
    name = "wireless_adhoc"

    @property
    def service( self ):
        return self.spell_card.adhoc_service

    @property
    def config_file( self ):
        return self.spell_card.wlan0_adhoc_config

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

    @property
    def is_missing( self ):
        return self.status != "ok"

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

        if kw and ( 'IP' in kw or 'MASK' in kw ):
            config = self.config_file.open()
            config_data = config.read()
            try:
                config_data.IP = kw.get( 'IP', config_data.IP )
            except AttributeError:
                config_data.IP = kw.get( 'IP', None )
            try:
                config_data.MASK = kw.get( 'MASK', config_data.MASK )
            except AttributeError:
                config_data.MASK = kw.get( 'MASK', None )

            config_data = remove_nones( config_data )

            if not force and config_data:
                config.write( config_data )
            else:
                raise NotImplementedError
        else:
            logger.info(
                "no se mandaron los parametros IP o MASK para la fase"
                "se ignora su actualizacion" )

    @property
    def service_content( self ):
        result = Chibi_atlas()
        result.unit = Chibi_atlas()
        result.unit.Description = "Ad-hoc wireless network for gensokyo(%i)"
        result.unit.Wants = "network.target"
        result.unit.Before = "network.target"
        result.unit.BindsTo = "sys-subsystem-net-devices-%i.device"
        result.unit.After = "sys-subsystem-net-devices-%i.device"

        result.service = Chibi_atlas_multi()
        result.service.Type = 'oneshot'
        result.service.RemainAfterExit = 'yes'
        result.service.EnvironmentFile = (
            '/etc/conf.d/network_wireless_adhoc@%i'
        )
        result.service.ExecStart = '/usr/bin/rfkill unblock wifi'
        result.service.ExecStart = '/usr/bin/ip link set %i up'
        result.service.ExecStart = (
            '/usr/bin/wpa_supplicant -B -i %i -D nl80211,wext -c '
            '/etc/wpa_supplicant/adhoc_gensokyo.conf'
        )
        result.service.ExecStart = (
            '/usr/bin/ip addr add ${addr}/${mask} dev %i' )
        result.service.ExecStop = '/usr/bin/ip addr flush dev %i'
        result.service.ExecStop = '/usr/bin/ip link set %i down'

        result.install = Chibi_atlas_multi()
        result.install.WantedBy = 'multi-user.target'
        return result
