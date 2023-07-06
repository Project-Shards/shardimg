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
    print(os.path.abspath(manifest_path))
    FileUtils.create_directory(build_dir)
    FileUtils.create_directory(build_dir+"/buildroot")
    FileUtils.create_directory(build_dir + "/buildroot/proc")
    FileUtils.create_directory(build_dir + "/buildroot/sys")
    FileUtils.create_directory(build_dir + "/buildroot/dev")
    FileUtils.create_directory(build_dir+"/root")
    FileUtils.create_directory(build_dir+"/include")

    FileUtils.copy_file(manifest_path, build_dir+"/include/manifest.json", True)

    logger.info(f"Mount proc, sys and dev in {build_dir}/buildroot")
    DiskUtils.mount(source="/proc", mountpoint=build_dir + "/buildroot/proc", fs="proc")
    DiskUtils.mount(source="/sys", mountpoint=build_dir + "/buildroot/sys", fs="sysfs")
    DiskUtils.mount(source="/dev", mountpoint=build_dir + "/buildroot/dev", options=["bind"])

    packages=["base", "dracut", "btrfs-progs", "busybox", "lvm2", "dmraid", "mdadm", "tpm2-tss", "dash", "binutils", "elfutils", manifest.kernelpackage, "linux-firmware"]

    Shards.install_packages(packages, build_dir+"/buildroot")
    Shards.execute_commands(manifest.commands, build_dir+"/buildroot")

    Shards.execute_commands([f'dracut --no-hostonly-cmdline --no-hostonly --uefi --kver {manifest.kernelversion} /{manifest.kernelname}.unsigned.efi'], build_dir+"/buildroot")

    Command.execute_command(
        command=[
            "chown",
            os.getenv("USER"),
            f"{build_dir}/buildroot/{manifest.kernelname}.unsigned.efi",
        ],
        command_description="Correct permissions for kernel efi",
        crash=True,
        elevated=True
    )

    FileUtils.copy_file(build_dir+f"/buildroot/{manifest.kernelname}.unsigned.efi", build_dir+f"/root/{manifest.kernelname}.unsigned.efi")

    logger.info("Unmounting proc, sys and dev")
    DiskUtils.unmount(mountpoint=build_dir + "/buildroot/proc")
    DiskUtils.unmount(mountpoint=build_dir + "/buildroot/sys")
    DiskUtils.unmount(mountpoint=build_dir + "/buildroot/dev")

    Shards.generate_flatpak_manifest(manifest, build_dir)
    Shards.build_flatpak(manifest, build_dir, repo)

    
