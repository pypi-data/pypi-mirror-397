#!/usr/bin/env python3
# coding: utf-8
# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===========================================================================
import json
import os
import re
import shutil
import subprocess as sp
import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common_info import get_os_and_arch, need_skip_sys_package, DeployStatus, OSName
from ansible.module_utils.common_utils import ensure_docker_daemon_exist
from ansible.module_utils.path_manager import TmpPath


class SysInstaller:
    def __init__(self, module, nexus_url, os_and_arch, resources_dir, pkg_type):
        self.module = module
        self.nexus_url = nexus_url
        self.os_and_arch = os_and_arch
        self.resources_dir = resources_dir
        self.stdout = []
        self.pkg_type = pkg_type
        os.environ["http_proxy"] = ""
        os.environ["https_proxy"] = ""
        os.environ["HTTP_PROXY"] = ""
        os.environ["HTTPS_PROXY"] = ""
        os.environ["LD_LIBRARY_PATH"] = ""
        with open(os.path.expanduser("~/nexus/nexus_config.json"), "r") as f:
            self.nexus_config = json.load(f)

    def create_config_file(self):
        if self.os_and_arch in self.nexus_config["rpm_os"]:
            config_content = [
                "[nexus]\n",
                "name = {}\n".format(self.os_and_arch),
                "baseurl = {}/repository/{}/\n".format(self.nexus_url, self.os_and_arch),
                "gpgcheck = 0\n",
                "enabled = 1\n",
            ]
            config_file = os.path.expanduser("~/nexus/sources.repo")
            with open(config_file, "w") as repo:
                repo.writelines(config_content)
        else:
            config_file = os.path.expanduser("~/nexus/sources.list")
            nexus_codename = self.nexus_config["codename"].get(self.os_and_arch)
            if self.os_and_arch.startswith(("Debian", "veLinux")):
                trusted = "[trusted=yes]"
            else:
                trusted = ""
            with open(config_file, "w") as fp:
                fp.write("deb {} {}/repository/{}/ {} main\n".format(trusted, self.nexus_url, self.os_and_arch,
                                                                     nexus_codename))

    def install_deb_pkgs(self):
        sys_pkgs = self._get_pkgs_name()
        os.environ["DEBIAN_FRONTEND"] = "noninteractive"
        os.environ["DEBIAN_PRIORITY"] = "critical"
        cmds = [
            "apt update -o Dir::Etc::sourcelist=/root/nexus/sources.list -o Dir::Etc::sourceparts='-' "
            "-o Acquire::Check-Date=false",
            "apt install -f -y -o Dir::Etc::sourcelist=/root/nexus/sources.list -o Acquire::Check-Date=false",
            "apt install -y --no-install-recommends {} -o Acquire::Check-Date=false -o "
            "Dir::Etc::sourcelist=/root/nexus/sources.list".format(sys_pkgs),
        ]
        for cmd in cmds:
            if "recommends" not in cmd:
                self._run_cmd(cmd)
            else:
                self._run_cmd(cmd, pkg_name="sys_pkg")

    def install_rpm_pkgs(self):
        self._modify_conf("enabled=1", "enabled=0")
        sys_pkgs = self._get_pkgs_name()
        cmds_pre = [
            "yum clean all",
            'yum makecache --disablerepo="*" --enablerepo=nexus -c /root/nexus/sources.repo',
        ]
        for cmd in cmds_pre:
            self._run_cmd(cmd)
        if self.os_and_arch.startswith(("EulerOS", "Centos", "Kylin_V10Lance", "Kylin_V10Halberd")):
            os_release = os.uname()[2]
            self._install_kernel(os_release, "kernel-headers")
            self._install_kernel(os_release, "kernel-devel")
        install_pkgs_cmd = (
            'yum install --skip-broken -y {} --disablerepo="*" --enablerepo=nexus '
            "-c /root/nexus/sources.repo".format(sys_pkgs)
        )
        self._run_cmd(install_pkgs_cmd, pkg_name="sys_pkg")
        self._run_cmd("systemctl restart haveged")
        self._modify_conf("enabled=0", "enabled=1")

    def install_docker(self, pkg_type="rpm"):
        if self.module.get_bin_path("docker"):
            return

        # 处理containerd备份
        containerd_backup_path, containerd_path = self._backup_containerd()

        if "EulerOS" in self.os_and_arch:
            docker_pkgs_name = " ".join(self.nexus_config.get("euler_docker"))
        elif "Debian" in self.os_and_arch:
            docker_pkgs_name = " ".join(self.nexus_config.get("debian_docker"))
        else:
            docker_pkgs_name = " ".join(self.nexus_config.get("common_docker"))
        if pkg_type == "rpm":
            cmd = (
                'yum install -y --skip-broken {} --disablerepo="*" --enablerepo=nexus '
                "-c /root/nexus/sources.repo".format(docker_pkgs_name)
            )
            self._run_cmd(cmd, pkg_name="docker")
        elif pkg_type == "deb":
            cmd = (
                "apt install -y --no-install-recommends {} -o Acquire::Check-Date=false -o "
                "Dir::Etc::sourcelist=/root/nexus/sources.list".format(docker_pkgs_name)
            )
            self._run_cmd(cmd, pkg_name="docker")

        # 恢复containerd并重启相关服务
        self._restore_containerd_and_restart_services(containerd_backup_path, containerd_path)

        self._restart_docker()

    def _backup_containerd(self):
        """
        检查并备份containerd二进制文件
        返回: (备份路径, 原始路径) 元组
        """
        containerd_path = self.module.get_bin_path("containerd")
        containerd_backup_path = None
        if containerd_path:
            if not os.path.exists(TmpPath.ROOT):
                os.makedirs(TmpPath.ROOT, mode=0o750)
            containerd_backup_path = os.path.join(TmpPath.ROOT, "containerd.backup")
            try:
                shutil.copy2(containerd_path, containerd_backup_path)
            except (shutil.Error, IOError) as e:
                self.module.fail_json(msg="Failed to backup containerd: {}".format(str(e)), rc=1)
        return containerd_backup_path, containerd_path

    def _restore_containerd_and_restart_services(self, containerd_backup_path, containerd_path):
        """
        恢复containerd备份并重启相关服务
        """
        if not containerd_backup_path:
            return

        # 先备份当前的containerd文件
        current_containerd_backup = self._backup_current_containerd(containerd_path)

        try:
            # 恢复containerd文件
            self._restore_containerd_from_backup(containerd_backup_path, containerd_path)

            # 删除原始备份文件
            self._remove_file(containerd_backup_path)
            # 重启containerd服务并检查返回码
            if not self._restart_containerd_with_retry():
                # 如果重启失败，则恢复原来的containerd文件
                self._rollback_containerd(containerd_path, current_containerd_backup)
                self.module.fail_json(
                    msg="Failed to restart containerd with new version, rolled back to original", 
                    rc=1
                )
            
            # 重启相关服务
            self._restart_related_services()
        finally:
            # 清理临时备份文件
            if current_containerd_backup and os.path.exists(current_containerd_backup):
                self._remove_file(current_containerd_backup)

    def _backup_current_containerd(self, containerd_path):
        """备份当前的containerd文件"""
        current_containerd_backup = None
        if os.path.exists(containerd_path):
            current_containerd_backup = os.path.join(TmpPath.ROOT, "containerd.current.backup")
            try:
                shutil.copy2(containerd_path, current_containerd_backup)
            except (shutil.Error, IOError) as e:
                self.module.fail_json(msg="Failed to backup current containerd: {}".format(str(e)), rc=1)
        return current_containerd_backup

    def _restore_containerd_from_backup(self, containerd_backup_path, containerd_path):
        """从备份恢复containerd文件"""
        # 停止containerd服务以避免"text file busy"错误
        self._run_cmd("systemctl stop containerd")
        try:
            shutil.copy2(containerd_backup_path, containerd_path)
        except (shutil.Error, IOError) as e:
            self.module.fail_json(msg="Failed to restore containerd from backup: {}".format(str(e)), rc=1)

    def _restart_containerd_with_retry(self):
        """重启containerd服务，最多尝试3次"""
        for attempt in range(3):
            rc, _ = self._run_cmd("systemctl restart containerd", ignore_errors=True)
            if rc == 0:
                return True
            if attempt < 2:  # 不是最后一次尝试，等待5秒后重试
                time.sleep(5)
        return False

    def _rollback_containerd(self, containerd_path, current_containerd_backup):
        """回滚containerd到原始版本"""
        if current_containerd_backup and os.path.exists(current_containerd_backup):
            # 停止containerd服务以避免"text file busy"错误
            self._run_cmd("systemctl stop containerd")
            try:
                shutil.copy2(current_containerd_backup, containerd_path)
                # 重新启动containerd服务
                self._run_cmd("systemctl restart containerd")
            except (shutil.Error, IOError) as e:
                self.module.fail_json(msg="Failed to restore original containerd: {}".format(str(e)), rc=1)

    def _restart_related_services(self):
        """重启相关服务"""
        # 重启docker服务
        self._run_cmd("systemctl restart docker")
        # 检查是否有kubelet服务，如果有则重启
        if self.module.get_bin_path("kubelet"):
            self._run_cmd("systemctl restart kubelet")

    def _remove_file(self, file_path):
        """安全删除文件"""
        try:
            os.remove(file_path)
        except OSError as e:
            self.module.fail_json(msg="Failed to remove {} file: {}".format(file_path, str(e)), rc=1)

    def _modify_conf(self, pattern, repl):
        if self.os_and_arch in (OSName.BCLINUX_21_10_AARCH64, OSName.BCLINUX_21_10U4_AARCH64):
            file = "/etc/dnf/plugins/license-manager.conf"
            if os.path.islink(file):
                self.module.fail_json(changed=False, rc=1,
                                      msg="{} should not be a symbolic link file".format(file))
            with open(file, "r+") as f:
                content = f.read()
                content = re.sub(pattern, repl, content)
                f.seek(0)
                f.write(content)

    def _install_kernel(self, os_release, kernel_type):
        check_kernel_headers = "rpm -q {}".format(kernel_type)
        return_code, out = self._run_cmd(check_kernel_headers, ignore_errors=True)
        kernel_version = "{}-{}".format(kernel_type, os_release)
        if return_code == 0 and out == kernel_version:
            return
        cmd = 'yum install -y {} --disablerepo="*" --enablerepo=nexus -c ' "/root/nexus/sources.repo".format(
            kernel_version
        )
        return_code, _ = self._run_cmd(cmd, ignore_errors=True)
        if return_code != 0:
            cmd = (
                'yum install -y --skip-broken {} --disablerepo="*" --enablerepo=nexus '
                "-c /root/nexus/sources.repo".format(kernel_type)
            )
            self._run_cmd(cmd)

    def _run_cmd(self, cmd, pkg_name=None, ignore_errors=False):
        rc, out, err = self.module.run_command(cmd)
        self.module.log('run_cmd: {} '.format(cmd).ljust(120, '='))
        if out:
            for line in out.splitlines():
                self.module.log(line)
        if err:
            for line in err.splitlines():
                self.module.log(line)
        if not ignore_errors and (rc != 0 or "Failed" in err):
            self.module.fail_json(msg=err, rc=1, changed=True)
        if pkg_name:
            if pkg_name == "sys_pkg":
                self.stdout.append(out)
            self.stdout.append("{} installed successfully".format(pkg_name))
        return rc, out

    def _restart_docker(self):
        return_code = sp.call(["docker", "ps"], shell=False, stdout=sp.PIPE, stderr=sp.PIPE)
        if return_code != 0:
            self._run_cmd("systemctl enable docker")
            self._run_cmd("systemctl daemon-reload")
            self._run_cmd("systemctl restart docker")

    def _get_pkgs_name(self):
        pkg_info_path = os.path.expanduser("~/nexus/pkg_reqs.json")
        if not os.path.exists(pkg_info_path):
            pkg_info_path = os.path.expanduser("~/nexus/pkg_info.json")
        with open(pkg_info_path, "r") as f:
            pkg_info = json.load(f)
        pkgs_name = {item.get("name") for item in pkg_info}
        docker_pkgs_name = set(self.nexus_config.get("common_docker"))
        kernel_pkgs = {"kernel-headers", "kernel-devel"}
        if "EulerOS" in self.os_and_arch:
            pkgs_name -= kernel_pkgs
            docker_pkgs_name = set(self.nexus_config.get("euler_docker"))
        elif "CentOS_7.6" in self.os_and_arch:
            pkgs_name -= kernel_pkgs
        elif "Ubuntu_22.04_" in self.os_and_arch:
            pkgs_name.add("libssl-dev")
            pkgs_name.add("libssl1.1")

        return " ".join(pkgs_name - docker_pkgs_name)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            nexus_url=dict(type="str", required=True),
            ansible_run_tags=dict(type="list", required=True),
            resources_dir=dict(type="str", required=True),
            pkg_type=dict(type="str", required=True)
        )
    )
    nexus_url = module.params["nexus_url"]
    os_and_arch = get_os_and_arch()
    if need_skip_sys_package(os_and_arch):
        module.exit_json(changed=False, rc=0,
                         stdout="[ASCEND]not support installing sys_pkg on {}. Bypassing...".format(os_and_arch),
                         result={DeployStatus.DEPLOY_STATUS: DeployStatus.SKIP})
    resources_dir = os.path.expanduser(module.params["resources_dir"])
    pkg_type = module.params["pkg_type"]
    installer = SysInstaller(module, nexus_url, os_and_arch, resources_dir, pkg_type)
    installer.create_config_file()
    if os_and_arch.startswith(("Ubuntu", "Debian", "veLinux")):
        installer.install_deb_pkgs()
        installer.install_docker(pkg_type="deb")
    else:
        installer.install_rpm_pkgs()
        installer.install_docker(pkg_type="rpm")
    ensure_docker_daemon_exist(module)
    module.exit_json(changed=True, stdout="\n".join(installer.stdout), rc=0)


if __name__ == "__main__":
    main()
