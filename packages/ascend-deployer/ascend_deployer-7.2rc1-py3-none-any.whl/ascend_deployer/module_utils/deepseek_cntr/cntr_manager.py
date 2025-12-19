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
from typing import List

from ansible.module_utils.basic import AnsibleModule


class CntrManager:
    _CNTR_CACHE_FILE = "/root/.ascend_deployer/.CONTAINER_CACHE"  # cntr_name=cntr_id

    retry_times = 10

    _DEFAULT_START_PARAMS = [
        "--device=/dev/davinci_manager",
        "--device=/dev/devmm_svm",
        "--device=/dev/hisi_hdc",
        "-v /usr/local/Ascend/driver:/usr/local/Ascend/driver",
        "-v /usr/local/Ascend/add-ons/:/usr/local/Ascend/add-ons/",
        "-v /usr/local/sbin/:/usr/local/sbin/",
        "-v /var/log/npu/slog/:/var/log/npu/slog",
        "-v /var/log/npu/profiling/:/var/log/npu/profiling",
        "-v /var/log/npu/dump/:/var/log/npu/dump",
        "-v /var/log/npu/:/usr/slog",
        "-v /etc/hccn.conf:/etc/hccn.conf",
    ]

    def __init__(self, module: AnsibleModule, image_name: str, weight_mount_path: str, cntr_mnt_path: str,
                 mnt_davinci_devices: List[str]):
        """
        Initialize CntrManager class for managing DeepSeek containers.

        @param module: The AnsibleModule object for executing commands
        @param image_name: Docker image name to be used for container creation
        @param weight_mount_path: Local path where model weights are stored
        @param cntr_mnt_path: Container path where model weights will be mounted
        @param mnt_davinci_devices: List of Davinci devices to be mounted to the container
        """
        self.module = module
        self.image_name = image_name
        self.weight_mount_path = weight_mount_path
        self.cntr_mnt_path = cntr_mnt_path
        self.mnt_davinci_devices = mnt_davinci_devices
        dir_path = os.path.dirname(self._CNTR_CACHE_FILE)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, mode=0o750)

    def get_docker_start_command(self, cntr_name: str) -> str:
        shm_size = "500g"
        mnt_davinci_devices = self.mnt_davinci_devices
        command = "docker run -itd --name {} ".format(cntr_name)
        command += "--network=host --privileged=true --shm-size={} ".format(shm_size)
        davinci = ["--device=/dev/{}".format(i) for i in mnt_davinci_devices]
        command += " ".join(davinci)
        command += " "
        command += " ".join(self._DEFAULT_START_PARAMS)
        command += " -v {}:{}".format(self.weight_mount_path, self.cntr_mnt_path)
        command += " {} /bin/bash".format(self.image_name)
        return command

    def start_cntr(self) -> str:
        """
        返回容器id
        """
        cntr_name = "deepseek_npu_{}".format(int(time.time()))
        command = self.get_docker_start_command(cntr_name)
        rc, out, err = self.module.run_command(command)
        if rc != 0:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] docker execute command: {} failed: {}".format(command, err)
            )
        cntr_id = out.strip()
        self._wait_for_cntr_ready(cntr_id)
        self._save_cntr_to_cache(cntr_name, cntr_id)
        return cntr_id

    def rm_last_cntr(self):
        cntr_name, cntr_id = self._read_local_cache()
        if not cntr_name:
            return
        command = "docker rm -f {}".format(cntr_id)
        _, _, _ = self.module.run_command(command)
        self._write_empty_file()

    def _save_cntr_to_cache(self, cntr_name: str, cntr_id: str):
        try:
            with open(self._CNTR_CACHE_FILE, "w") as f:
                f.write("{}={}".format(cntr_name, cntr_id))
            os.chmod(self._CNTR_CACHE_FILE, 0o640)
        except Exception as e:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Save container: {}-{} to local file: {} failed: ".format(
                    cntr_name, cntr_id, self._CNTR_CACHE_FILE, str(e))
            )

    def _wait_for_cntr_ready(self, cntr_id: str):
        command = "docker exec {} true > /dev/null 2>&1".format(cntr_id)
        retry = 1
        while retry <= self.retry_times:
            rc, _, _ = self.module.run_command(command)
            if rc == 0:
                return
            time.sleep(1)
        self.module.fail_json(
            changed=False,
            rc=1,
            msg="[ASCEND][ERROR] Container: {} starts failed, please check.".format(cntr_id)
        )

    def _read_local_cache(self) -> (str, str):
        if not os.path.exists(self._CNTR_CACHE_FILE):
            return "", ""
        try:
            with open(self._CNTR_CACHE_FILE, "r") as f:
                content = f.readlines()
        except Exception as e:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Read file: {} failed: ".format(self._CNTR_CACHE_FILE, str(e))
            )
        if not content:
            return "", ""
        cntr_name, cntr_id = content[0].strip().split("=")
        return cntr_name, cntr_id

    def _write_empty_file(self):
        try:
            with open(self._CNTR_CACHE_FILE, "w") as f:
                pass
        except Exception as e:
            self.module.fail_json(
                changed=False,
                rc=1,
                msg="[ASCEND][ERROR] Write file: {} failed: ".format(self._CNTR_CACHE_FILE, str(e))
            )

