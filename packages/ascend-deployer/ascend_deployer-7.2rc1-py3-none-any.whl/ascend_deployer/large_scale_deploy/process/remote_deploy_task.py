import json
import logging
import os.path
import queue
import sys
import time
import traceback

from large_scale_deploy.config_model.inventory import Inventory
from large_scale_deploy.tools import spread_tool, errors
from large_scale_deploy.tools.spread_tool import ConnHostInfo
from module_utils.path_manager import LargeScalePath, TmpPath, PathManager, ProjectPath

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("large_scale_deployer.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("large_scale_deployer")


class HostError:

    def __init__(self, host, error_info_list):
        self.host = host
        self.error_info_list = error_info_list


class RemoteDeployTask:
    _ROUND_WAIT_TIME = 20
    _MAX_WAIT_TIME = 3 * 60 * 60

    def __init__(self, remote_conn_info: ConnHostInfo, inventory: Inventory, ascend_deployer_args: str,
                 error_que: queue.Queue, retry_args=""):
        self._remote_conn_info = remote_conn_info
        self._inventory = inventory
        self._ascend_deployer_args = ascend_deployer_args
        self._host_result_dir = os.path.join(LargeScalePath.REMOTE_HOST_RESULTS, self._remote_conn_info.ip)
        self._error_que = error_que
        self._retry_args = retry_args

    @staticmethod
    def check_host_status(data):
        """
        检查主机检查结果状态
        """
        host_check_list = data.get("HostCheckResList", {}).values()
        for host_info in host_check_list:
            check_items = host_info.get("check_res_list", [])
            if any(check_item.get("status", "") != "success" for check_item in check_items):
                return False
        return True

    @spread_tool.validate_cmd_result()
    def _start_deploy(self, start_cmd):
        cmd = f"echo y | nohup  {start_cmd} > " \
              f"{LargeScalePath.REMOTE_EXECUTE_RES_LOG} 2>&1 &"
        return spread_tool.run_ssh_cmd(self._remote_conn_info, cmd)

    @spread_tool.validate_cmd_result(raise_error=False)
    def _is_process_existed(self, process_cmd):
        return spread_tool.run_ssh_cmd(self._remote_conn_info, f'ps -ef | grep "{process_cmd}" | grep -v grep')

    @spread_tool.validate_cmd_result(raise_error=False)
    def _clear_remote_old_progress(self):
        return spread_tool.run_ssh_cmd(self._remote_conn_info, f"rm -rf {TmpPath.PROGRESS_JSON}")

    @spread_tool.validate_cmd_result(raise_error=False)
    def _download_progress_config(self):
        return spread_tool.scp_download(self._remote_conn_info, self._host_result_dir, TmpPath.PROGRESS_JSON)

    @spread_tool.validate_cmd_result(raise_error=False)
    def _download_test_report(self):
        return spread_tool.scp_download(self._remote_conn_info, self._host_result_dir, TmpPath.TEST_REPORT_JSON)

    @spread_tool.validate_cmd_result(raise_error=False)
    def _download_check_report(self):
        return spread_tool.scp_download(self._remote_conn_info, self._host_result_dir, TmpPath.CHECK_RES_OUTPUT_JSON)

    @spread_tool.validate_cmd_result()
    def _download_execute_failed_log(self):
        return spread_tool.scp_download(self._remote_conn_info, self._host_result_dir,
                                        LargeScalePath.REMOTE_EXECUTE_RES_LOG)

    @spread_tool.validate_cmd_result()
    def _send_inventory_file(self):
        cur_inventory_file_path = os.path.join(self._host_result_dir, ProjectPath.INVENTORY_FILE)
        if not self._retry_args:
            self._inventory.output(cur_inventory_file_path)
        return spread_tool.scp_upload(self._remote_conn_info, cur_inventory_file_path,
                                      LargeScalePath.REMOTE_INVENTORY_FILE)

    def _collect_progress_json(self, start_cmd):
        start_time = time.time()
        while True:
            res, _ = self._is_process_existed(start_cmd)
            if not res:
                return
            res, _ = self._download_progress_config()
            if not res:
                continue
            time.sleep(self._ROUND_WAIT_TIME)
            if time.time() - start_time > self._MAX_WAIT_TIME:
                raise errors.LargeScaleDeployFailed(f"Host {self._remote_conn_info.ip} deploy time out.")

    def start(self):
        try:
            self._clear_remote_old_progress()
            self._send_inventory_file()
            start_cmd = f"bash {LargeScalePath.REMOTE_START_SCRIPT} {self._ascend_deployer_args}"
            self._start_deploy(start_cmd)
            self._collect_progress_json(start_cmd)
            if "test" in self._ascend_deployer_args:
                self._download_test_report()
            elif "check" in self._ascend_deployer_args:
                self._download_check_report()
                check_result_path = os.path.join(self._host_result_dir, "check_res_output.json")
                with open(os.path.join(self._host_result_dir, "check_res_output.json"), "r") as fid:
                    data = json.load(fid)
                if not self.check_host_status(data):
                    raise errors.LargeScaleDeployFailed(
                        f"Host {self._remote_conn_info.ip} check failed. Detail see {check_result_path}")
            elif "clean" in self._ascend_deployer_args:
                self._download_execute_failed_log()
                logger.info("The execute log is saved in {}/ascend_deployer_execute.log".format(self._host_result_dir))
            else:
                res, _ = self._download_progress_config()
                if not res:
                    self._download_execute_failed_log()
                    raise errors.LargeScaleDeployFailed(
                        f"Host {self._remote_conn_info.ip} generate progress report failed. Detail see"
                        f" {self._host_result_dir}/ascend_deployer_execute.log")
        except Exception as e:
            host_error = HostError(self._remote_conn_info.ip, [str(traceback.format_exc()), str(e)])
            self._error_que.put(host_error)
