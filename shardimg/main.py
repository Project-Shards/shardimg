# main.py
#
# Copyright 2023 axtlos <axtlos@getcryst.al>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-only
import click
import sys
from shardimg.classes.manifest import Manifest
from shardimg.functions.system import SystemImage
from shardimg.functions.boot import *
from shardimg.functions.init import *
from shardimg.utils.log import setup_logging
logger = setup_logging()

@click.group()
@click.option('--verbose', is_flag=True, help='Enables verbose mode.', default=False)
def main(verbose):
    if verbose:
        print("Verbose mode enabled")

@main.command()
@click.option('--manifest', help='Path to the manifest file.', default="manifest.json")
@click.option('--build-dir', help='Path to the build directory.', default="build")
@click.option('--repo', help='Path to the flatpak repository. Can be an empty directory.', default="repo")
@click.option('--keep', is_flag=True, help='Keep the build directory after the build.', default=False)
def build(manifest, build_dir, keep, repo):
    print(manifest)
    manifest_parsed = Manifest(manifest=manifest)
    manifest_parsed.parse_manifest()
    print(manifest_parsed)
    print("Name "+manifest_parsed.name)
    print("ID "+manifest_parsed.id)
    print("Type "+manifest_parsed.type)
    print("Author "+manifest_parsed.author)
    print("Packages "+str(manifest_parsed.packages))
    print("Base "+manifest_parsed.base)
    print("Commands" +str(manifest_parsed.commands))
    print("FsGuard enabled "+str(manifest_parsed.fsguard_enabled))
    print("FsGuard binary "+manifest_parsed.fsguard_binary)
    print("FsGuard paths "+" ".join(manifest_parsed.fsguard_paths))
    print("Building")
    if manifest_parsed.id.count(".") < 2:
        logger.error("Invalid ID. Must contain at least 2 periods")
        sys.exit(1)
    if manifest_parsed.type == "system":
        SystemImage.build_system_image(manifest=manifest_parsed,
                                       build_dir=build_dir,
                                       repo=repo,
                                       manifest_path=manifest,
                                       fsguard_enabled=manifest_parsed.fsguard_enabled,
                                       fsguard_binary=manifest_parsed.fsguard_binary,
                                       fsguard_paths=manifest_parsed.fsguard_paths
                                       )
    elif manifest_parsed.type == "boot":
        build_boot_image(manifest_parsed, build_dir, repo, manifest)
@main.command()
@click.argument('directory', type=click.Path(exists=False), default=".")
@click.option('--name', prompt='What name should your image have?', help='The name of the image')
@click.option('--id', prompt='What is the ID of your image?', help='An image id in the reverse domain name notation')
@click.option('--version', prompt='Which version is your image?', help='The version of your image', default="1.0")
@click.option('--author', prompt='Who is the author of this image?', help='Your name/username to show who created the image', default=lambda: os.environ.get("USER", ""), show_default="current user")
@click.option('--type', type=click.Choice(["boot", "system"], case_sensitive=False), prompt='What type of image do you want to Create?', help='The type of image to create, can be boot and system', default="system")
@click.option('--base', prompt='What image should be used as the base?', help='The base image to be used, can be empty to create an independent image', default='')
def init(directory, name, id, version, author, type, base):
    print(directory)
    print(name)
    print(id)
    print(version)
    print(author)
    print(type)
    print(base)
    initialize_directory(directory, name, id, version, author, type, base)


if __name__ == '__main__':
    sys.exit(main.main())
