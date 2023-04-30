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
from shardimg.utils.files import FileUtils
from shardimg.classes.manifest import Manifest


def initialize_directory(directory: str, name: str, id: str, version: str, author: str, type: str, base: str):
    if not os.path.exists(directory):
        FileUtils.create_directory(directory)
    manifest = Manifest(
        name=name,
        id=id,
        version=version,
        type=type,
        base=base,
        author=author,
    )
    manifest.write_manifest(directory+"/manifest.json")
