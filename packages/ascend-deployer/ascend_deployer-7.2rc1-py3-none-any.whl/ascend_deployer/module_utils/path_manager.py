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

import errno
import os.path
import shutil
import string
import tarfile
import zipfile

_CUR_DIR = os.path.dirname(__file__)
PATH_WHITE_LIST_LIN = string.digits + string.ascii_letters + '~-+_./ '
MIN_PATH_LEN = 1
MAX_PATH_LEN = 4096


class ParameterTypes:
    """
    定义Ansible模块参数类型的常量类
    """
    STR = "str"
    INT = "int"
    DICT = "dict"
    LIST = "list"
    BOOL = "bool"


def get_validated_env(
        env_name,
        whitelist=PATH_WHITE_LIST_LIN,
        check_symlink=True,
        check_owner=True
):
    """
    获取并验证环境变量 (兼容 Python 2/3)
    :param env_name: 环境变量名称
    :param whitelist: 允许的值列表
    :param check_symlink: 是否检查软链接
    :param check_owner: 属组检查
    :return: 验证通过的环境变量值
    :raises ValueError: 验证失败时抛出
    """
    value = os.getenv(env_name)
    if value is None:
        return None
    # 白名单校验
    whitelist_check(value, whitelist)
    # 长度校验
    length_check(env_name, MAX_PATH_LEN, MIN_PATH_LEN, value)
    # 软连接校验
    if check_symlink:
        symlink_check(env_name, value)
    if check_owner and os.path.lexists(value) and not owner_check(value):
        raise ValueError("The path {} is not owned by current user or root.".format(value))
    return value


def whitelist_check(value, whitelist):
    for char in value:
        if char not in whitelist:
            raise ValueError(
                "The path is invalid. The path can contain only char in '{}'".format(whitelist))


def owner_check(path):
    path_stat = os.stat(path)
    path_owner, path_gid = path_stat.st_uid, path_stat.st_gid
    user_check = path_owner == os.getuid() and path_owner == os.geteuid()
    return path_owner == 0 or path_gid in os.getgroups() or user_check


def length_check(env_name, max_length, min_length, value):
    str_len = len(value)
    if min_length is not None and str_len < min_length:
        raise ValueError(
            "Value for {} is too short. Minimum length: {}, actual: {}".format(
                env_name, min_length, str_len
            )
        )
    if max_length is not None and str_len > max_length:
        raise ValueError(
            "Value for {} is too long. Maximum length: {}, actual: {}".format(
                env_name, max_length, str_len
            )
        )


def symlink_check(env_name, value):
    # 在 Python 2/3 中正确处理 unicode 路径
    if isinstance(value, bytes):
        path_value = value.decode('utf-8', 'replace')
    else:
        path_value = value
    # 软链接检查
    try:
        # 检查路径是否存在且是符号链接
        if os.path.lexists(path_value) and os.path.islink(path_value):
            raise ValueError(
                "Path for {} is a symlink: {}. Symlinks are not allowed for security reasons.".format(
                    env_name, path_value
                )
            )
    except (OSError, IOError) as e:
        # 处理文件系统访问错误
        if e.errno != errno.ENOENT:  # 忽略文件不存在的错误
            raise ValueError(
                "Error checking symlink for {}: {} - {}".format(env_name, path_value, str(e))
            )


class ProjectPath:
    USER_HOME = os.path.expanduser("~")
    ROOT = os.path.dirname(_CUR_DIR)
    PLAYBOOK_DIR = os.path.join(ROOT, "playbooks")
    INVENTORY_FILE = "inventory_file"
    PROCESS_PLAYBOOK_DIR = os.path.join(PLAYBOOK_DIR, "process")


class TmpPath:
    ROOT = os.path.join(ProjectPath.USER_HOME, ".ascend_deployer")
    DEPLOY_INFO = os.path.join(ROOT, "deploy_info")
    DL_YAML_DIR = os.path.join(ROOT, "dl_yaml")
    PROGRESS_JSON_NAME = "deployer_progress_output.json"
    PROGRESS_JSON = os.path.join(DEPLOY_INFO, PROGRESS_JSON_NAME)
    TEST_REPORT_JSON = os.path.join(DEPLOY_INFO, "test_report.json")
    CHECK_RES_OUTPUT_JSON = os.path.join(DEPLOY_INFO, "check_res_output.json")


class LargeScalePath:
    ROOT_TMP_DIR = os.path.join(TmpPath.ROOT, "large_scale_deploy")
    INVENTORY_FILE_PATH = os.path.join(ProjectPath.ROOT, "large_scale_inventory.ini")
    PARSED_INVENTORY_FILE_PATH = os.path.join(ROOT_TMP_DIR, "parsed_inventory_file.ini")
    DEPLOY_NODE_INVENTORY_FILE_PATH = os.path.join(ROOT_TMP_DIR, "deploy_node_inventory_file.ini")
    REMOTE_DEPLOYER_DIR = os.path.join(ROOT_TMP_DIR, "ascend_deployer")
    REMOTE_INVENTORY_FILE = os.path.join(REMOTE_DEPLOYER_DIR, ProjectPath.INVENTORY_FILE)
    REMOTE_START_SCRIPT = os.path.join(REMOTE_DEPLOYER_DIR, "install.sh")
    REMOTE_EXECUTE_RES_LOG = os.path.join(ROOT_TMP_DIR, "ascend_deployer_execute.log")
    REMOTE_HOST_RESULTS = os.path.join(ROOT_TMP_DIR, "remote_host_data")
    SPREAD_TASK = os.path.join(ROOT_TMP_DIR, "spread_task")
    SPREAD_NODES_TREE_JSON = os.path.join(SPREAD_TASK, "spread_nodes_tree.json")
    EXEC_RESULTS_DIR = os.path.join(SPREAD_TASK, "exec_results")
    REPORT_DIR = os.path.join(ROOT_TMP_DIR, "report")
    ALL_TEST_REPORT_CSV = os.path.join(REPORT_DIR, "test_report.csv")


class PathManager:

    @classmethod
    def recover_dir(cls, dir_path):
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path, mode=0o750, exist_ok=True)

    @classmethod
    def init_large_scale_dirs(cls):
        cls.recover_dir(LargeScalePath.REMOTE_HOST_RESULTS)
        cls.recover_dir(LargeScalePath.REPORT_DIR)

    @classmethod
    def clear_last_info_except_inventory(cls):
        cls.recover_dir(LargeScalePath.REPORT_DIR)
        all_remote_ip = os.listdir(LargeScalePath.REMOTE_HOST_RESULTS)
        for ip in all_remote_ip:
            remote_info_path = os.path.join(LargeScalePath.REMOTE_HOST_RESULTS, ip)
            for file in os.listdir(remote_info_path):
                if file != ProjectPath.INVENTORY_FILE:
                    os.remove(os.path.join(remote_info_path, file))


class CompressedFileCheckUtils:
    """
    Utility class for checking compressed files (ZIP and TAR) for security issues.

    This class provides methods to validate compressed files by checking for:
    - Symbolic links (which can be a security risk)
    - Path traversal attempts (e.g., files containing ../ sequences)
    - Absolute paths (which can be a security risk)

    The class supports both ZIP and TAR file formats and provides comprehensive
    security checks to prevent potential security vulnerabilities when extracting
    compressed files.
    """
    WHITELIST_DIRS = [
        "mpich-4.1.3/modules/"
    ]

    @staticmethod
    def is_in_whitelist(file_path):
        """检查文件路径是否在白名单目录中"""
        return any(file_path.startswith(dir) for dir in CompressedFileCheckUtils.WHITELIST_DIRS)

    @staticmethod
    def check_tar_file_symbolic_link(file_info):
        # 添加白名单检查，如果在白名单中则跳过符号链接检查
        if CompressedFileCheckUtils.is_in_whitelist(file_info.path):
            return True, ''

        if file_info.issym():
            err_msg = "[ASCEND][ERROR] The file:{} is a symbolic link, please check it.".format(file_info.path)
            return False, err_msg
        return True, ''

    @staticmethod
    def check_zip_file_symbolic_link(file_info):
        # 添加白名单检查，如果在白名单中则跳过符号链接检查
        if CompressedFileCheckUtils.is_in_whitelist(file_info.filename):
            return True, ''

        # external_attr表示zip中该文件的外部属性，包括目录，符号链接，文件权限，形如：lrwxrwxrwx，drwxr-xr-x，-rw-rw-r--
        # 0o120000为符号链接的权限模式前缀，加上文件权限就是0o120777，使用os.lstat(符号链接路径).st_mode查看符号链接权限模式
        # 0o40000为目录的权限模式前缀，加上文件权限就是0o40755，使用os.stat(目录路径).st_mode查看目录权限模式
        # 0o100000为普通文件的权限模式前缀，加上文件权限就是0o100664，使用os.stat(普通文件路径).st_mode查看普通文件权限模式
        # external_attr=0，然后分文件和目录处理不同
        # external_attr |= (权限模式) << 16，然后目录为了兼容ms-dos会再来一下：external_attr |= 0x10
        # 所以判断zip文件中的文件是否为符号链接，只需要external_attr > 0o120000 << 16即可，前提是文件类型是ZIP_STORED
        if file_info.compress_type == zipfile.ZIP_STORED and file_info.external_attr > 0o120000 << 16:
            err_msg = "[ASCEND][ERROR] The file:{} is a symbolic link, please check it.".format(file_info.path)
            return False, err_msg
        return True, ''

    @staticmethod
    def check_package_inner_file_name(file_name):
        check_str_list = ["../", "..\\", ".\\", "./", "~/"]
        for check_str in check_str_list:
            if check_str in file_name:
                err_msg = "[ASCEND][ERROR] check compressed file:{} failed ,inner file has special string".format(
                    file_name)
                return False, err_msg
            if os.path.isabs(file_name):
                err_msg = "[ASCEND][ERROR] check compressed file:{} failed ,inner file cannot be abspath".format(
                    file_name)
                return False, err_msg
        return True, ''

    @staticmethod
    def check_zip_file_info(filepath):
        with zipfile.ZipFile(filepath, 'r') as file_list:
            for file in file_list.infolist():
                checks = [
                    CompressedFileCheckUtils.check_zip_file_symbolic_link(file),
                    CompressedFileCheckUtils.check_package_inner_file_name(file.filename)
                ]

                for ret, err_msg in checks:
                    if not ret:
                        return False, err_msg
            return True, ''

    @staticmethod
    def check_tar_file_info(filepath):
        try:
            with tarfile.open(filepath, 'r') as file_list:
                for file in file_list:
                    checks = [
                        CompressedFileCheckUtils.check_tar_file_symbolic_link(file),
                        CompressedFileCheckUtils.check_package_inner_file_name(file.name)
                    ]

                    for ret, err_msg in checks:
                        if not ret:
                            return False, err_msg
                return True, ''
        except Exception as e:
            return False, "[ASCEND][ERROR] Failed to check tar file {}: {}".format(filepath, str(e))

    @staticmethod
    def check_compressed_file_valid(filepath):
        try:
            if filepath.endswith((".tar.gz", ".tar")):
                ret, err_msg = CompressedFileCheckUtils.check_tar_file_info(filepath)
                if not ret:
                    return False, err_msg
                return True, ""
            elif filepath.endswith(".zip"):
                ret, err_msg = CompressedFileCheckUtils.check_zip_file_info(filepath)
                if not ret:
                    return False, err_msg
                return True, ""
            else:
                err_msg = "[ASCEND][ERROR] unsupported compressed file format {}".format(filepath)
                return False, err_msg
        except Exception as e:
            err_msg = "[ASCEND][ERROR] {}".format(str(e))
            return False, err_msg
