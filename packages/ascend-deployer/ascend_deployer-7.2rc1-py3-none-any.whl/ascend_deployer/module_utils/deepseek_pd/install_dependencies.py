#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Huawei Technologies Co., Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ===========================================================================
import os

from ansible.module_utils import common_info
from ansible.module_utils.common_utils import compare_version


class DependenciesInstaller:

    def __init__(self, module):
        self.module = module
        self.resources_dir = os.path.expanduser(self.module.params["resources_dir"])
        self.python_tar = self.module.params["python_tar"]
        self.python_version = self.python_tar.replace("P", "p").replace("-", "")
        self.pip_install_option = ""
        self.local_path = common_info.get_local_path(os.getuid(), os.path.expanduser("~"))
        os.environ["PATH"] = "{}/{}/bin:".format(self.local_path, self.python_version) + os.environ["PATH"]
        os.environ["LD_LIBRARY_PATH"] = "{}/{}/lib".format(self.local_path, self.python_version)

    def install_packages(self):
        packages = ['ruamel.yaml', 'ruamel.yaml.clib', 'PyYAML==6.0.1']

        for package in packages:
            install_package_cmd = "python3 -m pip install {} --no-index --find-links {}/pylibs/{} {}".format(
                package, self.resources_dir, '.'.join(self.python_version.split('.')[:2]), self.pip_install_option
            )
            rc, out, err = self.module.run_command(install_package_cmd)

            if rc != 0:
                self.module.fail_json(
                    msg="[ASCEND][ERROR] python libs {} is installed failed: {}".format(package, err),
                    rc=1, changed=False)

    def run(self):
        self.install_packages()
