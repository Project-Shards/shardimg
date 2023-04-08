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
        Command.execute_command(command=["umount", mountpoint], command_description="Unmount "+mountpoint, crash=True, elevated=True)


    @staticmethod
    def overlay_mount(
        lowerdirs: list,
        upperdir: str,
        destination: str,
        workdir: str,
        options: list = [],
    ):
        command = ["mount", "-t", "overlay", "overlay"]
        if len(options) > 0:
            command.extend(["-o",",".join(options)])
        command.extend(["-o", "lowerdir="+":".join(lowerdirs)+",upperdir="+upperdir+",workdir="+workdir, destination])
        Command.execute_command(command=command, command_description="Mount overlay at "+destination, crash=True, elevated=True)
