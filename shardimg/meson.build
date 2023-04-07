pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'shardimg')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('pkgdatadir', pkgdatadir)
configure_file(
            input: 'shardimg.in',
           output: 'shardimg',
    configuration: conf,
          install: true,
      install_dir: get_option('bindir')
)

shardimg_sources = [
    '__init__.py',
    'main.py'
]

install_data(shardimg_sources, install_dir: moduledir)
subdir('classes')
subdir('utils')
subdir('functions')
