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

import re

from ansible.module_utils.utils import JsonDict


class HccnIpTable:
    """
    A class to represent HCCN IP table information and parse HCCN tool output.

    This class is used to store and parse IP address and netmask information
    obtained from HCCN tool commands.
    """

    # 使用类变量替代类方法
    TABLE_SEQ_STR = ":"

    def __init__(self, ipaddr="", netmask=""):
        self.ipaddr = ipaddr
        self.netmask = netmask

    @classmethod
    def parse(cls, recv_str: str):
        if not recv_str:
            return None
        res = cls()
        lines = recv_str.splitlines()
        for k, _ in res.__dict__.items():
            for line in lines:
                if k in line and cls.TABLE_SEQ_STR in line:
                    value = line.split(cls.TABLE_SEQ_STR)[1]
                    setattr(res, k, value)
        return res

class DeviceEntry(JsonDict):
    """
      A class to represent device entry information for NPU devices.

      This class stores the mapping between device ID, device IP address, and rank ID
      for NPU devices in a distributed computing environment.
      """

    def __init__(self, device_id, device_ip, rank_id):
        """
        Initialize DeviceEntry with device information.

        @param device_id: Unique identifier for the NPU device
        @param device_ip: IP address of the NPU device
        @param rank_id: Rank identifier for the device in distributed computing context
        """
        self.device_id = device_id
        self.device_ip = device_ip
        self.rank_id = rank_id


class HostHccnToolClient:
    """
    A class to manage HCCN tool clients for multiple NPU devices on a host.

    This class provides functionality to build NPU card HCCN tool clients and
    create device entities for distributed computing configurations.
    """

    def __init__(self, davinci_devices, module, error_messages):
        self.davinci_devices = davinci_devices
        self.module = module
        self.error_messages = error_messages

    def build_npu_card_hccn_tool_client(self):
        res = []
        for davinci_device in self.davinci_devices:
            res.append(NpuCardHccnToolClient(davinci_device, self.module, self.error_messages))
        return res

    def build_device_entities(self):
        res = []
        for card_client in self.build_npu_card_hccn_tool_client():
            entry = DeviceEntry(device_id=card_client.npu_id, device_ip=card_client.query_npu_ip(),
                                rank_id=str(int(card_client.npu_id) + 1))
            res.append(entry)
        return res


class NpuCardHccnToolClient:
    """
    A class to interact with HCCN tool for a specific NPU card.

    This class provides functionality to query NPU card information using HCCN tool commands.
    """

    def __init__(self, davinci_device: str, module, error_messages):
        """
        Initialize NpuCardHccnToolClient with device and module information.

        @param davinci_device: Davinci device identifier string (e.g., "davinci0")
        @param module: Ansible module instance for executing commands
        @param error_messages: Error messages collection for handling exceptions
        """
        self.davinci_device = davinci_device
        self.module = module
        self.error_messages = error_messages
        npu_fields = re.split(r"(\d+)", davinci_device)
        if len(npu_fields) < 2:
            self.module.fail_json(
                msg=f"Invalid davinci device format: {davinci_device}", 
                rc=1, 
                changed=False
            )
        self.npu_id = npu_fields[1]

    def query_npu_ip(self):
        _, outputs, _ = self.module.run_command(f'hccn_tool -i {self.npu_id} -ip -g', check_rc=True)
        hccn_ip_table = HccnIpTable.parse(outputs)
        if not hccn_ip_table:
            return self.module.fail_json(msg=f"Failed to query npu ip of {self.npu_id}", rc=1, changed=False)
        return hccn_ip_table.ipaddr
