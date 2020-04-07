from chibi_command.disk.mount import Mount, Umount


def _mount( args ):
    block = args.block
    boot = f"{block}p1"
    root = f"{block}p2"

    boot_path = args.backup_path + 'boot'
    root_path = args.backup_path + 'root'
    if not boot_path.exists:
        boot_path.mkdir()
    if not root_path.exists:
        root_path.mkdir()

    if not Mount( boot, boot_path ).run():
        raise OSError( f"no se pudo montar {boot}" )
    if not Mount( root, root_path ).run():
        raise OSError( f"no se pudo montar {root}" )

    return boot_path, root_path


def _umount( args ):
    boot_path = args.backup_path + 'boot'
    root_path = args.backup_path + 'root'
    if not boot_path.exists:
        boot_path.mkdir()
    if not root_path.exists:
        root_path.mkdir()

    if not Umount( boot_path ).run():
        raise OSError( f"no se pudo desmontar {boot_path}" )
    if not Umount( root_path ).run():
        raise OSError( f"no se pudo desmontar {root_path}" )

    return boot_path, root_path
