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
import random, string
logger = setup_logging()

def build_boot_image(
        manifest: Manifest,
        build_dir: str
):
    FileUtils.create_directory(build_dir)
    FileUtils.create_directory(build_dir+"/root")
    Shards.install_packages(manifest.packages, build_dir+"/root")

def create_boot_overlay(build_dir: str, base: str):
    FileUtils.create_directory(build_dir+"/workdir")
    FileUtils.create_directory(build_dir+"/root")

    DiskUtils.overlay_mount(
        lowerdirs=[build_dir+"/system"],
        upperdir=build_dir+"/desktop",
        workdir=build_dir+"/workdir",
        destination=build_dir+"/root"
    )
