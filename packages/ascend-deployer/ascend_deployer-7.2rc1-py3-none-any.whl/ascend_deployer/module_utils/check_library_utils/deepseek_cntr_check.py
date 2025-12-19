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
import os
import shlex
import subprocess
import threading

# 修改queue模块导入，兼容Python 2.7
try:
    from queue import Queue  # Python 3
except ImportError:
    from Queue import Queue  # Python 2.7

from ansible.module_utils.check_output_manager import check_event
from ansible.module_utils.check_utils import CheckUtil as util
from ansible.module_utils.deepseek_cntr.mindie_service_config import CONFIG_FILE_MAP, SINGLE_NODE, DOUBLE_NODE

BLOCKSIZE = 1024 * 1024 * 100


class DeepseekCntrCheck:

    def __init__(self, module, error_messages):
        self.module = module
        self.worker_num = module.params["worker_num"]
        self.cntr_mnt_path = module.params["cntr_mnt_path"]
        self.weight_mount_path = self.module.params["weight_mount_path"]
        self.model_weight_path = self.module.params["model_weight_path"]
        self.mindie_image_name = self.module.params["mindie_image_name"]
        self.mindie_image_file = self.module.params["mindie_image_file"]
        self.npu_info = module.params["npu_info"]
        self.worker_num = module.params["worker_num"]
        self.master_ip = module.params["master_ip"]
        self.worker_groups = module.params["worker_groups"]
        self.error_messages = error_messages
        self._queue = Queue()

    @check_event
    def check_deepseek_cntr(self):
        self.check_dependency()
        self.check_network()
        self.check_mount_path()
        self.check_image_name_and_file()
        self.check_worker_num_and_master_ip()

    def check_dependency(self):
        if not self.module.get_bin_path("docker"):
            util.record_error("[ASCEND][ERROR] Can not find docker", self.error_messages)

        if not self.module.get_bin_path('npu-smi'):
            util.record_error("[ASCEND][ERROR] Can not find npu-smi.", self.error_messages)

        if not self.module.get_bin_path('hccn_tool'):
            util.record_error("[ASCEND][ERROR] Can not find hccn_tool.", self.error_messages)

    def check_network(self):
        rc, out, err = self.module.run_command("npu-smi info -t topo", check_rc=False)
        if rc != 0:

            util.record_error("[ASCEND][ERROR] Failed to check HCCS status. "
                              "Command 'npu-smi info -t topo' failed with return code {}. "
                              "Error message: {}. "
                              "Please verify npu-smi installation and NPU device accessibility.".format(
                                  rc, err),
                              self.error_messages)
        elif "HCCS" not in out:
            util.record_error("[ASCEND][ERROR] HCCS is not enabled. Please enable HCCS before proceeding.",
                              self.error_messages)

        if self.worker_num == 1:
            return
        find_cmd = "npu-smi info -l"
        _, outputs, _ = self.module.run_command(find_cmd, check_rc=True)
        npu_ids = []
        for line in outputs.split('\n'):
            if "NPU ID" in line:
                npu_ids.append(line.split(":")[-1].strip())
        if not npu_ids:
            util.record_error("[ASCEND][ERROR] Can not find any npu device, using command:{}".format(find_cmd),
                              self.error_messages)
        for npu_id in npu_ids:
            check_cmd = {
                "hccn_tool -i {} -ip -g".format(npu_id): "ipaddr",
            }
            self.run_commands_in_threads(check_cmd)

        # 收集所有错误信息后再统一处理
        error_messages = []
        while not self._queue.empty():
            cmd, msg = self._queue.get()
            error_messages.append("[ASCEND][ERROR] Execute cmd {} failed, {}".format(cmd, msg))

        # 统一记录所有错误
        for error_msg in error_messages:
            util.record_error(error_msg, self.error_messages)

    def run_commands_in_threads(self, commands):
        threads = []
        for cmd, expect_out in commands.items():
            thread = threading.Thread(target=self.run_command, args=(cmd, expect_out))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def run_command(self, cmd, expect_out=None):
        try:
            rc, out, err = self.module.run_command(cmd, check_rc=False)
            output = out + err
            if rc != 0 or (expect_out and expect_out not in output):
                self._queue.put((cmd, output))
        except Exception as e:
            self._queue.put((cmd, str(e)))

    def check_mount_path(self):
        """
        检查是否提供了挂载路径和路径是否实际存在
        """
        paths_to_check = {
            'weight_mount_path': self.weight_mount_path,
            'model_weight_path': self.model_weight_path,
            'cntr_mnt_path': self.cntr_mnt_path
        }

        for path_name, path_value in paths_to_check.items():
            if not path_value:
                util.record_error('[ASCEND][ERROR] Please provide a value for the {} parameter.'.format(path_name),
                                  self.error_messages)

        if not os.path.exists(self.weight_mount_path):
            util.record_error('[ASCEND][ERROR] weight_mount_path: {} is not existed.'.format(self.weight_mount_path),
                              self.error_messages)
            return

        if os.path.islink(self.weight_mount_path):
            util.record_error(
                '[ASCEND][ERROR] The specified weight_mount_path "{}" should not be a symbolic link.'.format(
                    self.weight_mount_path), self.error_messages)
            return
        # 检查 cntr_mnt_path 是否是 model_weight_path 的父目录

        mount_path = os.path.abspath(self.cntr_mnt_path)
        model_path = os.path.abspath(self.model_weight_path)

        # 检查 model_weight_path 是否在 cntr_mnt_path 下, 挂载容器后，从容器内的访问权重的目录
        if not model_path.startswith(mount_path):
            util.record_error(
                '[ASCEND][ERROR] The model_weight_path must be under the cntr_mnt_path directory.',
                self.error_messages)

    def check_image_name_and_file(self):
        # 都未提供时，从resource中自动找
        if not self.mindie_image_name and not self.mindie_image_file:
            return

        # 如果提供了 file 参数，检查文件是否存在且不是软链接
        if self.mindie_image_file:
            if not os.path.exists(self.mindie_image_file):
                util.record_error("[ASCEND][ERROR] The specified mindie_image_file '{}' does not exist.".format(
                    self.mindie_image_file), self.error_messages)

            if os.path.islink(self.mindie_image_file):
                util.record_error(
                    "[ASCEND][ERROR] The specified mindie_image_file '{}' should not be a symbolic link.".format(
                        self.mindie_image_file), self.error_messages)

        if self.mindie_image_name:
            # 检查 mindie_image_name 是否为字符串类型
            if not isinstance(self.mindie_image_name, str):
                util.record_error("[ASCEND][ERROR] The mindie_image_name parameter must be a string, got {}.".format(
                    type(self.mindie_image_name).__name__), self.error_messages)
                return

            # 如果提供了 mindie_image_name，检查是否包含标签
            if ':' not in self.mindie_image_name:
                util.record_error(
                    "[ASCEND][ERROR] The mindie_image_name '{}' must include a tag. "
                    "Valid format example: mindie:dev-2.0.RC1.B091-800I-A2-py311-ubuntu22.04-aarch64".format(
                        self.mindie_image_name), self.error_messages)

            docker_exists = self.module.get_bin_path("docker")
            if not docker_exists:
                util.record_error(
                    "[ASCEND][ERROR] Docker not found. Image '{}' not verified locally.".format(
                        self.mindie_image_name), self.error_messages)
                return
            check_cmd = ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"]

            rc, out, err = self.module.run_command(check_cmd)
            if rc != 0:
                util.record_error(
                    "[ASCEND][ERROR] Failed to list docker images. Command '{}' failed with return code {}. "
                    "Error message: {}".format(" ".join(check_cmd), rc, err.strip()),
                    self.error_messages)
                return
            image_lines = out.splitlines()
            if self.mindie_image_name not in image_lines:
                util.record_error(
                    "[ASCEND][ERROR] mindie_image_name: '{}' not found locally.".format(self.mindie_image_name),
                    self.error_messages)

    def check_worker_num_and_master_ip(self):
        """
        检查 worker_num 和 master_ip 的合法性，基于 CONFIG_FILE_MAP 中定义的支持配置
        """
        # 获取 npu_info 参数
        scene = self.npu_info.get("scene", "")

        # 检查当前 worker_num 是否在 CONFIG_FILE_MAP 的键中（支持的节点数量）
        if self.worker_num not in CONFIG_FILE_MAP:
            util.record_error(
                "[ASCEND][ERROR] Unsupported worker_num: {}. "
                "Supported worker numbers are: {}".format(
                    self.worker_num,
                    list(CONFIG_FILE_MAP.keys())),
                self.error_messages
            )
            return

        # 检查当前场景是否在指定节点数量的支持场景中
        worker_config = CONFIG_FILE_MAP.get(self.worker_num, {})
        if scene not in worker_config:

            util.record_error(
                "[ASCEND][ERROR] For worker_num={}, unsupported scene: {}. "
                "Supported scenes are: {}".format(
                    self.worker_num, scene, list(worker_config.keys())),
                self.error_messages
            )
            return

        # 当 worker_num 为 2 时，检查 master_ip
        if self.worker_num == DOUBLE_NODE:

            # 检查 master_ip 是否填写
            if not self.master_ip:
                util.record_error(
                    "[ASCEND][ERROR] When worker_num > 1 , mindie_master must be provided",
                    self.error_messages
                )
                return

            # 检查 master_ip 是否在 worker_ips 中
            if self.master_ip not in self.worker_groups:
                util.record_error(
                    "[ASCEND][ERROR] mindie_master '{}' must be in worker list {}".format(self.master_ip,
                                                                                          self.worker_groups),
                    self.error_messages
                )
