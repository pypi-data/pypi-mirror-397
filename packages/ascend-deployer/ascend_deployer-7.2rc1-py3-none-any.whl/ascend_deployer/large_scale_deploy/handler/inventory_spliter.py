from typing import List

from large_scale_deploy.common.common_data import LS_CONSOLE_LOGGER
from large_scale_deploy.config_model.host import InventoryHostInfo
from large_scale_deploy.config_model.base import Var
from large_scale_deploy.config_model.inventory import LargeScaleInventory
from large_scale_deploy.tools.errors import ConfigrationError
from large_scale_deploy.tools.spread_tool import ConnHostInfo


class SubGroup:

    def __init__(self, deploy_node: InventoryHostInfo, workers: List[InventoryHostInfo],
                 src_inventory: LargeScaleInventory):
        self.deploy_node = deploy_node
        self.deploy_node_conn_info = ConnHostInfo.from_ansible_host_info(deploy_node.to_info_dict())
        self.workers = workers
        self.inventory = self._generate_new_inventory(src_inventory, deploy_node, workers)

    @staticmethod
    def _generate_new_inventory(src_inventory: LargeScaleInventory, deploy_node: InventoryHostInfo,
                                workers: List[InventoryHostInfo]):
        new_inventory = src_inventory.to_inventory_copy()
        new_inventory.worker = workers
        new_inventory.other_build_image = [deploy_node]
        return new_inventory


class InventorySpliter:

    def __init__(self, src_inventory: LargeScaleInventory):
        self._src_inventory = src_inventory
        self._large_scale_setting = src_inventory.large_scale_setting

    def _check_workers_when_deploy_node(self, workers: List[InventoryHostInfo], sub_groups: List[SubGroup]):
        max_subgroup_size = max((len(sg.workers) for sg in sub_groups), default=0)
        if max_subgroup_size > self._large_scale_setting.sub_group_max_size:
            LS_CONSOLE_LOGGER.warning(f"Worker count: {len(workers)}, "
                                      f"the sub group max size: {max_subgroup_size} is bigger than "
                                      f"{self._large_scale_setting.sub_group_max_size}")

    def _generate_sub_group_by_deploy_node(self, deploy_nodes, workers):
        sub_groups = []
        cur_deploy_node_idx = 1
        cur_worker_index = 0
        self._src_inventory.apply_node = [deploy_nodes[0]]
        for index, worker in enumerate(workers):
            if (cur_deploy_node_idx < len(deploy_nodes) and
                    worker.int_ip >= deploy_nodes[cur_deploy_node_idx].int_ip):
                sub_group_workers = workers[cur_worker_index: index]
                sub_group = SubGroup(deploy_nodes[cur_deploy_node_idx - 1], sub_group_workers, self._src_inventory)
                sub_group.inventory.all_vars.append(Var("sub_group_idx", str(cur_deploy_node_idx)))
                sub_groups.append(sub_group)
                cur_deploy_node_idx += 1
                cur_worker_index = index
            if cur_deploy_node_idx >= len(deploy_nodes):
                sub_group = SubGroup(deploy_nodes[-1], workers[index:], self._src_inventory)
                sub_group.inventory.all_vars.append(Var("sub_group_idx", str(cur_deploy_node_idx)))
                sub_groups.append(sub_group)
                break
        return sub_groups

    def split_by_deploy_node(self) -> List[SubGroup]:
        workers = self._src_inventory.worker
        deploy_nodes = self._src_inventory.deploy_node
        sub_groups = self._generate_sub_group_by_deploy_node(deploy_nodes, workers)
        self._check_workers_when_deploy_node(workers, sub_groups)
        return sub_groups

    def split_by_network(self) -> List[SubGroup]:
        workers = self._src_inventory.worker
        deploy_nodes = workers[::self._large_scale_setting.sub_group_max_size]
        sub_groups = self._generate_sub_group_by_deploy_node(deploy_nodes, workers)
        return sub_groups
