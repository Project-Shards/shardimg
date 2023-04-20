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
from shardimg.utils.command import Command
from shardimg.utils.files import FileUtils
from shardimg.classes.manifest import Manifest


class Shards:
    @staticmethod
    def install_packages(packages, root):
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
                        "-Syu",
                        "--needed",
                    ] + packages,
            command_description="Installing packages",
            crash=True,
            elevated=False
        )

    @staticmethod
    def generate_flatpak_manifest(manifest, build_dir):
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
                            "cp -a root /app/root"
                        ],
                        "sources": [
                            {
                                "type": "dir",
                                "path": "./root",
                                "dest": "root"
                            }
                        ]
                    }
                ]
            }, f)

    @staticmethod
    def build_flatpak(manifest, build_dir, repo):
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
