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
import hashlib
import sys

from shardimg.classes.manifest import Manifest
from shardimg.utils.files import FileUtils
from shardimg.utils.shards import Shards
from shardimg.utils.disks import DiskUtils
from shardimg.utils.command import Command
from shardimg.utils.log import setup_logging

logger = setup_logging()


class SystemImage:

    @staticmethod
    def build_system_image(
            manifest: Manifest,
            build_dir: str,
            repo: str,
            manifest_path: str,
            fsguard_enabled: bool = True,
            fsguard_paths: list = ["usr"],
            fsguard_binary: str = "/usr/bin/FsGuard"
    ):
        """
        Builds a flatpak system image based on the passed manifest.

        Parameters:
        manifest (Manifest): The parsed manifest containing all required data
        build_dir (str): The build directory
        repo (str): Path to the repo that the final flatpak will be added to
        manifest_path (str): Path to the original manifest
        fsguard_enabled (bool): Whether FsGuard is enabled in the image
        fsguard_paths (list): Paths that should be added to the FsGuard file list. Defaults to usr if not specified
        fsguard_binary (str): Path to the FsGuard binary in the image. Defaults to "/usr/bin/FsGuard" if not specified
        """
        include_dir = os.path.abspath(manifest_path).split("/")
        include_dir.pop()
        include_dir.append("include")
        include_dir = "/".join(include_dir)

        modules_dir = os.path.abspath(manifest_path).split("/")
        modules_dir.pop()
        modules_dir.append("modules")
        modules_dir = "/".join(modules_dir)

        if manifest.base.strip() != "":
            logger.info(f"Pulling base image")
            Shards.initialize_base_image(
                base=manifest.base,
                build_dir=build_dir
            )
        else:
            logger.info(f"Populate build directory {build_dir}")
            FileUtils.create_directory(build_dir)
            FileUtils.create_directory(build_dir + "/root")
            FileUtils.create_directory(build_dir + "/root/proc")
            FileUtils.create_directory(build_dir + "/root/sys")
            FileUtils.create_directory(build_dir + "/root/dev")

        logger.info("Add manifest.json to include")
        FileUtils.copy_file(manifest_path, build_dir + "/manifest", False)
        FileUtils.create_directory(build_dir + "/include")
        FileUtils.copy_directory(include_dir, build_dir, False)
        FileUtils.copy_file(manifest_path, build_dir + "/include/manifest.json", True)

        FileUtils.create_directory(build_dir + "/modules")
        FileUtils.copy_directory(modules_dir, build_dir, False)

        logger.info(f"Mount proc, sys and dev in {build_dir}/root")
        DiskUtils.mount(source="/proc", mountpoint=build_dir + "/root/proc", fs="proc")
        DiskUtils.mount(source="/sys", mountpoint=build_dir + "/root/sys", fs="sysfs")
        DiskUtils.mount(source="/dev", mountpoint=build_dir + "/root/dev", options=["bind"])

        logger.info("Installing packages")
        Shards.install_packages(manifest.packages, build_dir + "/root")
        logger.info("Executing commands")
        Shards.execute_commands(manifest.commands, build_dir + "/root")

        logger.info("Unmounting proc, sys and dev")
        DiskUtils.unmount(mountpoint=build_dir + "/root/proc")
        DiskUtils.unmount(mountpoint=build_dir + "/root/sys")
        DiskUtils.unmount(mountpoint=build_dir + "/root/dev")

        SystemImage.fsGuard_setup(fsguard_paths=fsguard_paths, build_dir=build_dir, fsguard_binary=fsguard_binary)

        logger.info("Build flatpak")
        Shards.generate_flatpak_manifest(manifest, build_dir)
        Shards.build_flatpak(manifest, build_dir, repo)

    @staticmethod
    def fsGuard_setup(fsguard_paths: list, build_dir: str, fsguard_binary: str):
        """
        Generates the FsGuard filelist and adds the signature to FsGuard

        Args:
            fsguard_paths (str): The Paths to generate checksums for
            build_dir (str): Build directory of the image
            fsguard_binary (str): Path to the FsGuard binary

        Returns:

        """
        logger.info("Creating FsGuard file list")
        suid_binaries = []
        for path in fsguard_paths:
            for (dirpath, dirname, filenames) in os.walk(build_dir + "/root/" + path):

                for file in filenames:
                    if not fsguard_binary.strip() in dirpath + "/" + file:
                        filepath = dirpath + "/" + file
                        filepath = os.path.abspath(
                            dirpath + "/" + FileUtils.get_symlink(filepath)) if FileUtils.get_symlink(
                            filepath) is not None else filepath
                        if not os.path.isfile(filepath):
                            filepath = build_dir + "/root" + os.path.abspath(
                                FileUtils.get_symlink(dirpath + "/" + file))
                        suid = False
                        if FileUtils.is_suid(filepath):
                            suid = True
                        suid_binaries.append("{} {} {}".format(
                            filepath.replace(os.path.abspath(build_dir + "/root"), "").replace(build_dir + "/root", ""),
                            Shards.fsguard_checksum(filepath),
                            "true" if suid else "false")
                        )
                        print("{} {} {}".format(
                            filepath.replace(os.path.abspath(build_dir + "/root"), "").replace(build_dir + "/root", ""),
                            Shards.fsguard_checksum(filepath),
                            "true" if suid else "false")
                        )

        logger.info("Writing fsguard checksums to file")
        if os.path.exists(build_dir + "/include/FsGuard/filelist"):
            logger.warn("File " + build_dir + "/include/suid_binaries already exists! Deleting.")
            FileUtils.delete_directory(build_dir + "/include/FsGuard")
        FileUtils.create_directory(build_dir + "/include/FsGuard")
        FileUtils.create_file(build_dir + "/include/FsGuard/filelist")
        FileUtils.write_file(path=build_dir + "/include/FsGuard/filelist", content="\n".join(suid_binaries))

        if not os.path.exists(os.getenv("HOME")+"/.minisign/minisign.pub"):
            logger.error(f"Minisign public key not found! {os.getenv('HOME')}/.minisign/minisign.pub: No such file "
                         f"or directory")
            sys.exit(1)

        Command.execute_command(
            command=[
                "bash",
                "-c",
                "echo | minisign -Sm"+build_dir+"/include/FsGuard/filelist -x "+build_dir+"/filelist.minisig"
            ],
            crash=True
        )
        signature = "----begin attach----"
        with open(build_dir+"/filelist.minisig", "r") as minisig:
            signature = signature+minisig.read()
        signature = signature+"----begin second attach----"
        with open(os.getenv("HOME")+"/.minisign/minisign.pub", "r") as pubkey:
            signature = signature+pubkey.read().split("\n")[1].strip("\n")

        FileUtils.append_file(path=build_dir+"/root"+fsguard_binary, content=signature)
