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
import stat
from shardimg.utils.log import setup_logging
logger=setup_logging()

class FileUtils:

    @staticmethod
    def create_file(
        path: str,
    ):
        """
        Creates a file.

        Parameters:
        path (str): The path of the file to create
        """
        if os.environ.get("DEBUG"):
            logger.debug(f"Creating file {path}")
            if os.environ.get("SHARDS_FAKE"):
                return
        file = open(path, 'x')
        file.close()

    @staticmethod
    def delete_file(
        path: str,
        crash: bool = False
    ):
        """
        Deletes a file.

        Parameters:
        path  (str) : The path to the file to delete
        crash (bool): Whether to crash the program if the given file does not exist
        """
        if os.environ.get("DEBUG"):
            logger.debug(f"Deleting file {path}")
            if os.environ.get("SHARDS_FAKE"):
                return
        if os.path.exists(path):
            os.remove(path)
        elif crash:
            logger.error(f"File {path} does not exist!")
            sys.exit(1)
        else:
            logger.warn(f"File {path} does not exist!")

    @staticmethod
    def append_file(
        path: str,
        content: str,
    ):
        """
        Appends content to a file. Creates the specified file if it does not exist

        Parameters:
        path    (str): The path to the file where content should be appended to
        content (str): The content to append
        """
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
        """
        Overwrites a file with given content.
        Creates the specified file if it does not exist

        Parameters:
        path    (str): The path to the file that should be overwritten
        content (str): The content to write
        """
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
        """
        Creates a directory. Does not do anything if the directory already exists.
        If upper directories in the given path do not exist, they will be created too.

        Parameters:
        path (str): The path to create
        """
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
        """
        Searches for a specific string in a file and replaces it with a different
        given string.

        Parameters:
        path    (str): The path of the file to work on.
        search  (str): The string to search for
        replace (str): The string to replace the search string with.
        """
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
        """
        Copies a file.

        Parameters:
        source      (str) : The file source
        destination (str) : Where the file should be copied to
        crash       (bool): Whether the program should crash if the copying failed
        """
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
        """
        Copies a directory.

        Parameters:
        source      (str) : The file source
        destination (str) : Where the file should be copied to
        crash       (bool): Whether the program should crash if the copying failed
        """
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

    @staticmethod
    def is_suid(path: str) -> bool:
        """
        Checks if a file has the suid bit set.

        Parameters:
        path (str): The file to check
        """
        binary = os.stat(path)
        if binary.st_mode & stat.S_ISUID == 2048:
            return True
        return False

    @staticmethod
    def get_symlink(path: str) -> str:
        """
        Checks if a file is a symlink and returns the path it points to if it is.

        Parameters:
        path (str): The path to check

        Returns:
        str: The path the symlink points to. None if the file is not a symlink
        """
        if os.path.islink(path):
            return os.readlink(path)
        else:
            return None
