pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
utilsdir = join_paths(pkgdatadir, 'shardimg/utils')

shardimg_sources = [
    '__init__.py',
    'podman.py',
    'command.py',
    'files.py',
    'log.py',
]

install_data(shardimg_sources, install_dir: utilsdir)
