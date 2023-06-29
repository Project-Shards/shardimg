# command.py
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
import subprocess
import os
import sys
from shardimg.utils.log import setup_logging
logger=setup_logging()

class Command:
    @staticmethod
    def execute_command(
        command: list,
        command_description: str = "",
        crash: bool = False,
        workdir: str = "",
        elevated: bool = False,
        capture: bool = False,
    ) -> [str, str, str]:
        """
        Executes a given command and optionally captures the output.

        Parameters:
        command             (list): The command to run, each parameter is a seperate object in the list
        command_description (str) : A description of what the command does (optional)
        crash               (bool): Whether the system should crash if the command fails. Defaults to False if not specified
        workdir             (str) : In what directory the command should run. Runs in the current cwd if not specified
        elevated            (bool): Whether the command should be run as the root user. Defaults to False if not specified
        capture             (bool): Whether the command output should be captured. Defaults to False if not specified.

        Returns:
        [str, str, str]: A list containing the returncode, stdout and stderr
        """
        if os.environ.get("DEBUG"):
            logger.debug("Command: " + " ".join(command))
            if os.environ.get("SHARDS_FAKE"):
                return [0, "", ""]

        rootcommand = ["sudo"] + command
        out = subprocess.run(
            rootcommand if elevated else command,
            capture_output=capture,
            cwd=workdir if workdir.strip() != "" else None
        )
        if out.returncode != 0 and command_description.strip() != "":
            logger.error(command_description+" failed with returncode "+str(out.returncode))
            if crash:
                sys.exit(out.returncode)
        elif out.returncode != 0:
            logger.error(" ".join(command)+" failed with returncode "+str(out.returncode))
            if crash:
                sys.exit(out.returncode)

        return [out.returncode, out.stdout, out.stderr]

    @staticmethod
    def execute_chroot(
            command: list,
            command_description: str = "",
            crash: bool = False,
            root: str = "/mnt"
    ) -> [str, str, str]:
        """
        Executes a given command in a chroot.

        Parameters:
        command             (list): The command to run, each parameter is a seperate object in the list
        command_description (str) : A description of what the command does (optional)
        crash               (bool): Whether the system should crash if the command fails. Defaults to False if not specified
        root                (str) : The root that chroot should switch to.

        Returns:
        [str, str, str]: A list containing the returncode, stdout and stderr
        """
        chroot_command = ["arch-chroot", root]
        chroot_command.extend(command)
        return Command.execute_command(
            command=chroot_command,
            command_description=command_description,
            crash=crash,
            elevated=True
        )
