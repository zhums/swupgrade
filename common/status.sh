#!/bin/bash

echo

if [ -z "$1" ]; then
    echo [$(date)@$(hostname)] Completed:  $CUR_PATH/$0 : $@ | tee -a ${BASE_PATH}/status.txt
else
    echo [$(date)@$(hostname)] InProgress:  $CUR_PATH/$0 : $@ | tee -a ${BASE_PATH}/status.txt
#    echo [$(date)@$(hostname)] InProgress:  $CUR_PATH/$0 $@ : $1 | tee -a ${BASE_PATH}/status.txt
fi

${BASE_PATH}/common/sync.sh
touch ${ACTION}_DONE
