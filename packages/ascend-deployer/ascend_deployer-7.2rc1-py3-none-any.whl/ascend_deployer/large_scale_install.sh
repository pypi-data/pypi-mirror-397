#!/bin/bash
readonly BASE_DIR=$(
    cd "$(dirname $0)" >/dev/null 2>&1
    pwd -P
)

main() {
    if [[ -f ~/.local/ascend_deployer_rc ]]; then
      source ~/.local/ascend_deployer_rc
    fi
    python3 -V > /dev/null 2>&1
    if [[ $? != 0 ]]; then
      echo "[ASCEND ERROR] Large-scale deployment scenarios only support Python 3"
    else
      python3 ${BASE_DIR}/large_scale_deployer.py $*
    fi
}

main $*
main_status=$?
exit ${main_status}
