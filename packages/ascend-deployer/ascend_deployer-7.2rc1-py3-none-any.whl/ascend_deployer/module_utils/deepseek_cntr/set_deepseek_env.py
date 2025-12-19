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

import os
import re
from typing import List, Dict, Tuple

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.deepseek_cntr.mindie_service_config import SINGLE_NODE, DOUBLE_NODE
from ansible.module_utils.path_manager import TmpPath

ENV_FILE_MAP = {
    SINGLE_NODE: {  # single node
        "a910b": "A2_single_machine.sh",
        "a910_93": "A3_single.sh"
    },
    # 双机不支持A3环境
    DOUBLE_NODE: {  # double nodes
        "a910b": "A2_double_machine.sh",
    }
}


class SetDeepseekEnv:
    """
    Initialize SetDeepseekEnv class for configuring DeepSeek environment.
    """
    def __init__(self, module: AnsibleModule, cntr_id: str, master_ip: str, worker_num: int, container_ip: str,
                 npu_info: dict):
        """
        @param module: The AnsibleModule object for executing commands
        @param cntr_id: Container ID where the environment will be configured
        @param master_ip: IP address of the master node
        @param worker_num: Number of worker nodes (SINGLE_NODE or DOUBLE_NODE)
        @param container_ip: IP address of the current container
        @param npu_info: Dictionary containing NPU information, including scene type
        """
        self.module = module
        self.container_id = cntr_id
        self.master_ip = master_ip
        self.worker_num = worker_num
        self.container_ip = container_ip
        self.npu_info = npu_info
        self.env_path_in_container = "{}:/usr/local/Ascend/mindie/latest/mindie-service/scripts/".format(cntr_id)
        self.env_filename = self.select_env_file()
        self.container_env_file = os.path.join(self.env_path_in_container, self.env_filename)
        self.local_path = os.path.join(TmpPath.ROOT, "mindie_service")
        self.local_env_file = os.path.join(self.local_path, self.env_filename)
        self.env_content = []

    def copy_env_from_container(self):
        command = "docker cp {} {}".format(self.container_env_file, self.local_env_file)
        rc, _, err = self.module.run_command(command)
        if rc != 0:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] docker copy env file from container {} to {} failed: {}".format(
                    self.container_env_file, self.local_env_file, err)
            )

    def read_current_env(self):
        if not os.path.exists(self.local_env_file):
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Could not find bashrc: {}, please confirm.".format(self.local_env_file)
            )
        with open(self.local_env_file, "r") as f:
            return f.readlines()

    def copy_env_back(self):
        try:
            with open(self.local_env_file, "w") as f:
                f.writelines(self.env_content)
        except Exception as e:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Write env to file: {} failed: {}".format(self.local_env_file, str(e))
            )
        command = "docker cp {} {}".format(self.local_env_file, self.container_env_file)
        rc, _, err = self.module.run_command(command)
        if rc != 0:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] docker copy env file {} to {} failed: {}".format(
                    self.local_env_file, self.container_env_file, err)
            )

    def select_env_file(self):
        scene = self.npu_info.get("scene") if isinstance(self.npu_info, dict) else None
        worker_env = ENV_FILE_MAP.get(self.worker_num, {})
        env_filename = worker_env.get(scene)

        if env_filename:
            return env_filename
        else:
            return self.module.fail_json(changed=False, rc=1,
                                         msg=f"[ASCEND][ERROR] No env file found for worker_num={self.worker_num},"
                                             f" scene={scene}")

    def ensure_source_commands(self):
        """确保必要的环境变量source命令存在"""
        required_sources = [
            'source /usr/local/Ascend/mindie/set_env.sh',
            'source /usr/local/Ascend/ascend-toolkit/set_env.sh',
            'source /usr/local/Ascend/nnal/atb/set_env.sh',
            'source /usr/local/Ascend/atb-models/set_env.sh'
        ]

        # 检查每个必需的source命令是否已存在
        for source_cmd in required_sources:
            # 检查是否已存在该source命令，去除行尾的换行符进行比较
            exists = any(source_cmd.strip() in line.strip() for line in self.env_content)
            if not exists:
                # 如果不存在，则添加到文件开头，加上换行符
                self.env_content.insert(2, source_cmd + '\n')

    def modify_env(self):
        self.env_content = self.read_current_env()
        self.export_jemalloc()
        if self.npu_info.get("scene") == "a910b":
            self.ensure_source_commands()
            if self.worker_num == DOUBLE_NODE:
                # 修改RANK_TABLE_FILE, MIES_CONTAINER_IP, MASTER_IP环境变量
                rank_table_path = "/usr/local/Ascend/mindie/latest/mindie-service/rank_table_file.json"
                for i, line in enumerate(self.env_content):
                    if 'export RANK_TABLE_FILE=' in line or 'RANK_TABLE_FILE=' in line:
                        self.env_content[i] = f'export RANK_TABLE_FILE="{rank_table_path}"\n'
                    elif 'export MIES_CONTAINER_IP=' in line or 'MIES_CONTAINER_IP=' in line:
                        self.env_content[i] = f'export MIES_CONTAINER_IP={self.container_ip}\n'
                    elif 'export MASTER_IP=' in line or 'MASTER_IP=' in line:
                        self.env_content[i] = f'export MASTER_IP={self.master_ip}\n'
                    # 批量替换chmod命令中的旧路径
                    elif 'chmod -R 640 "ranktable_file_path/hccl_2s_16p.json"' in line:
                        self.env_content[i] = line.replace('"ranktable_file_path/hccl_2s_16p.json"',
                                                           f'"{rank_table_path}"')

    def export_jemalloc(self):
        pattern = r'export LD_PRELOAD="[^"]{0,256}libjemalloc\.so[^"]{0,256}:(\$LD_PRELOAD)"'

        for i, line in enumerate(self.env_content):
            if re.search(pattern, line):
                self.env_content[i] = 'export LD_PRELOAD="/usr/lib64/libjemalloc.so.2:$LD_PRELOAD"\n'
                return

    def execute(self):
        self.copy_env_from_container()
        self.modify_env()
        self.copy_env_back()
        return self.container_env_file.split(":")[-1]
