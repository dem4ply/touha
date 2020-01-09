# -*- coding: utf-8 -*-
import yaml

from chibi.file import Chibi_path
from chibi.atlas import Chibi_atlas
from chibi_command.dd import dd


class Touha( Chibi_atlas ):
    def __init__( self, *args, path, **kw ):
        super().__init__( *args, path=path, **kw )
        self.name = self.path.base_name
        backups = self.path  + 'backups'
        if not backups.exists:
            backups.mkdir()
        self.backups = [ Backup( path=b )for b in backups.ls() ]

    def new_backup( self, path, block ):
        pass


class Backup( Chibi_atlas ):
    def __init__( self, *args, path, **kw ):
        super().__init__( *args, path=path, **kw )


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
