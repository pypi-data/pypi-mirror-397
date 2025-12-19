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

import json
import os
import platform
import re
import subprocess

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.path_manager import TmpPath, ParameterTypes
from ansible.module_utils.deepseek_cntr.hccn_tool_client import HostHccnToolClient
from ansible.module_utils.deepseek_pd.load_mindie_image import LoadMindIeImage
from ansible.module_utils.deepseek_cntr.mindie_service_config import MindIEServiceConfig, SINGLE_NODE, DOUBLE_NODE
from ansible.module_utils.deepseek_cntr.set_deepseek_env import SetDeepseekEnv
from ansible.module_utils.utils import JsonDict

from ansible.module_utils.deepseek_cntr.cntr_manager import CntrManager

from ansible.module_utils.deepseek_cntr.mindie_service import MindIeService


class ServerEntry(JsonDict):

    def __init__(self, device, server_id, container_ip, host_nic_ip="reserve"):
        self.device = device or []
        self.server_id = server_id
        self.container_ip = container_ip
        self.host_nic_ip = host_nic_ip


class DeepseekCntrInstaller:
    _card_model_map = {"Atlas 800I A2": "800i-a2", "A900T": "800i-a2", "A300i-duo": "300i-duo"}
    _INSTALL_ACTION = "install"
    _COLLECT_ACTION = "collect"

    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                action=dict(type=ParameterTypes.STR, required=False),
                worker_num=dict(type=ParameterTypes.INT, required=False),
                model_name=dict(type=ParameterTypes.STR, required=False),
                model_weight_path=dict(type=ParameterTypes.STR, required=False),
                weight_mount_path=dict(type=ParameterTypes.STR, required=False),
                cntr_mnt_path=dict(type=ParameterTypes.STR, required=False),
                mindie_image_name=dict(type=ParameterTypes.STR, required=False),
                mindie_image_file=dict(type=ParameterTypes.STR, required=False),
                resources_dir=dict(type=ParameterTypes.STR, required=False),
                npu_info=dict(type=ParameterTypes.DICT, required=False),
                davinci_devices=dict(type=ParameterTypes.LIST, required=False),
                master_ip=dict(type=ParameterTypes.STR, required=False),
                node_ip=dict(type=ParameterTypes.STR, required=False),
                all_server_entry=dict(type=ParameterTypes.LIST, required=False),
            )
        )
        self.action = self.module.params["action"]
        self.worker_num = self.module.params["worker_num"]
        self.model_name = self.module.params["model_name"]
        self.model_weight_path = self.module.params["model_weight_path"]
        self.weight_mount_path = self.module.params["weight_mount_path"]
        self.cntr_mnt_path = self.module.params["cntr_mnt_path"]
        self.npu_info = self.module.params["npu_info"]
        self.messages = []
        self.mindie_image_name = self.module.params["mindie_image_name"]
        self.mindie_image_file = self.module.params["mindie_image_file"]
        self.mnt_davinci_devices = self.get_mnt_davinci_device(self.module.params["davinci_devices"])
        self.master_ip = self.module.params["master_ip"]
        self.node_ip = self.module.params["node_ip"]
        self.card = self.npu_info["card"]
        self.arch = platform.machine()
        self.all_server_entry = self.module.params.get("all_server_entry", [])
        self.facts = dict()
        self.deepseek_tmp_path = os.path.join(TmpPath.ROOT, "deepseek")
        self.cntr_mng = None
        if not os.path.exists(self.deepseek_tmp_path):
            os.makedirs(self.deepseek_tmp_path, mode=0o750)

    def get_mnt_davinci_device(self, need_mnt_davinci_device_ids):
        _, out, _ = self.module.run_command("ls /dev/ | grep davinci")
        all_davinci = re.findall(r"\bdavinci\d+\b", out)
        if need_mnt_davinci_device_ids:
            davinci_nodes = []
            for device_id in need_mnt_davinci_device_ids:
                davinci_node = "davinci{}".format(device_id)
                if davinci_node not in all_davinci:
                    self.messages.append("[ASCEND][ERROR] davinci device {} not found.".format(device_id))
                    self.module_failed()
                davinci_nodes.append(davinci_node)
            return davinci_nodes
        return all_davinci

    def module_failed(self):
        return self.module.fail_json(msg="\n".join(self.messages), rc=1, changed=False)

    def module_success(self):
        return self.module.exit_json(msg="Install DeepSeek success.", rc=0, changed=True)

    def clear_pre_cntr(self):
        self.cntr_mng = CntrManager(self.module, self.mindie_image_name, self.weight_mount_path, self.cntr_mnt_path,
                                    self.mnt_davinci_devices)
        self.cntr_mng.rm_last_cntr()

    def start_cntr(self):
        cntr_id = self.cntr_mng.start_cntr()
        return cntr_id

    def generate_server_entity(self):
        device_entities = HostHccnToolClient(self.mnt_davinci_devices, self.module,
                                             self.messages).build_device_entities()
        server_entry = ServerEntry(device=device_entities, server_id=self.node_ip,
                                   container_ip=self.node_ip).to_dict()
        self.facts['server_entry'] = server_entry

    def generate_ranktable(self, cntr_id):
        rank_id = 0
        all_server_entry = []
        for server_entry in self.all_server_entry:
            devices = []
            for device in server_entry.get("device", []):
                device["rank_id"] = str(rank_id)
                devices.append(device)
                rank_id += 1
            server_entry["device"] = devices
            all_server_entry.append(server_entry)
        rank_table = {"server_count": str(self.worker_num),
                      "server_list": all_server_entry,
                      "status": "completed",
                      "version": "1.0"}
        rank_table_file = os.path.join(self.deepseek_tmp_path, "rank_table_file.json")
        with open(rank_table_file, 'w') as file:
            file.write(json.dumps(rank_table, indent=4))
        os.chmod(rank_table_file, mode=0o640)

        # copy rank_table to docker
        if os.path.exists(rank_table_file):
            dest_path = "/usr/local/Ascend/mindie/latest/mindie-service/"
            cmd = ["docker", "cp", rank_table_file, f"{cntr_id}:{dest_path}"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "No error message"
                self.messages.append("Execute cmd '{}' failed with return code {}. Error details: {}".format(
                    ' '.join(cmd), result.returncode, error_msg))
                self.module_failed()

    def set_cntr_env(self, cntr_id: str):
        return SetDeepseekEnv(self.module, cntr_id, self.master_ip, self.worker_num, self.node_ip,
                              self.npu_info).execute()

    def modify_mindie_config(self, cntr_id: str):
        # 这里根据npu卡的类型或者worker num 读取配置文件
        mindie_service_conf = MindIEServiceConfig(self.module, self.master_ip, self.mindie_image_name,
                                                  self.model_weight_path,
                                                  cntr_id, self.npu_info, self.worker_num)
        mindie_service_conf.process()

    def start_mindie_service(self, cntr_id, env_file):
        MindIeService(self.module, cntr_id, env_file, self.worker_num, self.npu_info).start_service()

    def load_image(self):
        if not self.mindie_image_name:
            self.mindie_image_name = LoadMindIeImage(self.mindie_image_name, self.mindie_image_file, self.module,
                                                     self.npu_info, self.messages).docker_mindie_image()

    def install(self):
        self.load_image()
        self.clear_pre_cntr()
        cntr_id = self.start_cntr()
        if self.all_server_entry:
            self.generate_ranktable(cntr_id)
        env_file = self.set_cntr_env(cntr_id)
        self.modify_mindie_config(cntr_id)
        self.start_mindie_service(cntr_id, env_file)
        self.module_success()

    def collect_info(self):
        if self.worker_num == SINGLE_NODE:
            self.module.exit_json(changed=False, msg='Skip generate rank table file for single node ', rc=0)
        self.generate_server_entity()
        self.module.exit_json(changed=True, msg='Collect info success', ansible_facts=self.facts, rc=0)

    def run(self):
        if self.action == self._INSTALL_ACTION:
            self.install()
        elif self.action == self._COLLECT_ACTION:
            self.collect_info()


def main():
    DeepseekCntrInstaller().run()


if __name__ == '__main__':
    main()
