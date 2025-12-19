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
import json
import os.path

from ansible.module_utils.path_manager import TmpPath
from ansible.module_utils.common_utils import is_valid_ip

SINGLE_NODE = 1
DOUBLE_NODE = 2

CONFIG_FILE_MAP = {
    SINGLE_NODE: {  # single node
        "a910b": "config_A2_single_8k.json",
        "a910_93": "config_A3_single_16k.json"
    },
    DOUBLE_NODE: {  # double nodes
        "a910b": "config_A2_double_16k.json",
    }
}
SCENE = "scene"
BACKEND_CONFIG = "BackendConfig"
MODEL_DEPLOY_CONFIG = "ModelDeployConfig"
MODEL_CONFIG = "ModelConfig"


class MindIEServiceConfig:
    """
    This class is mainly to process the mindie config.
    """

    _DEFAULT_CONFIG_PATH = "/usr/local/Ascend/mindie/latest/mindie-service/conf/config.json"

    _DOCKER_CP = "docker cp {} {}"

    def __init__(self, module, master_ip, mindie_image_name,
                 model_weight_path, cntr_id, npu_info, worker_num):

        """
        @param module: The AnsibleModule object
        @param master_ip: master node ip address
        @param mindie_image_name: mindie service docker image name
        @param model_weight_path: model weight path
        @param cntr_id: container id
        @param npu_info: npu information dictionary
        @param worker_num: number of worker nodes, use SINGLE_NODE or DOUBLE_NODE constants
        """

        self.module = module
        self.master_ip = master_ip
        self.mindie_image_name = mindie_image_name
        self.model_weight_path = model_weight_path
        self.cntr_id = cntr_id
        self.npu_info = npu_info
        self.worker_num = worker_num
        self.config_path = self._DEFAULT_CONFIG_PATH
        self.load_config_path = os.path.join(TmpPath.ROOT, "mindie_service")
        self.config_file = self.select_config_file()
        self.data = self.load_config()

    def select_config_file(self):
        scene = self.npu_info.get(SCENE) if self.npu_info else None
        # 使用嵌套字典方式查找配置文件
        worker_config = CONFIG_FILE_MAP.get(self.worker_num, {})
        config_filename = worker_config.get(scene)

        if config_filename:
            return os.path.join(self.load_config_path, config_filename)
        else:
            return self.module.fail_json(changed=False, rc=1,
                                         msg="[ASCEND][ERROR] No config file found for worker_num={},"
                                             " scene={}".format(self.worker_num, scene))

    def load_config(self):
        # type: () -> dict
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            return self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Parse config: {} failed: {}".format(self.config_path, str(e))
            )

    def validate_ip(self):
        if self.worker_num == SINGLE_NODE:
            return
        if not self.master_ip:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] The master_ip is empty, please check."
            )
        if not is_valid_ip(self.master_ip):
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] The master_ip: {} is invalid, please check.".format(self.master_ip)
            )

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Save config to {} failed: {}".format(self.config_path, str(e))
            )

    def modify_config(self):
        scene = self.npu_info.get(SCENE)
        # check data structure validity
        if not isinstance(self.data, dict):
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Invalid data structure: data is not type of Dict"
            )
            return
        backend_config = self.data.get(BACKEND_CONFIG)
        if not isinstance(backend_config, dict):
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Invalid data structure: {} is not type of Dict".format(BACKEND_CONFIG)
            )
            return
        model_deploy_config = backend_config.get(MODEL_DEPLOY_CONFIG)
        if not isinstance(model_deploy_config, dict):
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Invalid data structure: {} is not type of Dict".format(MODEL_DEPLOY_CONFIG)
            )
            return
        model_config = model_deploy_config.get(MODEL_CONFIG)
        if not isinstance(model_config, list) or len(model_config) == 0 or not isinstance(model_config[0], dict):
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Invalid data structure: {} is not type of List or "
                    "element is not type of Dict".format(MODEL_CONFIG)
            )
            return
        if self.worker_num == SINGLE_NODE or scene == "a910b":
            self.data[BACKEND_CONFIG][MODEL_DEPLOY_CONFIG][MODEL_CONFIG][0]["modelWeightPath"] = self.model_weight_path
            if scene == "a910_93":
                self.data[BACKEND_CONFIG][MODEL_DEPLOY_CONFIG][MODEL_CONFIG][0]["multi_step"] = 1
        else:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] The worker_num: {} is not supported on {}, "
                    "please check.".format(self.worker_num, scene)
            )

    def process(self):
        self.validate_ip()
        self.modify_config()
        self.save_config()
        dest_path = "{}:{}".format(self.cntr_id, self.config_path)
        command = self._DOCKER_CP.format(self.config_file, dest_path)
        rc, _, err = self.module.run_command(command)
        if rc != 0:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Execute command: {} failed: {}".format(command, err)
            )

        chmod_command = "docker exec {} chmod 640 {}".format(self.cntr_id, self.config_path)
        rc, _, err = self.module.run_command(chmod_command)
        if rc != 0:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Execute command: {} failed: {}".format(chmod_command, err)
            )
