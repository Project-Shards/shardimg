# system.py
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

import os
from pathlib import Path
from shardimg.classes.manifest import Manifest
from shardimg.utils.files import FileUtils
from shardimg.utils.command import Command
from shardimg.utils.shards import Shards
from shardimg.utils.disks import DiskUtils
from shardimg.utils.log import setup_logging
logger=setup_logging()

def build_system_image(
        manifest: Manifest,
        build_dir: str,
        repo: str,
        manifest_path: str,
        suid_paths: list = ["usr"],
        suid_exclude: list = []
):
    """
    Builds a flatpak system image based on the passed manifest.

    Parameters:
    manifest      (Manifest): The parsed manifest containing all required data
    build_dir     (str)     : The build directory
    repo          (str)     : Path to the repo that the final flatpak will be added to
    manifest_path (str)     : Path to the original manifest
    suid_paths    (list)    : Paths that should be checked for suid binaries. Defaults to usr if not specified
    suid_exclude  (list)    : Paths that should be excluded from the suid binary check (optional)
    """
    include_dir = os.path.abspath(manifest_path).split("/")
    include_dir.pop()
    include_dir.append("include")
    include_dir = "/".join(include_dir)

    logger.info(f"Populate build directory {build_dir}")
    FileUtils.create_directory(build_dir)
    FileUtils.create_directory(build_dir+"/root")
    FileUtils.create_directory(build_dir+"/root/proc")
    FileUtils.create_directory(build_dir+"/root/sys")
    FileUtils.create_directory(build_dir+"/root/dev")

    logger.info("Add manifest.json to include")
    FileUtils.copy_file(manifest_path, build_dir+"/manifest", False)
    FileUtils.create_directory(build_dir+"/include")
    FileUtils.copy_directory(include_dir, build_dir, False)
    FileUtils.copy_file(manifest_path, build_dir+"/include/manifest.json", True)

    logger.info(f"Mount proc, sys and dev in {build_dir}/root")
    DiskUtils.mount(source="/proc", mountpoint=build_dir+"/root/proc", fs="proc")
    DiskUtils.mount(source="/sys", mountpoint=build_dir+"/root/sys", fs="sysfs")
    DiskUtils.mount(source="/dev", mountpoint=build_dir+"/root/dev", options=["bind"])

    logger.info("Installing packages")
    Shards.install_packages(manifest.packages, build_dir+"/root")
    logger.info("Executing commands")
    Shards.execute_commands(manifest.commands, build_dir+"/root")

    logger.info("Unmounting proc, sys and dev")
    DiskUtils.unmount(mountpoint=build_dir+"/root/proc")
    DiskUtils.unmount(mountpoint=build_dir+"/root/sys")
    DiskUtils.unmount(mountpoint=build_dir+"/root/dev")

    logger.info("Getting binaries with suid bit")
    suid_binaries = []
    for path in suid_paths:
        for (dirpath, dirname, filenames) in os.walk(build_dir+"/root/"+path):

            for file in filenames:
                print(dirpath+"/"+file)
                filepath = dirpath+"/"+file
                filepath = os.path.abspath(dirpath+"/"+FileUtils.get_symlink(filepath)) if FileUtils.get_symlink(filepath) is not None else filepath
                if not os.path.isfile(filepath):
                    filepath = build_dir+"/root"+os.path.abspath(FileUtils.get_symlink(dirpath+"/"+file))
                if FileUtils.is_suid(filepath):
                    suid_binaries.append(filepath.replace(os.path.abspath(build_dir+"/root"),"").replace(build_dir+"/root",""))

    logger.info("Writing suid binaries to file")
    if os.path.exists(build_dir+"/include/suid_binaries"):
        logger.warn("File "+build_dir+"/include/suid_binaries already exists! Deleting.")
        FileUtils.delete_file(build_dir+"/include/suid_binaries")
    FileUtils.create_file(build_dir+"/include/suid_binaries")
    FileUtils.write_file(path=build_dir+"/include/suid_binaries", content="\n".join(suid_binaries))

    logger.info("Build flatpak")
    Shards.generate_flatpak_manifest(manifest, build_dir)
    Shards.build_flatpak(manifest, build_dir, repo)

    
