# desktop.py
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
import random, string
setup_logging()

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def build_desktop_image(
        manifest: Manifest,
        build_dir: str
):
    system_container_name=randomword(10)
    FileUtils.create_directory(build_dir)
    #get_system_rootfs(build_dir, system_container_name)
    get_image_rootfs(
        build_dir=build_dir,
        container=randomword(10),
        image="archlinux:latest", # TODO: Replace with crystal registry
        name="system"
    )
    create_desktop_overlay(
        build_dir=build_dir,
        base=manifest.base
    )
    install_packages(
        root_dir=build_dir+"/root",
        packages=manifest.packages
    )
    DiskUtils.unmount(build_dir+"/root")
    generate_containerfile(
        manifest=manifest,
        build_dir=build_dir
    )
    Command.execute_command(
        [
            "rm",
            "-rf",
            build_dir+"/desktop/var/cache/pacman/pkg/*"
        ],
        command_description="Remove pacman cache",
        crash=False,
        workdir=build_dir,
    )
    Command.execute_command(
        [
            "podman",
            "build",
            "-t",
            "shards/" + manifest.name.lower() + ":" + manifest.version,
            "."
        ],
        workdir=build_dir,
        crash=True,
        elevated=True
    )



def get_image_rootfs(build_dir: str, container: str, image: str, name: str):
    Command.execute_command(
        command=[
            "podman",
            "pull",
            image
        ],
        command_description="Pull "+image,
        crash=True,
        workdir=build_dir,
        elevated=False
    )
    FileUtils.create_directory(build_dir+"/system")
    Command.execute_command(
        command=[
            "podman",
            "create",
            "--name="+container,
            image
        ],
        command_description="Create temporary container using "+image,
        crash=True,
        workdir=build_dir,
        elevated=False
    )
    Command.execute_command(
        command=[
            "podman",
            "export",
            container,
            "-o",
            name+".tar"
        ],
        command_description="Get container rootfs",
        crash=True,
        workdir=build_dir+"/"+name,
        elevated=False
    )
    Command.execute_command(
        command=[
            "tar",
            "xvf",
            name+".tar"
        ],
        command_description="Extract "+image+" rootfs",
        crash=True,
        workdir=build_dir+"/"+name,
        elevated=False
    )

def create_desktop_overlay(build_dir: str, base: str):
    FileUtils.create_directory(build_dir+"/workdir")
    FileUtils.create_directory(build_dir+"/root")
    if base.strip() == "":
        FileUtils.create_directory(build_dir+"/desktop")
    else:
        get_image_rootfs(
            build_dir=build_dir,
            container=randomword(10),
            image=base,
            name="desktop"
        )

    DiskUtils.overlay_mount(
        lowerdirs=[build_dir+"/system"],
        upperdir=build_dir+"/desktop",
        workdir=build_dir+"/workdir",
        destination=build_dir+"/root"
    )


def install_packages(root_dir: str, packages: list):
    Command.execute_command(
        command=[
            "pacstrap",
            root_dir,
        ]+packages,
        command_description="Install packages into root",
        crash=True,
        elevated=True
    )

def generate_containerfile(
        manifest: Manifest,
        build_dir: str,
):
    FileUtils.create_file(build_dir + "/Containerfile")
    FileUtils.append_file(build_dir + "/Containerfile", "FROM scratch\n")
    FileUtils.append_file(build_dir + "/Containerfile", "LABEL maintainer=\""+manifest.author+"\"\n")
    FileUtils.append_file(build_dir + "/Containerfile", "LABEL org.opencontainers.image.title=\""+manifest.name+"\"\n")
    FileUtils.append_file(build_dir + "/Containerfile", "LABEL org.opencontainers.image.version=\""+manifest.version+"\"\n")
    FileUtils.append_file(build_dir + "/Containerfile", "COPY desktop/ /\n")
    for i in manifest.commands:
        FileUtils.append_file(build_dir + "/Containerfile", "RUN "+i+"\n")
