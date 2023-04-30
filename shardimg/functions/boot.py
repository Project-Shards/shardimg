# boot.py
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

from shardimg.classes.manifest import Manifest
from shardimg.utils.files import FileUtils
from shardimg.utils.command import Command
from shardimg.utils.disks import DiskUtils
from shardimg.utils.log import setup_logging
from shardimg.utils.shards import Shards
import random, string, os
logger = setup_logging()

def build_boot_image(
        manifest: Manifest,
        build_dir: str,
        repo: str,
        manifest_path
):
    include_dir = os.path.abspath(manifest_path).split("/")
    include_dir.pop()
    include_dir.append("include")
    print(include_dir)
    include_dir = "/".join(include_dir)
    #print(include_dir)
    print(os.path.abspath(manifest_path))
    FileUtils.create_directory(build_dir)
    FileUtils.create_directory(build_dir+"/root")
    FileUtils.create_directory(build_dir+"/include")
    FileUtils.copy_directory(include_dir, build_dir, False)
    FileUtils.copy_file(manifest_path, build_dir+"/include/manifest.json", True)
    Shards.install_packages(manifest.packages, build_dir+"/root")
    Shards.execute_commands(manifest.commands, build_dir+"/root")
    Shards.generate_flatpak_manifest(manifest, build_dir)
    Shards.build_flatpak(manifest, build_dir, repo)
