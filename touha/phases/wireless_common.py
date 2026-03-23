import logging

from chibi.snippet.dict import remove_nones
from chibi_atlas import Chibi_atlas
from chibi_atlas.multi import Chibi_atlas_multi
from chibi.file import Chibi_path
from chibi.file.other import Chibi_systemd
from chibi_wpa_supplicant import Chibi_wpa_supplicant_conf

from touha.phases import Phase
from touha.snippets import is_in_level
from touha.phases.service import Service


logger = logging.getLogger( "touha.spell_card.phase.wireless_common" )


class Wireless_common( Service ):
    name = "wireless_common"

    @property
    def service( self ):
        path = (
            self.spell_card.root
            + 'etc/systemd/system/network_wireless_common@.service' )
        path = Chibi_path( path, chibi_file_class=Chibi_systemd )
        return path

    @property
    def config_file( self ):
        path= self.spell_card.root + 'etc/wpa_supplicant/commond.conf'
        return Chibi_path(
            path, chibi_file_class=Chibi_wpa_supplicant_conf )

    def validate_args( self, *, force=False, wpa_config, **kw ):
        wpa_config = Chibi_path(
            wpa_config, chibi_file_class=Chibi_wpa_supplicant_conf )
        if force or not wpa_config.exists:
            return True
        else:
            logger.info(
                f'No se encontro la configuracion de "{wpa_config}"'
                "configuracion de wpa, se omite la actualzacion del config" )

    def build_config_data( self, *, wpa_config, **kw ):
        wpa_config = Chibi_path(
            wpa_config, chibi_file_class=Chibi_wpa_supplicant_conf )
        content = wpa_config.open().read()
        return content

    @property
    def service_content( self ):
        result = Chibi_atlas()
        result.unit = Chibi_atlas()
        result.unit.Description = (
            "Se connecta a una de las wifis que estan en "
            "common.conf usando %i" )
        result.unit.Wants = "network.target"
        result.unit.Before = "network.target"
        result.unit.BindsTo = "sys-subsystem-net-devices-%i.device"
        result.unit.After = "sys-subsystem-net-devices-%i.device"

        result.service = Chibi_atlas_multi()
        result.service.Type = 'oneshot'
        result.service.RemainAfterExit = 'yes'
        result.service.ExecStart = '/usr/bin/rfkill unblock wifi'
        result.service.ExecStart = '/usr/bin/ip link set %i up'
        result.service.ExecStart = (
            '/usr/bin/wpa_supplicant -B -i %i -c '
            '/etc/wpa_supplicant/common.conf'
        )
        result.service.ExecStart = ( '/usr/bin/dhcpcd %i' )

        result.service.ExecStop = '/usr/bin/ip addr flush dev %i'
        result.service.ExecStop = '/usr/bin/ip link set %i down'

        result.install = Chibi_atlas_multi()
        result.install.WantedBy = 'multi-user.target'
        return result
