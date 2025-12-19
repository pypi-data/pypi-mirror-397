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
import platform
import re

from ansible.module_utils.check_output_manager import check_event
from ansible.module_utils.check_utils import CheckUtil as util
from ansible.module_utils.common_utils import result_handler, compare_version
from ansible.module_utils.deepseek_pd.config_info import MAX_SEQ_LEN_DICT, STATIC_CONFIG_DICT_A910_93, \
    STATIC_CONFIG_DICT_A910B

# A910_93 经典配置
A910_93_COMBINATIONS = [
    (4, 1, 2, 2),  # 4*1P+2*2D
    (8, 1, 2, 4),  # 8*1P+2*4D
    (16, 1, 4, 4),  # 16*1P+4*4D
    (24, 1, 6, 4),  # 24*1P+6*4D
]

# a910b 经典配置
A910B_COMBINATIONS = [
    (2, 2, 1, 4),  # 2*2P+1*4D
    (4, 2, 2, 4),  # 4*2P+2*4D
    (4, 2, 1, 8),  # 4*2P+1*8D
]

#
A910_93_BASE_COMBINATION = (24, 1, 6, 4)  # N*（24*1P+6*4D）
A910B_BASE_COMBINATION = (4, 2, 1, 8)  # N*（4*2P+1*8D）

KUBERNETES_NAMESPACE_MAX_LENGTH = 63
_DOCKER = "docker"
_CONTAINERD = "containerd"

_IMAGES = "images"
_CTR = "ctr"


class DeepseekDpCheck:

    def __init__(self, module, error_messages):
        self.module = module
        self.tags = list(filter(bool, self.module.params.get('tags', [])))
        self.model_name = self.module.params["model_name"]
        self.weight_mount_path = self.module.params["weight_mount_path"]
        self.model_weight_path = self.module.params["model_weight_path"]
        self.messages = []
        self.mindie_image_name = self.module.params["mindie_image_name"]
        self.mindie_image_file = self.module.params["mindie_image_file"]
        self.p_instances_num = self.module.params["p_instances_num"]
        self.d_instances_num = self.module.params["d_instances_num"]
        self.single_p_instance_pod_num = self.module.params["single_p_instance_pod_num"]
        self.single_d_instance_pod_num = self.module.params["single_d_instance_pod_num"]
        self.expert_map_file = self.module.params["expert_map_file"]
        self.job_id = self.module.params["job_id"]
        self.max_seq_len = self.module.params["max_seq_len"]
        self.mindie_host_log_path = self.module.params["mindie_host_log_path"]
        self.job_id = self.module.params["job_id"]
        self.python_version = module.params.get("python_version")
        self.arch = platform.machine()
        self.tls_config = self.module.params["tls_config"]
        self.npu_info = module.params["npu_info"]
        self.cluster_info = module.params.get("cluster_info")
        self.container_runtime_type = self.module.params['container_runtime_type']
        self.worker_groups = self.module.params.get("worker_groups")
        self.master_groups = self.module.params.get("master_groups")

        self.facts = dict()
        self.error_messages = error_messages

        seq_len_scene = MAX_SEQ_LEN_DICT.get(self.max_seq_len)
        if self.npu_info.get("scene") == "a910_93":
            self.static_config = STATIC_CONFIG_DICT_A910_93.get(seq_len_scene)
        else:
            self.static_config = STATIC_CONFIG_DICT_A910B.get(seq_len_scene)

    @staticmethod
    def match_image_name(line, target_image_name):
        """
        匹配镜像名称，支持带前缀和不带前缀的情况

        Args:
            line (str): ctr images list 输出的一行
            target_image_name (str): 目标镜像名称

        Returns:
            bool: 是否匹配
        """
        if not line.strip():
            return False

        # 提取镜像名称部分（第一列）
        image_name_in_line = line.split()[0]

        # 直接匹配
        if image_name_in_line == target_image_name:
            return True

        # 去掉前缀后匹配，例如 docker.io/library/mindie:tag 匹配 mindie:tag
        if '/' in image_name_in_line and image_name_in_line.split('/')[-1] == target_image_name:
            return True

        return False

    def check_mount_path(self):
        """
        检查是否提供了挂载路径和路径是否实际存在
        """
        paths_to_check = {
            'weight_mount_path': self.weight_mount_path,
            'model_weight_path': self.model_weight_path
        }

        for path_name, path_value in paths_to_check.items():
            if not path_value:
                util.record_error('[ASCEND][ERROR] Please provide a value for the {} parameter.'.format(path_name),
                                  self.error_messages)
                return
            if not os.path.exists(path_value):
                util.record_error('[ASCEND][ERROR] {}: {} is not existed.'.format(path_name, path_value),
                                  self.error_messages)
                return
            if os.path.islink(path_value):
                util.record_error('[ASCEND][ERROR] The specified {} "{}" should not be a symbolic link.'.format(
                    path_name, path_value), self.error_messages)
                return

        # 检查 weight_mount_path 是否是 model_weight_path 的父目录
        mount_path = os.path.abspath(self.weight_mount_path)
        model_path = os.path.abspath(self.model_weight_path)

        # 检查 model_weight_path 是否在 weight_mount_path 下
        if not model_path.startswith(mount_path):
            util.record_error(
                '[ASCEND][ERROR] The model_weight_path must be under the weight_mount_path directory.',
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
                    "Valid format example: mindie:2.1.RC1-xx-xx-py311-ubuntu22.04-aarch64".format(
                        self.mindie_image_name), self.error_messages)
                return
            # 验证镜像是否存在
            self.check_image_exists_in_registry()

    def check_image_exists_in_registry(self):
        """
        通过查询镜像是否存在
        """
        if not self.container_runtime_type:
            util.record_error(
                "[ASCEND][ERROR] Query container_runtime_type failed.",
                self.error_messages)
            return
        if _DOCKER in list(self.container_runtime_type.values())[0]:
            container_runtime = _DOCKER
        elif _CONTAINERD in list(self.container_runtime_type.values())[0]:
            container_runtime = _CONTAINERD
        else:
            util.record_error(
                "[ASCEND][ERROR] Invalid container runtime type. ", self.error_messages)
            return

        if container_runtime == _DOCKER:
            docker_exists = self.module.get_bin_path(_DOCKER)
            if not docker_exists:
                util.record_error(
                    "[ASCEND][ERROR] Docker not found. Image '{}' not verified locally.".format(
                        self.mindie_image_name), self.error_messages)
                return
            check_cmd = ["docker", _IMAGES, "--format", "{{.Repository}}:{{.Tag}}"]

            rc, out, err = self.module.run_command(check_cmd)
            if rc != 0:
                util.record_error(
                    "[ASCEND][ERROR] Failed to list {} images. Command '{}' failed with return code {}. "
                    "Error message: {}".format(container_runtime, " ".join(check_cmd), rc, err.strip()),
                    self.error_messages)
                return

            image_lines = out.splitlines()
            if self.mindie_image_name in image_lines:
                return

        else:
            ctr_exists = self.module.get_bin_path(_CTR)
            if not ctr_exists:
                util.record_error(
                    "[ASCEND][ERROR] Containerd not found. Image '{}' not verified locally.".format(
                        self.mindie_image_name), self.error_messages)
                return

            # 先检查默认命名空间
            check_cmd_default = [_CTR, _IMAGES, "list"]
            rc, out, err = self.module.run_command(check_cmd_default)
            if rc == 0:
                image_lines = out.splitlines()
                # 检查镜像是否存在，支持带前缀和不带前缀的匹配
                if any(self.match_image_name(line, self.mindie_image_name) for line in image_lines if line.strip()):
                    return

            # 再检查k8s.io命名空间
            check_cmd_k8s = [_CTR, "-n", "k8s.io", _IMAGES, "list"]
            rc, out, err = self.module.run_command(check_cmd_k8s)
            if rc != 0:
                util.record_error(
                    "[ASCEND][ERROR] Failed to list {} images. Command '{}' failed with return code {}. "
                    "Error message: {}".format(container_runtime, " ".join(check_cmd_k8s), rc, err.strip()),
                    self.error_messages)
                return

            image_lines = out.splitlines()
            # 检查镜像是否存在，支持带前缀和不带前缀的匹配
            if any(self.match_image_name(line, self.mindie_image_name) for line in image_lines if line.strip()):
                return

        util.record_error(
            "[ASCEND][ERROR] mindie_image_name: '{}' not found locally.".format(self.mindie_image_name),
            self.error_messages)

    def check_expert_map_file(self):
        if not self.expert_map_file:
            return
        if not os.path.exists(self.expert_map_file):
            util.record_error("[ASCEND][ERROR] expert_map_file: {} not existed.".format(self.expert_map_file),
                              self.error_messages)
        if os.path.islink(self.expert_map_file):
            util.record_error(
                "[ASCEND][ERROR] The specified expert_map_file '{}' should not be a symbolic link.".format(
                    self.expert_map_file), self.error_messages)

    def check_job_id(self):
        """
        job_id用来创建kubernetes的namespace, 因此要符合kubernetes命名规范
        """
        if not self.job_id:
            util.record_error("[ASCEND][ERROR] Please provide a value for the job_id parameter.",
                              self.error_messages)

        # Kubernetes DNS label 格式检查 (RFC 1123)
        # 长度检查
        if len(self.job_id) > KUBERNETES_NAMESPACE_MAX_LENGTH:
            util.record_error("[ASCEND][ERROR] {} length should not exceed 63 characters.".format(self.job_id),
                              self.error_messages)
            return

        # 正则表达式检查：以字母数字开头和结尾，只能包含字母数字和连字符
        pattern = r'^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$'
        if not re.match(pattern, self.job_id):
            util.record_error("[ASCEND][ERROR] job_id must follow Kubernetes naming convention: "
                              "contain only lowercase letters, numbers, and hyphens, start and end with "
                              "alphanumeric characters.", self.error_messages)

    def check_model_name(self):
        if not self.model_name:
            return
        # 检查 model_name 是否为字符串类型
        if not isinstance(self.model_name, str):
            util.record_error("[ASCEND][ERROR] The model_name parameter must be a string, got {}.".format(
                type(self.model_name).__name__), self.error_messages)

    def check_positive_integer(self, param_name, param_value):
        """
        检查参数是否为正整数

        Args:
            param_name (str): 参数名称
            param_value: 参数值

        Returns:
            bool: 检查是否通过
        """
        # 检查参数是否存在（不为 None 或空字符串）
        if not param_value:
            util.record_error("[ASCEND][ERROR] Please provide a value for the {} parameter.".format(param_name),
                              self.error_messages)
            return False

        # 检查参数是否为整数类型或可以转换为整数
        param_int_value = None
        if isinstance(param_value, int):
            param_int_value = param_value
        elif isinstance(param_value, str):
            try:
                param_int_value = int(param_value)
            except (ValueError, TypeError) as e:
                util.record_error("[ASCEND][ERROR] The {} parameter must be an integer, got '{}'.".format(
                    param_name, param_value), self.error_messages)
                return False
        else:
            util.record_error("[ASCEND][ERROR] The {} parameter must be an integer, got {}.".format(
                param_name, type(param_value).__name__), self.error_messages)
            return False

        # 检查参数值是否为正整数
        if param_int_value is not None and param_int_value <= 0:
            util.record_error("[ASCEND][ERROR] The {} parameter must be a positive integer, got {}.".format(
                param_name, param_int_value), self.error_messages)
            return False

        return True

    def check_p_and_d_params(self):
        """
        检查 P 和 D 实例相关参数
        需要确保 p_instances_num, d_instances_num, single_p_instance_pod_num, single_d_instance_pod_num
        都存在且为正整数类型
        """
        # 定义需要检查的参数
        params_to_check = {
            'p_instances_num': self.p_instances_num,
            'd_instances_num': self.d_instances_num,
            'single_p_instance_pod_num': self.single_p_instance_pod_num,
            'single_d_instance_pod_num': self.single_d_instance_pod_num
        }

        # 检查每个参数是否存在且为正整数类型
        for param_name, param_value in params_to_check.items():
            self.check_positive_integer(param_name, param_value)

        # 检查 single_d_instance_pod_num 是否有效
        if not self._check_single_d_instance_pod_num():
            return

        # 根据不同场景检查参数组合
        scene = self.npu_info.get("scene", "")
        if scene == "a910b":
            self._check_a910b_combinations()
        elif scene == "a910_93":
            self._check_a910_93_combinations()

    def check_cluster_node_ready_count(self):
        """
        检查集群中处于Ready状态的节点数量是否满足P和D实例的总需求

        需要满足条件：Ready节点数 >= (p_instances_num * single_p_instance_pod_num) +
                                    (d_instances_num * single_d_instance_pod_num)
        """
        # 只有当相关参数都存在时才进行检查
        has_all_required_params = (self.p_instances_num and self.single_p_instance_pod_num and
                                   self.d_instances_num and self.single_d_instance_pod_num)

        # 只有当相关参数都存在时才进行检查
        if has_all_required_params:

            # 计算所需的总节点数
            required_nodes = (self.p_instances_num * self.single_p_instance_pod_num +
                              self.d_instances_num * self.single_d_instance_pod_num)

            # cluster_info是通过kubectl get nodes -o wide获取的，需要解析其stdout
            lines = self.cluster_info.get('stdout_lines', [])

            if not lines:
                util.record_error(
                    "[ASCEND][ERROR] Cannot get cluster node information, skip node count check.",
                    self.error_messages)
                return

            # 解析节点状态
            ready_node_count = 0

            # 跳过标题行（）
            for line in lines[1:] if len(lines) > 1 else lines:
                # kubectl get nodes 输出格式通常为：
                # NAME STATUS ROLES AGE VERSION INTERNAL-IP EXTERNAL-IP OS-IMAGE KERNEL-VERSION CONTAINER-RUNTIME
                # 示例:
                # node1 Ready <none> 10d v1.21.0 192.168.1.10 ... Ubuntu 20.04.1 LTS 5.4.0-65-generic docker://20.10.7
                fields = line.split()
                if len(fields) >= 2 and fields[1].lower() == 'ready':
                    ready_node_count += 1

            # 检查Ready节点数是否满足需求
            if ready_node_count < required_nodes:
                util.record_error(
                    "[ASCEND][ERROR] Not enough ready nodes in the cluster. "
                    "Required: {} nodes, Available: {} ready nodes.".format(required_nodes, ready_node_count),
                    self.error_messages)

    def _check_single_d_instance_pod_num(self):
        """检查 single_d_instance_pod_num 参数是否有效"""
        if not self.static_config:
            util.record_error("[ASCEND][ERROR] The static_config for max_seq_len:{} is none".format(self.max_seq_len),
                              self.error_messages)
            return False
        if self.single_d_instance_pod_num not in self.static_config["decode"].moe_ep:
            valid_keys = list(self.static_config["decode"].moe_ep.keys())
            util.record_error(
                "[ASCEND][ERROR] The single_d_instance_pod_num:{} parameter must be one of {}".format(
                    self.single_d_instance_pod_num, sorted(valid_keys)), self.error_messages)
            return False
        return True

    def _check_a910b_combinations(self):
        """检查 a910b 场景的参数组合"""
        # 检查a910b场景的组合
        combination = (self.p_instances_num, self.single_p_instance_pod_num,
                       self.d_instances_num, self.single_d_instance_pod_num)

        # 检查是否为预定义组合
        if combination in A910B_COMBINATIONS:
            return

        util.record_error(
            "[ASCEND][ERROR] For a910b scene, the combination of parameters must be one of: "
            "2*2P+1*4D, 4*2P+2*4D, 4*2P+1*8D", self.error_messages)

    def _check_a910_93_combinations(self):
        """检查 a910_93 场景的参数组合"""
        # 检查a910_93场景的组合
        combination = (self.p_instances_num, self.single_p_instance_pod_num,
                       self.d_instances_num, self.single_d_instance_pod_num)

        # 检查是否为预定义组合
        if combination in A910_93_COMBINATIONS:
            return

        util.record_error(
            "[ASCEND][ERROR] For a910_93 scene, the combination of parameters must be one of: "
            "4*1P+2*2D, 8*1P+2*4D, 16*1P+4*4D, 24*1P+6*4D", self.error_messages)

    def check_max_seq_len(self):
        if not self.max_seq_len:
            util.record_error("[ASCEND][ERROR] Please provide a value for the max_seq_len parameter.")
            return
        self.check_positive_integer('max_seq_len', self.max_seq_len)
        if self.max_seq_len not in MAX_SEQ_LEN_DICT:
            util.record_error(
                "[ASCEND][ERROR] The max_seq_len:{} parameter must be one of {}".format(self.max_seq_len, sorted(
                    MAX_SEQ_LEN_DICT.keys())), self.error_messages)

    def check_mindie_host_log_path(self):
        if not self.mindie_host_log_path:
            return
        # 检查路径是否存在
        if not os.path.exists(self.mindie_host_log_path):
            util.record_error('[ASCEND][ERROR] mindie_host_log_path: {} not existed.'.format(self.mindie_host_log_path),
                              self.error_messages)
            return

        # 检查是否为目录
        if not os.path.isdir(self.mindie_host_log_path):
            util.record_error(
                '[ASCEND][ERROR] mindie_host_log_path: {} is not a directory.'.format(self.mindie_host_log_path),
                self.error_messages)
        if os.path.islink(self.mindie_host_log_path):
            util.record_error(
                '[ASCEND][ERROR] The specified mindie_host_log_path "{}" should not be a symbolic link.'.format(
                    self.mindie_host_log_path), self.error_messages)

    def check_groups(self):
        if not self.worker_groups or len(self.worker_groups) == 0:
            util.record_error(
                "[ASCEND][ERROR] Please provide at least one worker node.", self.error_messages)
        if not self.master_groups or len(self.master_groups) == 0:
            util.record_error(
                "[ASCEND][ERROR] Please provide at least one master node.", self.error_messages)

    @check_event
    def check_deepseek_pd(self):
        self.check_mount_path()
        self.check_image_name_and_file()
        self.check_expert_map_file()
        self.check_job_id()
        self.check_model_name()
        self.check_p_and_d_params()
        self.check_max_seq_len()
        self.check_mindie_host_log_path()
        self.check_cluster_node_ready_count()
        self.check_groups()
