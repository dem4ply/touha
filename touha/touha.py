# -*- coding: utf-8 -*-
import logging
import yaml
import datetime

from chibi.file import Chibi_path
from chibi.atlas import Chibi_atlas
from chibi_command.disk.dd import DD
from chibi_command.disk.mount import Mount, Umount
from touha.snippets import get_backup_date
from touha.spell_card import Spell_card


logger = logging.getLogger( 'touhas.touhas' )


class Touha( Chibi_atlas ):
    def __init__( self, *args, path=None, name=None, **kw ):
        super().__init__( *args, path=path, name=name, **kw )
        if name is None:
            self.name = self.path.base_name
        else:
            self.name = name
        if path is None:
            self.path = Chibi_path() + self.name
        backups = self.backup_folder
        if not backups.exists:
            backups.mkdir()
        self.backups = [ Backup( path=b )for b in backups.ls() ]

    def new_backup( self, block, **kw ):
        date = get_backup_date( **kw )
        path = self.build_backup_name( date )
        logger.info( f"creadno backup en {path} usando el blocke {block}" )
        backup = Backup( path=path, block=block )
        backup.start()
        self.backups.append( backup )

    @property
    def backup_folder( self ):
        return self.path + 'backups'

    def build_backup_name( self, name ):
        return self.backup_folder + f"{name}.img"

    def __str__( self ):
        return self.name

    def __repr__( self ):
        return f"Touha( name={self.name}, path={self.path} )"

    @classmethod
    def from_block( cls, block, mount_path ):
        spell_card = Spell_card( block=block, mount_path=mount_path )
        return cls.from_spell_card( Spell_card )

    @classmethod
    def _from_spell_card( cls, spell_card ):
        return cls( name=spell_card.name, spell_card=spell_card )


class Backup( Chibi_atlas ):
    def __init__( self, *args, path, block=None, **kw ):
        super().__init__( *args, path=path, block=block, **kw )

    def start( self ):
        if not self.block:
            raise ValueError( "was expected the block is going to clone" )
        dd = self.build_dd( i=self.block, o=self.path )
        result = dd()
        if not result:
            raise NotImplementedError( str( vars( result ) ) )

    def restore( self, block=None ):
        if block is None:
            block = self.block
        if block is None:
            raise NotImplementedError(
                "bloque no definido para la restauracion" )
        dd = self.build_dd( i=self.path, o=block )
        result = dd()
        if not result:
            raise NotImplementedError( str( vars( result ) ) )

    def build_dd( self, i, o ):
        dd = DD.input_file( i ).output_file( o )
        return dd

    @property
    def date( self ):
        str_date = self.path.file_name
        return datetime.datetime.strptime( str_date, "%Y-%m-%d" )


class Touhas():
    def __init__( self, path=None, *args, **kw ):
        super().__init__( *args, **kw )
        if path is None:
            path = Chibi_path( 'touhas' )
        self.path = Chibi_path( str( path ) )
        self.load()

    def __len__( self ):
        return len( self._touhas )

    def add( self, name ):
        logger.info( f"agregando touha {name}" )
        new_touha = Touha( path=self.path + name )
        self._touhas[ name ] = new_touha

    def __getitem__( self, name ):
        try:
            return self._touhas[ name ]
        except KeyError:
            self.add( name )
            return self[ name ]

    def __iter__( self ):
        return iter( self._touhas )

    def load( self ):
        if not self.path.exists:
            self.path.mkdir()
        self._touhas = {
            path.base_name: Touha( path=path ) for path in self.path.ls() }


def get_touhas( path ):
    touhas = path.open().read()
    return touhas


yaml.add_representer(
    Touha, yaml.representer.SafeRepresenter.represent_dict )
