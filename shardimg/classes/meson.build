pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
classesdir = join_paths(pkgdatadir, 'shardimg/classes')

shardimg_sources = [
    '__init__.py',
    'manifest.py',
]

install_data(shardimg_sources, install_dir: classesdir)
