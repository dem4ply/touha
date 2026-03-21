import datetime

from chibi.file import Chibi_path


def parse_phase_execute_args( param ):
    k, v = param.split( '=', 1 )
    return k, v


def transform_date_to_str( date ):
    return date.strftime( "%Y-%m-%d" )


def get_backup_date( **kw ):
    if 'date' in kw:
        date = kw[ 'date' ]
    else:
        date = datetime.datetime.utcnow().date()
    if isinstance( date, ( datetime.date, datetime.datetime ) ):
        date = transform_date_to_str( date )
    else:
        raise NotImplementedError
    return date


def get_boot_root( block ):
    if block.startswith( '/dev/s' ):
        return f"{block}1", f"{block}2"
    else:
        raise NotImplementedError(
            f"no esta implementado el error para los bloques {block}" )


def is_in_level( level, expected ):
    translate = { 'info': 10, 'debug': 0 }
    if isinstance( level, str ):
        level = translate[ level.lower() ]
    if isinstance( expected, str ):
        expected= translate[ expected.lower() ]
    return level <= expected
