import logging


logger = logging.getLogger( "touha.spell_card.phase" )


class Phase:
    name = "phase base"
    def __init__( self, spell_card ):
        self._spell_card = spell_card

    def run( self, force=False ):
        raise NotImplementedError

    @property
    def spell_card( self ):
        return self._spell_card

    @property
    def status( self ):
        raise NotImplementedError(
            f"el status para la fase {self.name} no esta implementado" )

    @property
    def full_status( self ):
        raise NotImplementedError(
            f"el full status para la fase {self.name} no esta implementado" )

    def _status_file( self, path ):
        if path.exists:
            status = "exists"
        else:
            status = "missing"
        return f"{path}: {status}"

    def _status_full_file( self, path ):
        f = path.open()
        text = f.read_text()
        result = [ f"Contenido del archivo '{path}'" ]
        result.append( text )
        return "\n".join( result )
