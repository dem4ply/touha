# -*- coding: utf-8 -*-
import yaml

from chibi.file import Chibi_path
from chibi.atlas import Chibi_atlas
from chibi_command.disk.dd import DD
from touha.snippets import get_backup_date


class Touha( Chibi_atlas ):
    def __init__( self, *args, path, **kw ):
        super().__init__( *args, path=path, **kw )
        self.name = self.path.base_name
        backups = self.backup_folder
        if not backups.exists:
            backups.mkdir()
        self.backups = [ Backup( path=b )for b in backups.ls() ]

    def new_backup( self, block, **kw ):
        date = get_backup_date( **kw )
        path = self.build_backup_name( date )
        backup = Backup( path=path, block=block )
        backup.start()
        self.backups.append( backup )

    @property
    def backup_folder( self ):
        return self.path + 'backups'

    def build_backup_name( self, name ):
        return self.backup_folder + f"{name}.img"


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

    def restore( self ):
        dd = self.build_dd( i=self.path, o=self.block )
        result = dd()
        if not result:
            raise NotImplementedError( str( vars( result ) ) )

    def build_dd( self, i, o ):
        dd = DD.input_file( i ).output_file( o )
        return dd


class Touhas:
    def __init__( self, path ):
        self.path = Chibi_path( str( path ) )
        self.load()

    def __len__( self ):
        return len( self._touhas )

    def add( self, name ):
        new_touha = Touha( path=self.path + name )
        self._touhas[ name ] = new_touha

    def __getitem__( self, name ):
        return self._touhas[ name ]

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
