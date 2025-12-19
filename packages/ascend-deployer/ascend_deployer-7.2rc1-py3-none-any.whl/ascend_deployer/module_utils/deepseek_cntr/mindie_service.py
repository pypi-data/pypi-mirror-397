#!/usr/bin/env python3
# coding: utf-8
# Copyright 2025 Huawei Technologies Co., Ltd
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
import os.path
import time
from datetime import datetime

from ansible.module_utils.basic import AnsibleModule


class MindIeService:
    """
    A class to manage and control MindIE service in a container.

    This class provides functionality to start and monitor MindIE service,
    including NUMA node configuration and environment setup.
    """

    _DOCKER_EXEC = "docker exec -d {} {} sh -c '{}'"

    def __init__(self, module: AnsibleModule, cntr_id: str, env_file: str, worker_num: int, npu_info: dict):
        """
        Initialize MindIeService with container and environment information.

        @param module: AnsibleModule instance for executing commands
        @param cntr_id: Container ID where the MindIE service will run
        @param env_file: Environment file path to be sourced before starting service
        @param worker_num: Number of worker nodes in the deployment
        @param npu_info: Dictionary containing NPU information and configuration
        """
        self.module = module
        self.cntr_id = cntr_id
        self.env_file = env_file
        self.worker_num = worker_num
        self.npu_info = npu_info
        self.numa_node = self.get_numa_node()
        self.need_setpgrp = 'setsid' if self.npu_info.get("scene") == "a910b" else ''

    def check_server_state(self, cntr_id: str):
        command = "ps aux  | grep -v grep | grep mindieservice_daemon > /dev/null"
        rc, _, _ = self.module.run_command(self._DOCKER_EXEC.format(cntr_id, self.need_setpgrp, command))
        if rc != 0:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] {} Start mindieservice failed:, please check log"
                    " in container".format(cntr_id)
            )

    def get_numa_node(self):
        # 获取numa node0的cpu信息
        rc, out, err = self.module.run_command("lscpu")

        if rc != 0:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Failed to get NUMA information, error: {}".format(err)
            )

        # 查找 NUMA node0 的 CPU 信息
        numa_lines = out.strip().split('\n')

        for line in numa_lines:
            if 'NUMA node0 CPU(s):' in line:
                return line.split(':')[-1].strip()

        return self.module.fail_json(changed=False, rc=1, msg="[ASCEND][ERROR] NUMA node0 information not found.")

    def start_service(self):
        # start master node first then sub node.
        target_path = "/usr/local/Ascend/mindie/latest/mindie-service/"
        command = "source {} && taskset -c {} {}bin/mindieservice_daemon  > /dev/null 2>&1".format(self.env_file,
                                                                                                   self.numa_node,
                                                                                                   target_path)

        rc, _, err = self.module.run_command(self._DOCKER_EXEC.format(self.cntr_id, self.need_setpgrp, command))
        if rc != 0:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Start mindie server failed: {}".format(err)
            )
        # wait 10s, then check the server whether normal or not
        time.sleep(60)
        self.check_server_state(self.cntr_id)
