#!/bin/bash

#TODO
#rm /tmp/log.txt

echo
echo [$(date)@$(hostname)] =============================SUCCESSFULLY COMPLETED======================= | tee -a ${BASE_PATH}/status.txt

${BASE_PATH}/common/sync.sh with_token
