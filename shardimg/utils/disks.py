# diskutils.py
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
# SPDX-License-Identifier: GPL-3.0

from shardimg.utils.command import Command
from shardimg.utils.log import setup_logging
logger=setup_logging()

class DiskUtils:
    @staticmethod
    def unmount(
        mountpoint: str,
    ):
        """
        Unmounts a mountpoint.

        Parameters:
        mountpoint (str): The mountpoint to unmount
        """
        Command.execute_command(command=["umount", mountpoint], command_description="Unmount "+mountpoint, crash=True, elevated=True)

    @staticmethod
    def bind_mount(
        source: str,
        mountpoint: str,
    ):
        """
        Creates a bind mount.

        Parameters:
        source     (str): The source directory.
        mountpoint (str): The mountpoint where the source should be binded to.
        """
        Command.execute_command(command=["mount", "--bind", source, mountpoint], command_description="Bind mount "+source+" to "+mountpoint, crash=True, elevated=True)

    @staticmethod
    def mount(
        source: str,
        mountpoint: str,
        options: list = [],
        fs: str = None
    ):
        """
        Mounts a device to a given mountpoint.

        Parameters:
        source     (str) : Path to the device to mount
        mountpoint (str) : Mountpoint for the device
        options    (list): Options to add to the mount command (optional)
        fs         (str) : The device type, equivalent to the -t flag in mount (optional)
        """
        command = ["mount"]
        if fs is not None:
            command.extend(["-t", fs])

        if len(options) > 0:
            command.extend(["-o", ",".join(options)])

        command.extend([source, mountpoint])
        print(command)
        Command.execute_command(
            command=command,
            command_description="Mount "+source+" to "+mountpoint+" with options "+" ".join(options),
            crash=True,
            elevated=True
        )

    @staticmethod
    def overlay_mount(
        lowerdirs: list,
        upperdir: str,
        destination: str,
        workdir: str,
        options: list = [],
    ):
        """
        Creates an overlay mount.

        Parameters:
        lowerdirs   (list): The lower directories
        upperdir    (str) : The upper directory
        destination (str) : Where the overlay gets mounted to
        workdir     (str) : Work directory of the overlay mount
        options     (list): Extra options for the mount command (optional)
        """
        command = ["mount", "-t", "overlay", "overlay"]
        if len(options) > 0:
            command.extend(["-o",",".join(options)])
        command.extend(["-o", "lowerdir="+":".join(lowerdirs)+",upperdir="+upperdir+",workdir="+workdir, destination])
        Command.execute_command(command=command, command_description="Mount overlay at "+destination, crash=True, elevated=True)
