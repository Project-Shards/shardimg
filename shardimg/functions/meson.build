pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
functionsdir = join_paths(pkgdatadir, 'shardimg/functions')

shardimg_sources = [
    '__init__.py',
    'desktop.py',
    'system.py',
]

install_data(shardimg_sources, install_dir: functionsdir)
