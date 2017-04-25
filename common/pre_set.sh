#!/bin/bash

set -e
source ${BASE_PATH}/common/exports.sh

[ "${UPGRADE_DEBUG}" == "true" ] && set -x

CUR_PATH=$(pwd)

cd $(dirname $0)

ACTION=$(basename $0 | tr '[:lower:]' '[:upper:]' | cut -d'.' -f1)

echo "[$(date)@$(hostname)] Processing: $CUR_PATH/$0 $@ " | tee -a ${BASE_PATH}/status.txt

[ -f ${ACTION}_DONE ] && {
    echo [$(date)@$(hostname)] Already Completed:  $CUR_PATH/$0 $@ | tee -a ${BASE_PATH}/status.txt
}

#[ "$(basename $0)" == "deploy.sh" -a -f DONE ] && {
#    echo [$(date)@$(hostname)] Already Completed:  $CUR_PATH/$0 $@ | tee -a ${BASE_PATH}/status.txt
#}

${BASE_PATH}/common/sync.sh

[ -f ${ACTION}_DONE ] && exit $? || :
