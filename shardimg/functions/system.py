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

from shardimg.classes.manifest import Manifest
from shardimg.utils.files import FileUtils
from shardimg.utils.command import Command
from shardimg.utils.log import setup_logging
setup_logging()

def build_system_image(
        manifest: Manifest,
        build_dir: str,
):
    FileUtils.create_directory(build_dir)
    generate_containerfile(manifest, build_dir)
    out = Command.execute_command(
        [
            "podman",
            "build",
            "-t",
            "shards/"+manifest.name.lower()+":"+manifest.version,
            "."
        ],
        workdir=build_dir,
        crash=True
    )
    if out[0] != 0:
        print("Error building image")
        exit(1)

def generate_containerfile(
        manifest: Manifest,
        build_dir: str,
):
    FileUtils.create_file(build_dir + "/Containerfile")
    FileUtils.append_file(build_dir + "/Containerfile", "FROM archlinux:latest\n")
    FileUtils.append_file(build_dir + "/Containerfile", "LABEL maintainer=\""+manifest.author+"\"\n")
    FileUtils.append_file(build_dir + "/Containerfile", "LABEL org.opencontainers.image.title=\""+manifest.name+"\"\n")
    FileUtils.append_file(build_dir + "/Containerfile", "LABEL org.opencontainers.image.version=\""+manifest.version+"\"\n")
    FileUtils.append_file(build_dir + "/Containerfile", "RUN pacman -Syu --noconfirm\n")
    FileUtils.append_file(build_dir + "/Containerfile", "RUN pacman -S --noconfirm "+" ".join(manifest.packages)+"\n")
    FileUtils.append_file(build_dir + "/Containerfile", "RUN pacman -Scc --noconfirm\n")
    FileUtils.append_file(build_dir + "/Containerfile", "RUN rm -rf /var/cache/pacman/pkg/*\n")
    for i in manifest.commands:
        FileUtils.append_file(build_dir + "/Containerfile", "RUN "+i+"\n")

