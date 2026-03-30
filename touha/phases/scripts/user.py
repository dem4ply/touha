#!/usr/bin/env python3
import sys
import logging

from chibi.config import basic_config
from chibi_command.echo import cowsay
from chibi_command.nix import User
from chibi_argsparser.common import Chibi_args

logger = logging.getLogger( 'touha.phase.user' )

parser = Chibi_args()
parser.user_name.help = "nombre del usuario"

parser.command.set_as_subparser()
parser.command.execute
parser.command.status


def user_not_exists( user ):
    if user.exists:
        logger.info( 'el usuario "{user_name}" existe' )
        return 0
    logger.info( 'el usuario "{user_name}" no existe' )
    return 1


def main():
    args = parser()
    user_name = args.user_name
    user = User.name( user_name )
    if args.command.status:
        return user_not_exists( user )
    elif args.command.execute:
        if user_not_exists( user ):
            user.create()
    return 0


if __name__ == "__main__":
    sys.exit( main() )  # pragma: no cover
