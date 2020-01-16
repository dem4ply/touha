# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, Mock

from chibi.file.temp import Chibi_temp_path
from touha.touha import Backup


class Backup_db( unittest.TestCase ):
    def setUp( self ):
        self.root_dir = Chibi_temp_path()
        self.touhas_db = self.root_dir + 'touhas'


class Test_backup_start( Backup_db ):
    @patch( 'touha.touha.Backup.build_dd' )
    def test_should_no_run_if_no_have_block( self, build_dd ):
        path = self.touhas_db + 'backup_1'
        backup = Backup( path=path )
        with self.assertRaises( ValueError ):
            backup.start()
        build_dd.assert_not_called()

    @patch( 'touha.touha.Backup.build_dd' )
    def test_should_should_generete_the_expected_dd( self, build_dd ):
        path = self.touhas_db + 'backup_1'
        block = 'mmp0'
        backup = Backup( path=path, block=block )
        backup.start()
        build_dd.assert_called_with( i=block, o=path )


class Test_backup_restore( Backup_db ):
    pass

class Test_backup_build_dd( Backup_db ):
    def test_should_create_the_expected_result( self ):
        path = self.touhas_db + 'backup_1'
        block = 'mmp0'
        expected = f'dd bs=1M status=progress if={block} of={path}'
        backup = Backup( path=path, block=block )
        dd = backup.build_dd( i=backup.block, o=backup.path )
        self.assertEqual( expected, dd.preview() )

    def test_path_should_be_a_required_parameter( self ):
        with self.assertRaises( TypeError ):
            Backup( block='mmp0' )
