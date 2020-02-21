import datetime


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
