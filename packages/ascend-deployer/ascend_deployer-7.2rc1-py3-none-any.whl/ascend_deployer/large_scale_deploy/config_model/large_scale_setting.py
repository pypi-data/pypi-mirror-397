from typing import List

from large_scale_deploy.config_model.base import Var
from large_scale_deploy.tools.errors import ConfigrationError


class LargeScaleSetting:

    def __init__(self, sub_group_max_size=200):
        self.sub_group_max_size = int(sub_group_max_size)

    @classmethod
    def from_inventory_vars(cls, inventory_vars: List[Var]):
        new_setting = cls()
        for var in inventory_vars:
            if not hasattr(new_setting, var.option.lower()):
                continue
            if not var.value.isdigit():
                raise ConfigrationError(f"large_scale setting option: {var.option} value: {var.value} must be number.")
            if var.option == "SUB_GROUP_MAX_SIZE" and int(var.value) <= 0:
                raise ConfigrationError(
                    f"large_scale setting option: {var.option} value: {var.value} must bigger than 0.")
            setattr(new_setting, var.option.lower(), int(var.value))
        return new_setting
