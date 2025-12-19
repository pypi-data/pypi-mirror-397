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
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.deepseek_pd.load_mindie_image import LoadMindIeImage
from ansible.module_utils.deepseek_pd.extract_deploye_scripts import ExtractMindieDeployer
from ansible.module_utils.deepseek_pd.mindie_config import MindiePDConfig
from ansible.module_utils.deepseek_pd.install_dependencies import DependenciesInstaller


class DeepseekPDInstaller:
    _card_model_map = {"Atlas 800I A2": "800i-a2", "A900T": "800i-a2", "A300i-duo": "300i-duo"}
    _INSTALL_ACTION = "install"
    _CONFIGURE_ACTION = "configure"
    _EXTRACT_ACTION = "extract"

    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                action=dict(type="str", required=False),
                resources_dir=dict(type='str', required=False),
                node_name=dict(type="str", required=False),
                model_name=dict(type="str", required=False),
                weight_mount_path=dict(type="str", required=False),
                model_weight_path=dict(type="str", required=False),
                mindie_image_name=dict(type="str", required=False),
                mindie_image_file=dict(type="str", required=False),
                expert_map_file=dict(type="str", required=False),
                npu_info=dict(type="dict", required=False),
                python_tar=dict(type="str", required=False),
                job_id=dict(type="str", required=False),
                p_instances_num=dict(type="int", required=False),
                d_instances_num=dict(type="int", required=False),
                single_p_instance_pod_num=dict(type="int", required=False),
                single_d_instance_pod_num=dict(type="int", required=False),
                max_seq_len=dict(type="int", required=False),
                mindie_host_log_path=dict(type="str", required=False),
                tls_config=dict(type="dict", required=False),
                container_runtime_type=dict(type='dict', required=False),
            ),
        )
        self.action = self.module.params["action"]
        self.node_name = self.module.params["node_name"]
        self.model_name = self.module.params["model_name"]
        self.weight_mount_path = self.module.params["weight_mount_path"]
        self.model_weight_path = self.module.params["model_weight_path"]
        self.messages = []
        self.mindie_image_name = self.module.params["mindie_image_name"]
        self.mindie_image_file = self.module.params["mindie_image_file"]
        self.resources_dir = self.module.params["resources_dir"]
        self.p_instances_num = self.module.params["p_instances_num"]
        self.d_instances_num = self.module.params["d_instances_num"]
        self.single_p_instance_pod_num = self.module.params["single_p_instance_pod_num"]
        self.single_d_instance_pod_num = self.module.params["single_d_instance_pod_num"]
        self.job_id = self.module.params["job_id"]
        self.npu_info = self.module.params["npu_info"]
        self.arch = platform.machine()
        self.facts = dict()

    def _module_failed(self):
        return self.module.fail_json(msg="\n".join(self.messages), rc=1, changed=False)

    def _module_success(self):
        return self.module.exit_json(msg="Install DeepSeek success.", rc=0, changed=True)

    def configure_user_config(self):
        MindiePDConfig(self.module, self.mindie_image_name).run()
        self._module_success()

    def install_dependencies(self):
        DependenciesInstaller(self.module).run()

    def create_ms_namespace(self):
        self.module.run_command("kubectl create namespace {}".format(self.job_id))
        os.makedirs("/data/mindie-ms/status", mode=0o750, exist_ok=True)

    def install(self):
        self.mindie_image_name = LoadMindIeImage(self.mindie_image_name, self.mindie_image_file, self.module,
                                                 self.npu_info, self.messages).load()
        self.facts['mindie_image_name'] = self.mindie_image_name
        return self.module.exit_json(changed=True, msg='load image success', ansible_facts=self.facts)

    def extract_file(self):
        ExtractMindieDeployer(self.module).run()
        self._module_success()

    def run(self):
        if self.action == self._INSTALL_ACTION:
            self.install()
        elif self.action == self._CONFIGURE_ACTION:
            self.install_dependencies()
            self.create_ms_namespace()
            self.configure_user_config()
        elif self.action == self._EXTRACT_ACTION:
            self.extract_file()


def main():
    DeepseekPDInstaller().run()


if __name__ == '__main__':
    main()
