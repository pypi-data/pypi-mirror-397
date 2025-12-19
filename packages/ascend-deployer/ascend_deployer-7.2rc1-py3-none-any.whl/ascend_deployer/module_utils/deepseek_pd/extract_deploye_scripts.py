#!/usr/bin/env python3
# coding: utf-8
# Copyright 2024 Huawei Technologies Co., Ltd
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

import fnmatch

import os
import platform
import shutil

from ansible.module_utils.path_manager import TmpPath
from ansible.module_utils import common_info, common_utils


class ExtractMindieDeployer:

    def __init__(self, module):
        self.module = module
        self.resources_dir = os.path.expanduser(module.params["resources_dir"])
        self.arch = platform.machine()
        self.mindie_unzip_path = os.path.join(self.resources_dir, "run_from_mindie")
        self.mindie_service_path = os.path.join(self.mindie_unzip_path, "mindie_service")
        self.mindie_llm_path = os.path.join(self.mindie_unzip_path, "mindie_llm")
        self.mindie_deploy_path = os.path.join(TmpPath.ROOT, "mindie_pd")
        self.messages = []

    def find_package(self, pattern):
        for root, dirs, files in os.walk(self.resources_dir):
            for file in files:
                if fnmatch.fnmatch(file, pattern):
                    return os.path.join(root, file)  # 返回第一个匹配的完整路径
        return None

    def unzip_package(self):
        if os.path.exists(self.mindie_unzip_path):
            shutil.rmtree(self.mindie_unzip_path)
        os.makedirs(self.mindie_unzip_path, mode=0o750)
        mindie_pattern = "Ascend-mindie*linux-{}*.run".format(self.arch)
        mindie_server_pattern = "Ascend-mindie-service*linux-{}*.run".format(self.arch)
        mindie_llm_pattern = "Ascend-mindie-llm*linux-{}*.run".format(self.arch)
        for pattern in [mindie_pattern, mindie_server_pattern, mindie_llm_pattern]:
            package = self.find_package(pattern)
            if not package:
                self.module.fail_json(msg="[ASCEND][ERROR] {} package not found".format(pattern), rc=1, changed=False)
            path = self.mindie_unzip_path
            if pattern == mindie_server_pattern:
                path = self.mindie_service_path
            elif pattern == mindie_llm_pattern:
                path = self.mindie_llm_path

            cmd = "bash {} --extract={}".format(package, path)
            rc, _, _ = self.module.run_command(cmd, check_rc=True)
            if rc != 0:
                self.module.fail_json(msg="[ASCEND][ERROR] extract mindie conf failed", rc=1, changed=False)

        self.create_config_json()

    def create_config_json(self):
        src_config = os.path.join(self.mindie_llm_path, "conf", "config.json")
        if os.path.exists(src_config):
            for config_name in ["config.json", "config_p.json", "config_d.json"]:
                dest_config = os.path.join(self.mindie_service_path, "examples", "kubernetes_deploy_scripts", "conf",
                                           config_name)
                shutil.copy2(src_config, dest_config)

    def extract_conf(self):
        # 创建目标路径
        if os.path.exists(self.mindie_deploy_path):
            shutil.rmtree(self.mindie_deploy_path)
        os.makedirs(self.mindie_deploy_path, mode=0o750)
        src_folder = os.path.join(self.mindie_service_path, 'examples')
        # 将src_folder下的所有文件和文件夹拷贝到目标路径
        if os.path.exists(src_folder):
            for item in os.listdir(src_folder):
                src_path = os.path.join(src_folder, item)
                dest_path = os.path.join(self.mindie_deploy_path, item)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
        else:
            self.module.fail_json(msg="[ASCEND][ERROR] source folder {} not found".format(src_folder), rc=1,
                                  changed=False)

    def run(self):
        self.unzip_package()
        self.extract_conf()
