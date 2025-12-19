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
import platform

from ansible.module_utils import common_utils


class LoadMindIeImage:
    """
    A class to load MindIE docker images for DeepSeek deployment.

    This class provides functionality to load MindIE images either by name or from tar files,
    supporting both docker and containerd (ctr) container runtimes.
    """

    _card_scene_map = {"a910b": "800i-a2", "a910_93": "800i-a3"}

    def __init__(self, mindie_image_name, mindie_image_file, module, npu_info, error_messages):
        """
        Initialize LoadMindIeImage with image and environment information.

        @param mindie_image_name: Name of the MindIE docker image to use
        @param mindie_image_file: Path to the MindIE image tar file
        @param module: The AnsibleModule object for executing commands
        @param npu_info: Dictionary containing NPU information, including scene type
        @param error_messages: List of error messages for collecting errors during image loading
        """
        self.mindie_image_name = mindie_image_name
        self.mindie_image_file = mindie_image_file
        self.module = module
        self.arch = platform.machine()
        self.npu_info = npu_info
        self.container_runtime_type = module.params.get('container_runtime_type', {})
        self.resources_dir = os.path.expanduser(module.params["resources_dir"])
        self.error_messages = error_messages or []

    def load(self):
        if self.mindie_image_name:
            return self.mindie_image_name
        elif self.query_container_runtime_type() == "containerd":
            return self.ctr_mindie_image()
        elif self.query_container_runtime_type() == "docker":
            return self.docker_mindie_image()
        else:
            self.error_messages.append("[ASCEND][ERROR] load mindie image file failed")
            return self.module.fail_json(msg="\n".join(self.error_messages), rc=1, changed=False)

    def ctr_load_mindie_image_file(self, mindie_image_file):
        # 使用 ctr 加载镜像
        _, out, _ = self.module.run_command("nerdctl -n k8s.io load -i {}".format(mindie_image_file), check_rc=True)
        for line in out.splitlines():
            if 'Loaded image:' in line:
                return line.split()[-1]
        self.error_messages.append(
            "[ASCEND][ERROR] Load mindie_image_file {} failed.".format(mindie_image_file))
        return self.module.fail_json(msg="\n".join(self.error_messages), rc=1, changed=False)

    def docker_load_mindie_image_file(self, mindie_image_file):
        _, out, _ = self.module.run_command("docker load -i {}".format(mindie_image_file), check_rc=True)
        for line in out.splitlines():
            if 'Loaded image:' in line:
                return line.split()[-1]
        self.error_messages.append(
            "[ASCEND][ERROR] Load mindie_image_file {} failed.".format(mindie_image_file))
        return self.module.fail_json(msg="\n".join(self.error_messages), rc=1, changed=False)

    def ctr_mindie_image(self):
        image_file_path = self._find_mindie_pkg()
        if image_file_path:
            # 使用 ctr 加载镜像
            return self.ctr_load_mindie_image_file(image_file_path)

        self.error_messages.append(
            "[ASCEND][ERROR] Please provide mindie image file")
        return self.module.fail_json(msg="\n".join(self.error_messages), rc=1, changed=False)

    def docker_mindie_image(self):
        image_file_path = self._find_mindie_pkg()
        if image_file_path:
            return self.docker_load_mindie_image_file(image_file_path)

        self.error_messages.append(
            "[ASCEND][ERROR] Please provide mindie image file")
        return self.module.fail_json(msg="\n".join(self.error_messages), rc=1, changed=False)

    def _find_mindie_pkg(self):
        if self.mindie_image_file:
            image_file_path = self.mindie_image_file
        else:
            scene_pattern = self._card_scene_map.get(self.npu_info.get("scene", ""), "")

            mindie_pattern = "*mindie*{}*{}*.tar.gz".format( scene_pattern, self.arch)
            pkgs, _ = common_utils.find_files(os.path.join(self.resources_dir, "MindIE-image*"), mindie_pattern)
            if not pkgs:
                self.error_messages.append(
                    "[ASCEND][ERROR] Can not find mindie image file")
                return self.module.fail_json(msg="\n".join(self.error_messages), rc=1, changed=False)
            image_file_path = pkgs[0]
        return image_file_path

    def query_container_runtime_type(self):
        # 检查 container_runtime_type 是否存在
        if not self.container_runtime_type:
            return self.module.fail_json(msg="[ASCEND][ERROR] container_runtime_type is not properly configured")

        # 检查字典是否为空
        if len(self.container_runtime_type) == 0:
            return self.module.fail_json(msg="[ASCEND][ERROR] container_runtime_type is empty")

        value_list = list(self.container_runtime_type.values())
        if 'docker' in value_list[0]:
            return 'docker'
        elif 'containerd' in value_list[0]:
            return 'containerd'
        else:
            return self.module.fail_json(msg="[ASCEND][ERROR] unknown container type")

