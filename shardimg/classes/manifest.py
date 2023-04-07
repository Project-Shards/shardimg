# manifest.py
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
import json

class Manifest:

    name: str
    version: str
    type: str
    base: str
    author: str
    packages: list
    commands: list

    def __init__(self, manifest):
        self.manifest_path = manifest
        self.parse_manifest(self.manifest_path)


    def parse_manifest(self, manifest):
        with open(manifest) as f:
            data = json.load(f)
        self.name = data["name"]
        self.version = data["version"]
        self.type = data["type"]
        self.base = data["base"]
        self.author = data["author"]
        self.packages = data["packages"]
        self.commands = data["commands"]