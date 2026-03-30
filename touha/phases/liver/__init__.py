from chibi_atlas import Chibi_atlas
from chibi.nix import user_exists
from chibi_container import Liver
from touha.phases import Phase


class Touha_liver( Liver ):
    @property
    def phases( self ):
        """
        contrulle el dicionario de phases para el liver
        """
        from touha.phases.liver.pacman import (
            Pacman, Pacman_key, Pacman_key_populate
        )
        from touha.phases.liver.stato import Alarm_password
        from touha.phases.liver.yay import Git, Base_devel, Yay
        from touha.phases.liver.sudo import Sudo
        from touha.phases.liver.chibi_phase import Chibi_phase
        from touha.phases.liver.rsync import Rsync

        phases_list = [
            Alarm_password( self ),
            Pacman_key( self ),
            Pacman_key_populate( self ),
            Pacman( self ),
            Sudo( self ),
            Rsync( self ),
            Git( self ),
            Base_devel( self ),
            Yay( self ),
            Chibi_phase( self ),
        ]
        return Chibi_atlas( { p.name: p for p in phases_list } )


class Phase_liver( Phase ):
    @property
    def ssh( self ):
        ssh = self.spell_card.ssh
        ssh.raise_on_fail = False
        return ssh

    def run_command( self, command ):
        ssh = self.ssh
        ssh.append( command )
        result = ssh.run()
        return result


class Phase_simple_command( Phase_liver ):
    command = None

    def build_command( self ):
        if not self.command:
            raise NotImplementedError(
                "se tiene que definir el comando de la "
                f"clase {type(self)}.command" )

        return self.command

    def run( self ):
        command = self.build_command()
        self.run_command( command )


class Phase_chain_commands( Phase_simple_command ):

    def run( self ):
        ssh = self.ssh
        for command in self.build_command():
            ssh.append( command )
        ssh.run()
