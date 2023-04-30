# shards.py
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

import yaml
import os
from shardimg.utils.command import Command
from shardimg.utils.files import FileUtils
from shardimg.classes.manifest import Manifest


class Shards:
    @staticmethod
    def install_packages(packages: list, root: str):
        FileUtils.create_directory(root + "/var/lib/pacman")
        FileUtils.copy_file(source="/etc/pacman.conf", destination=root + "/pacman.conf", crash=True)
        Command.execute_command(
            command=[
                        "fakechroot",
                        "fakeroot",
                        "pacman",
                        "--noconfirm",
                        "--root",
                        root,
                        "--dbpath",
                        root + "/var/lib/pacman",
                        "--config",
                        root + "/pacman.conf",
                        "--needed",
                        "-Syu",
                    ] + packages,
            command_description="Installing packages",
            crash=True,
            elevated=False
        )
        Command.execute_command(
            command=[
                        "fakechroot",
                        "fakeroot",
                        "pacman",
                        "--noconfirm",
                        "--root",
                        root,
                        "--dbpath",
                        root + "/var/lib/pacman",
                        "--config",
                        root + "/pacman.conf",
                        "-Scc"
            ],
            command_description="Clearing pacman cache",
            crash=False,
            elevated=False
        )

    @staticmethod
    def execute_commands(commands: list, root):
        for command in commands:
            Command.execute_command(
                command=[
                    "fakechroot",
                    "fakeroot",
                    "chroot",
                    root,
                    "bash",
                    "-c",
                    command,
                ],
                command_description="Run command "+command+" in chroot",
                crash=True
            )

    @staticmethod
    def generate_flatpak_manifest(manifest: Manifest, build_dir: str):
        with open(build_dir + "/" + manifest.name + ".yml", "w") as f:
            yaml.dump({
                "app-id": manifest.id,
                "runtime": "org.freedesktop.Platform",
                "runtime-version": "22.08",
                "sdk": "org.freedesktop.Sdk",
                "modules": [
                    {
                        "name": "root",
                        "buildsystem": "simple",
                        "build-options": {
                            "strip": False,
                            "no-debuginfo": True
                        },
                        "build-commands": [
                            "cp -a root /app/root",
                            "cp -a include/* /app/root/"
                        ],
                        "sources": [
                            {
                                "type": "dir",
                                "path": "./root",
                                "dest": "root"
                            },
                            {
                                "type": "dir",
                                "path": "./include",
                                "dest": "include"
                            },
                        ]
                    }
                ]
            }, f)

    @staticmethod
    def build_flatpak(manifest: Manifest, build_dir: str, repo: str):
        Command.execute_command(
            command=[
                "flatpak-builder",
                "--force-clean",
                "--repo=" + repo,
                build_dir + "/flatbuild",
                build_dir + "/" + manifest.name + ".yml"
            ],
            command_description="Building Flatpak",
            crash=True,
            elevated=False
        )

