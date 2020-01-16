# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from chibi.file.temp import Chibi_temp_path
from touha import Touhas, Touha
from touha.snippets import get_backup_date


class Touha_db( unittest.TestCase ):
    def setUp( self ):
        self.root_dir = Chibi_temp_path()
        self.touhas_db = self.root_dir + 'touhas'


class Test_touhas_file_not_exists( Touha_db ):
    def test_should_create_the_file( self ):
        self.assertFalse( self.touhas_db.exists )
        Touhas( self.touhas_db )
        self.assertTrue( self.touhas_db.exists )


class Test_touhas_file_is_empty( Touha_db ):
    def test_should_create_a_file( self ):
        self.assertFalse( self.touhas_db.exists )
        Touhas( self.touhas_db )
        self.assertTrue( self.touhas_db.exists )

    def test_when_open_should_do_nothing( self ):
        touhas = Touhas( self.touhas_db )
        self.assertEqual( len( touhas ), 0 )


class Test_add_a_new_touha( Touha_db ):
    def setUp( self ):
        super().setUp()
        self.name = "Momiji_Inubashiri"

    def test_when_add_a_new_touha_only_with_name( self ):
        touhas = Touhas( self.touhas_db )
        touhas.add( "Momiji_Inubashiri" )
        self.assertEqual( len( touhas ), 1 )

    def test_the_new_touha_should_be_retrieve( self ):
        touhas = Touhas( self.touhas_db )
        touhas.add( self.name )
        self.assertTrue( ( touhas.path + self.name + 'backups' ).exists )
        self.assertEqual(
            len( list( ( touhas.path + self.name + 'backups' ).ls() ) ), 0 )

    def test_after_save_should_be_retrieave( self ):
        touhas = Touhas( self.touhas_db )
        touhas.add( self.name )
        touhas_2 = Touhas( self.touhas_db )
        self.assertEqual( touhas[ self.name ], touhas_2[ self.name ], )


class Test_create_backup( Touha_db ):
    def setUp( self ):
        super().setUp()
        self.name = "Momiji_Inubashiri"

    @patch( 'touha.touha.Backup.build_dd' )
    def test_should_do_the_backup_when_create_a_new_backuip( self, build_dd, ):
        touhas = Touhas( self.touhas_db )
        touhas.add( "Momiji_Inubashiri" )
        touha = touhas[ self.name ]
        touha.new_backup( '/dev/mm' )
        expected_output = (
            touha.backup_folder
            + touha.build_backup_name( get_backup_date() ) )
        build_dd.assert_called_with( i='/dev/mm', o=expected_output )
