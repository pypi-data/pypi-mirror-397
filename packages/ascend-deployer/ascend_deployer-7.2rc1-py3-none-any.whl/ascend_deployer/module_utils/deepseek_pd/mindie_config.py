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

import json
import os
import platform

from ansible.module_utils.path_manager import TmpPath
from ansible.module_utils.deepseek_pd.config_info import STATIC_CONFIG_DICT_A910_93, STATIC_CONFIG_DICT_A910B, \
    MAX_SEQ_LEN_DICT

SCENE_CONFIG_MAP = {
    "a910_93": "user_config_base_A3.json",
    "a910b": "user_config.json"
}


class MindiePDConfig:

    def __init__(self, module, mindie_image_name):
        self.module = module
        self.p_instances_num = module.params["p_instances_num"]
        self.d_instances_num = module.params["d_instances_num"]
        self.single_p_instance_pod_num = module.params["single_p_instance_pod_num"]
        self.single_d_instance_pod_num = module.params["single_d_instance_pod_num"]
        self.weight_mount_path = module.params["weight_mount_path"]
        self.expert_map_file = module.params["expert_map_file"]
        self.image_name = mindie_image_name
        self.model_name = module.params["model_name"]
        self.model_weight_path = module.params["model_weight_path"]
        self.npu_info = module.params["npu_info"]
        self.arch = platform.machine()
        self.mindie_deploy_path = os.path.join(TmpPath.ROOT, "mindie_pd")
        self.job_id = module.params["job_id"]
        self.max_seq_len = module.params["max_seq_len"]
        self.mindie_host_log_path = module.params["mindie_host_log_path"]
        self.tls_config = module.params["tls_config"]
        config_file = SCENE_CONFIG_MAP.get(self.npu_info.get("scene"))
        self.user_config_json = os.path.join(
            self.mindie_deploy_path,
            "kubernetes_deploy_scripts",
            config_file
        )
        self.data = self.get_data()
        self.tls_config = self.module.params["tls_config"]

        self.seq_len_scene = MAX_SEQ_LEN_DICT.get(self.max_seq_len)
        if self.npu_info.get("scene") == "a910_93":
            self.static_config = STATIC_CONFIG_DICT_A910_93.get(self.seq_len_scene)
        else:
            self.static_config = STATIC_CONFIG_DICT_A910B.get(self.seq_len_scene)

    def modify_deploy_config(self):
        deploy_config = self.data.get('deploy_config')
        if not isinstance(deploy_config, dict):
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR]deploy_config is missing or not a dictionary in the config file."
            )
            return
        deploy_config['p_instances_num'] = self.p_instances_num
        deploy_config['d_instances_num'] = self.d_instances_num
        deploy_config['single_p_instance_pod_num'] = self.single_p_instance_pod_num
        deploy_config['single_d_instance_pod_num'] = self.single_d_instance_pod_num
        deploy_config['weight_mount_path'] = self.weight_mount_path
        deploy_config['image_name'] = self.image_name
        deploy_config['job_id'] = self.job_id
        if self.mindie_host_log_path:
            deploy_config['mindie_host_log_path'] = self.mindie_host_log_path
        if self.single_p_instance_pod_num == 1:
            deploy_config["prefill_distribute_enable"] = 0
        if self.single_d_instance_pod_num == 1:
            deploy_config["decode_distribute_enable"] = 0

        self.data['deploy_config'] = deploy_config

    def modify_mindie_service_prefill_config(self):

        # configure backend config
        backend_config = self.data["mindie_server_prefill_config"]["BackendConfig"]

        backend_config["multiNodesInferEnabled"] = self.single_p_instance_pod_num != 1
        backend_config["ModelDeployConfig"]["maxSeqLen"] = self.static_config["prefill"].maxSeqLen
        backend_config["ModelDeployConfig"]["maxInputTokenLen"] = self.static_config["prefill"].maxInputTokenLen
        backend_config["ScheduleConfig"]["maxPrefillTokens"] = self.static_config["prefill"].maxPrefillTokens

        # configure model config
        model_config = backend_config["ModelDeployConfig"]["ModelConfig"][0]
        model_config["modelName"] = self.model_name if self.model_name else model_config["modelName"]
        model_config["modelWeightPath"] = self.model_weight_path
        model_config["dp"] = self.static_config["prefill"].dp
        model_config["cp"] = self.static_config["prefill"].cp
        model_config["tp"] = self.static_config["prefill"].tp
        model_config["sp"] = self.static_config["prefill"].sp
        model_config["pp"] = self.static_config["prefill"].pp
        model_config["moe_tp"] = self.static_config["prefill"].moe_tp
        model_config["moe_ep"] = self.static_config["prefill"].moe_ep
        model_config["models"]["deepseekv2"]["ep_level"] = self.static_config["prefill"].ep_level

        # a910b 需要填写enable_init_routing_cutoff，topk_scaling_factor
        if self.npu_info.get("scene") == "a910b":
            if self.static_config["prefill"].enable_init_routing_cutoff:
                model_config["models"]["deepseekv2"]["enable_init_routing_cutoff"] = self.static_config[
                    "prefill"].enable_init_routing_cutoff

            if self.seq_len_scene == "16k":
                del model_config["models"]["deepseekv2"]["topk_scaling_factor"]
            else:
                model_config["models"]["deepseekv2"]["topk_scaling_factor"] = self.static_config[
                    "prefill"].topk_scaling_factor

        # MTP关闭时，删除plugin_params
        if not self.static_config["prefill"].MTP and "plugin_params" in model_config:
            del model_config["plugin_params"]

        # update model config
        backend_config["ModelDeployConfig"]["ModelConfig"][0] = model_config

        # update backend config
        self.data["mindie_server_prefill_config"]["BackendConfig"] = backend_config

    def modify_mindie_service_decode_config(self):

        self.data["mindie_server_decode_config"]["ServerConfig"][
            "distDPServerEnabled"] = self.single_d_instance_pod_num != 1

        # configure backend config
        backend_config = self.data["mindie_server_decode_config"]["BackendConfig"]

        backend_config["ModelDeployConfig"]["maxSeqLen"] = self.static_config["decode"].maxSeqLen
        backend_config["ModelDeployConfig"]["maxInputTokenLen"] = self.static_config["decode"].maxInputTokenLen
        backend_config["ScheduleConfig"]["maxPrefillTokens"] = self.static_config["decode"].maxPrefillTokens
        backend_config["ScheduleConfig"]["maxIterTimes"] = self.static_config["decode"].maxIterTimes

        # configure model config
        model_config = backend_config["ModelDeployConfig"]["ModelConfig"][0]
        model_config["modelName"] = self.model_name or model_config["modelName"]
        model_config["modelWeightPath"] = self.model_weight_path
        if self.expert_map_file:
            model_config["models"]["deepseekv2"]["eplb"]["expert_map_file"] = self.expert_map_file
        else:
            del model_config["models"]["deepseekv2"]["eplb"]

        model_config["dp"] = self.static_config["decode"].dp[self.single_d_instance_pod_num]
        model_config["cp"] = self.static_config["decode"].cp
        model_config["tp"] = self.static_config["decode"].tp
        model_config["sp"] = self.static_config["decode"].sp
        model_config["pp"] = self.static_config["decode"].pp
        model_config["moe_tp"] = self.static_config["decode"].moe_tp
        model_config["models"]["deepseekv2"]["ep_level"] = self.static_config["decode"].ep_level
        model_config["moe_ep"] = self.static_config["decode"].moe_ep[self.single_d_instance_pod_num]

        # MTP关闭时，删除plugin_params
        if not self.static_config["decode"].MTP and "plugin_params" in model_config:
            del model_config["plugin_params"]

        # update model config
        backend_config["ModelDeployConfig"]["ModelConfig"][0] = model_config

        # update backend config
        self.data["mindie_server_decode_config"]["BackendConfig"] = backend_config

    def get_data(self):
        if not os.path.exists(self.user_config_json):
            return self.module.fail_json(changed=False,
                                         rc=1,
                                         msg="[ASCEND][ERROR] Config file does not exist: {}".format(
                                             self.user_config_json))

        try:
            with open(self.user_config_json, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            return self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Failed to read config file {}: {}".format(self.user_config_json, str(e)))

    def write_data(self, data):
        with open(self.user_config_json, 'w') as f:
            json.dump(data, f, indent=4)

    def modify_tls_config(self):
        if not self.tls_config:
            return
        tls_config = self.data["deploy_config"]["tls_config"]

        if not self.tls_config.get('enable_tls', False):
            tls_config["tls_enable"] = False
        else:
            tls_config["kmc_ksf_master"] = self.tls_config.get('kmc_ksf_master', '')
            tls_config["kmc_ksf_standby"] = self.tls_config.get('kmc_ksf_standby', '')
            tls_config["kmc_ksf_items"] = self.tls_config.get('infer_tls_items', [])
            tls_config["management_tls_items"] = self.tls_config.get('management_tls_items', [])

        # a910_93 才配置ccae
        if self.npu_info.get("scene") == "a910_93":
            if not self.tls_config.get("ccae_tls_enable", False):
                tls_config["ccae_tls_enable"] = False
            else:
                tls_config["ccae_tls_items"] = self.tls_config["ccae_tls_items"]

        if not self.tls_config.get("cluster_tls_enable", False):
            tls_config["cluster_tls_enable"] = False
        else:
            tls_config["cluster_tls_items"] = self.tls_config["cluster_tls_items"]

        if not self.tls_config.get("etcd_server_tls_enable", False):
            tls_config["etcd_server_tls_enable"] = False
        else:
            tls_config["etcd_server_tls_items"] = self.tls_config["etcd_server_tls_items"]

        if not self.tls_config.get("infer_tls_enable", False):
            tls_config["infer_tls_enable"] = False
        else:
            tls_config["infer_tls_items"] = self.tls_config["infer_tls_items"]

        if not self.tls_config.get("management_tls_enable", False):
            tls_config["management_tls_enable"] = False
        else:
            tls_config["management_tls_items"] = self.tls_config["management_tls_items"]

        self.data["deploy_config"]["tls_config"] = tls_config

    def modify_mindie_env(self):
        # 800I A2 时需要配置分层通信
        mindie_env = os.path.join(self.mindie_deploy_path, "kubernetes_deploy_scripts", "conf", "mindie_env.json")
        if not os.path.exists(mindie_env) or self.npu_info.get("scene") != "a910b":
            return
        with open(mindie_env, 'r') as f:
            data = json.load(f)

        # 添加环境变量
        data["mindie_server_decode_env"]["HCCL_INTRA_PCIE_ENABLE"] = 1
        data["mindie_server_decode_env"]["HCCL_INTRA_ROCE_ENABLE"] = 0

        # 写回文件
        with open(mindie_env, 'w') as f:
            json.dump(data, f, indent=4)

    def run(self):
        self.modify_deploy_config()
        self.modify_mindie_service_prefill_config()
        self.modify_mindie_service_decode_config()
        self.modify_tls_config()
        self.write_data(self.data)
        self.modify_mindie_env()
