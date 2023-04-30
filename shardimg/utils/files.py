# files.py
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


from shardimg.utils.command import Command
from os.path import exists
import os
from shardimg.utils.log import setup_logging
logger=setup_logging()

class FileUtils:

    @staticmethod
    def create_file(
        path: str,
    ):
        if os.environ.get("DEBUG"):
            logger.debug(f"Creating file {path}")
            if os.environ.get("SHARDS_FAKE"):
                return
        file = open(path, 'x')
        file.close()

    @staticmethod
    def append_file(
        path: str,
        content: str,
    ):
        if os.environ.get("DEBUG"):
            logger.debug(f"Appending {content} to file {path}")
            if os.environ.get("SHARDS_FAKE"):
                return
        if not exists(path):
            logger.warn("File "+path+" doesn't exist! Creating file")
            FileUtils.create_file(path)
        with open(path, 'a') as file:
            file.write(content)

    @staticmethod
    def write_file(
        path: str,
        content: str,
    ):
        if os.environ.get("DEBUG"):
            logger.debug(f"Writing {content} to file {path}")
            if os.environ.get("SHARDS_FAKE"):
                return
        if not exists(path):
            logger.warn("File "+path+" doesn't exist! Creating file")
            FileUtils.create_file(path)
        with open(path, 'w') as file:
            file.write(content)

    @staticmethod
    def create_directory(
        path: str,
    ):
        if os.environ.get("DEBUG"):
            logger.debug(f"Creating directory {path}")
            if os.environ.get("SHARDS_FAKE"):
                return
        if not exists(path):
            os.makedirs(path)
        else:
            logger.warn("Directory "+path+" already exists!")

    @staticmethod
    def replace_file(
        path: str,
        search: str,
        replace: str,
    ):
        logger.info(f"Replacing {search} with {replace} in file {path}")
        Command.execute_command(
            command=[
                "sed",
                "-i",
                f"s/{search}/{replace}/g",
                path,
            ],
            command_description="Replacing "+search+" with "+replace+" in file "+path,
            crash=True,
        )

    @staticmethod
    def copy_file(
        source: str,
        destination: str,
        crash: bool = False,
    ):
        logger.info(f"Copying file {source} to {destination}")
        Command.execute_command(
            command=[
                "cp",
                source,
                destination,
            ],
            command_description="Copying file "+source+" to "+destination,
            crash=crash,
        )

    @staticmethod
    def copy_directory(
        source: str,
        destination: str,
        crash: bool = False,
    ):
        logger.info(f"Copying directory {source} to {destination}")
        Command.execute_command(
            command=[
                "cp",
                "-r",
                source,
                destination
            ],
            command_description="Copying directory "+source+" to "+destination,
            crash=crash
        )
