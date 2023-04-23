# -*- coding: utf-8 -*-
import datetime
import unittest

from touha.snippets import transform_date_to_str, get_backup_date
from touha.snippets import get_boot_root


class Test_transform_date_to_str( unittest.TestCase ):
    def test_with_datetime_should_work( self ):
        date = datetime.datetime( 2000, 1, 2, 12, 10, 20, 22)
        expected = '2000-01-02'
        self.assertEqual( expected, transform_date_to_str( date ) )

    def test_with_date_should_work( self ):
        date = datetime.date( 2000, 1, 2, )
        expected = '2000-01-02'
        self.assertEqual( expected, transform_date_to_str( date ) )


class Test_get_backup_date( unittest.TestCase ):
    def test_without_params_should_get_today( self ):
        expected = transform_date_to_str( datetime.datetime.utcnow() )
        result = get_backup_date()
        self.assertEqual( expected, result )

    def test_with_the_params_should_get_the_date_sended( self ):
        date = datetime.date( 2000, 1, 2, )
        expected = '2000-01-02'
        result = get_backup_date( date=date )
        self.assertEqual( expected, result )

    def test_with_the_params_should_get_the_datetime_sended( self ):
        date = datetime.datetime( 2000, 1, 2, 12, 10, 20, 22)
        expected = '2000-01-02'
        result = get_backup_date( date=date )
        self.assertEqual( expected, result )


class Test_get_boot_root( unittest.TestCase ):
    def test_with_sdc_should_return_sdc1_and_sdc2( self ):
        boot, root = get_boot_root( '/dev/sdc' )
        boot_expected = '/dev/sdc1'
        root_expected = '/dev/sdc2'
        self.assertEqual( boot_expected, boot )
        self.assertEqual( root_expected, root )
