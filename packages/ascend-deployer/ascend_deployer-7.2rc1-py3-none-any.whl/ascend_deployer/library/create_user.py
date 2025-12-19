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
import shlex
import subprocess

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(argument_spec=dict(group=dict(type="str", required=True),
                                              user=dict(type="str", required=True)))
    group = module.params["group"]
    user = module.params["user"]
    rc, out, err = module.run_command(shlex.split("getent group {}".format(group)))
    if rc != 0 and rc != 2:  # getent 返回 2 表示命令执行成功，但是用户组未找到
        return module.fail_json(msg="run cmd: getent group {} failed".format(group))

    # 如果输出为空，则组不存在
    if not out.strip():
        module.run_command(shlex.split("groupadd {}".format(group)), check_rc=True)

    rc, out, err = module.run_command(shlex.split("getent passwd {}".format(user)))
    if rc != 0 and rc != 2:  # getent 返回 2 表示未找到
        return module.fail_json(msg="run cmd: getent passwd {} failed".format(user))

    # 如果输出为空，则用户不存在
    if not out.strip():
        module.run_command(shlex.split("useradd -g {} -d /home/{} -m {} -s /bin/bash".format(group, user, user)),
                           check_rc=True)
    return module.exit_json(rc=0, changed=True)


if __name__ == '__main__':
    main()
