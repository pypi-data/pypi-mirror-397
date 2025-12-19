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

import abc
import inspect
import json
from typing import Dict


class JsonDict(metaclass=abc.ABCMeta):

    @staticmethod
    def _is_json_dict_in_typing_list(instance, sign_class):
        return isinstance(instance, list) and \
            isinstance(getattr(sign_class, "__args__"), tuple) and \
            len(sign_class.__args__) == 1 and \
            issubclass(sign_class.__args__[0], JsonDict)

    @classmethod
    def from_dict(cls, json_dict: Dict):
        sigs = inspect.signature(cls.__init__)
        args = []
        for arg_name, parameter in sigs.parameters.items():
            if arg_name == "self":
                continue
            value = json_dict.get(arg_name)
            if value is None:
                args.append(None)
                continue
            sign_class = parameter.annotation
            if isinstance(sign_class, type) and issubclass(sign_class, JsonDict):
                value = sign_class.from_dict(value)
            elif cls._is_json_dict_in_typing_list(value, sign_class):
                value = [sign_class.__args__[0].from_dict(item) for item in value]
            args.append(value)
        return cls(*args)

    @classmethod
    def from_json(cls, json_dict_str):
        return cls.from_dict(json.loads(json_dict_str))

    def to_dict(self):
        members = {}
        for key, value in vars(self).items():
            if key.startswith('__'):
                continue
            if isinstance(value, JsonDict):
                value = value.to_dict()
            elif isinstance(value, list):
                new_value = []
                for item in value:
                    if isinstance(item, JsonDict):
                        new_value.append(item.to_dict())
                    else:
                        new_value.append(item)
                value = new_value
            members[key] = value
        return members

    def to_json(self):
        return json.dumps(self.to_dict())
