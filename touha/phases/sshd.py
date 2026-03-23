import logging

from chibi.snippet.dict import remove_nones
from chibi_atlas import Chibi_atlas
from chibi_atlas.multi import Chibi_atlas_multi
from chibi.file import Chibi_path

from touha.phases import Phase
from touha.snippets import is_in_level
from chibi.config import default_file_load, configuration
from chibi_sshd import Chibi_authorized_keys, Chibi_sshd_conf


logger = logging.getLogger( "touha.spell_card.phase.sshd" )


class Sshd( Phase ):
    name = "sshd"

    @property
    def service( self ):
        raise NotImplementedError

    @property
    def chibi_config( self ):
        return configuration.touha.spell_card.phase.sshd

    @property
    def allow_user( self ):
        allow_user = self.chibi_config.allow_users
        if not allow_user:
            list_of_home_user = " ".join(
                ( user.base_name for user in self.spell_card.home.ls() ) )
            raise NotImplementedError(
                "No esta asignado un usaurio en la configuracion de chibi en "
                "'configuration.touha.spell_card.phase.sshd.allow_users', "
                f"usuarios disponibles: {list_of_home_user}" )
        return allow_user

    @property
    def authorized_keys_files( self ):
        for user in self.allow_user:
            home = self.spell_card.home + user
            if not home.exists:
                logger.warning(
                    f"no se encontro el home del usuario {user}" )
                continue
            ssh = home + '.ssh'
            if not ssh.exists:
                logger.warning(
                    f"el usuario {user} no tiene el directiorio '{ssh}'" )
            autorization_keys = ssh + 'authorized_keys'
            yield autorization_keys

    @property
    def authorized_public_key( self ):
        key = self.chibi_config.authorized_key
        if not key:
            raise NotImplementedError(
                "No esta asignado la public key en "
                "'configuration.touha.spell_card.phase.sshd.authorized_key', "
            )
        if not isinstance( key, Chibi_path ):
            raise NotImplementedError(
                "no esta implementado que "
                "'configuration.touha.spell_card.phase.sshd.authorized_key', "
                "no sea un Chibi_path siendo el tipo "
                f"{type(key)} con valor: {key}"
            )
        return key.open().read_text()

    @property
    def config_file( self ):
        path = self.spell_card.root + 'etc/ssh/sshd_config'
        path = Chibi_path(
            path, chibi_file_class=Chibi_sshd_conf )
        return path

    @property
    def status( self ):
        if not self.config_file:
            return "missing config"
        config = self.config_file.open().read()
        try:
            password = config.PasswordAuthentication
            if config.PasswordAuthentication:
                return "PasswordAuthentication enabled"
        except:
            return "PasswordAuthentication missing"
        else:
            return "OK"

    def full_status( self, f_logger=None, level="info" ):
        if not f_logger:
            f_logger = print
        else:
            raise NotImplementedError

        chibi_config = configuration.touha.spell_card.phase.sshd
        expected_chibi_config = [ 'allow_users' ]
        missing_keys = [
            k for k in expected_chibi_config if k not in chibi_config ]
        if missing_keys:
            f_logger( "chibi configuration missing:" )
            for k in missing_keys:
                f_logger( f"\tconfiguration.touha.spell_card.phase.sshd.{k}" )

        for k, v in chibi_config.items():
            f_logger(
                f"configuration.touha.spell_card.phase.sshd.{k}: {v}" )

        if is_in_level( level, 'info' ):
            status = self._status_file( self.config_file )
            f_logger( status )

            for authorized_keys in self.authorized_keys_files:
                status = self._status_file( authorized_keys )
                f_logger( status )

        if is_in_level( level, 'debug' ):
            status = self._status_full_file( self.config_file )
            f_logger( status )

            for authorized_keys in self.authorized_keys_files:
                status = self._status_full_file( authorized_keys )
                f_logger( status )

    def run( self, force=False, **kw ):
        if not force and self.config_file.exists:
            logger.info(
                f"el config file de {self.config_file} existe en el "
                "spellcard, se omite la creacion" )
        else:
            self.config_file.open().write( self.config_default_content )

        if self.validate_args( force=force, **kw ):
            config_data = self.build_config_data( **kw )
            self.write_config_data( config_data, force=force )

        for authorized_keys in self.authorized_keys_files:
            if not authorized_keys.exists:
                authorized_keys.touch()
            public_key = self.authorized_public_key
            if public_key not in authorized_keys:
                logger.info(
                    f"escribiendo la llave publica '{public_key}' "
                    f"en '{authorized_keys}'"
                )
                authorized_keys.open().append( public_key )

    def validate_args( self, **kw ):
        if not kw:
            return False

    def build_config_data( self, **kw ):
        raise NotImplementedError

    def write_config_data( self, config_data, force=False ):
        if config_data:
            self.config_file.open().write( config_data )
        else:
            raise NotImplementedError

    @property
    def config_default_content( self ):
        expected = {
            'AuthorizedKeysFile': '.ssh/authorized_keys',
            'PasswordAuthentication': False,
            'ChallengeResponseAuthentication': False,
            'UsePAM': True,
            'PrintMotd': False,
            'UseDNS': False,
            'Subsystem': 'sftp /usr/lib/ssh/sftp-server',
            'AllowUsers': ( self.allow_user ),
        }
        return expected
