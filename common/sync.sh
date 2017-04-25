#!/bin/bash
set -e
[ "${UPGRADE_DEBUG}" == "true" ] && set -x

[ -f ${BASE_PATH}/rest_node_list ] || exit 0

for node in $UPGRADE_HOST $(cat ${BASE_PATH}/rest_node_list);do
    echo [${HOSTNAME}] syncing status to $node ...
    #[ -f ${BASE_PATH}/status.txt ] && cat ${BASE_PATH}/status.json || :
    ssh -oPasswordAuthentication=no -oBatchMode=yes -o "StrictHostKeyChecking no" -i ${INSECURE_PRIVATE_KEY} user@${node}  "hostname"
    [ -f ${BASE_PATH}/status.txt ] && rsync -e "ssh -i ${INSECURE_PRIVATE_KEY}" ${BASE_PATH}/status.txt user@${node}:${BASE_PATH}/status.txt || :
    [ -f ${BASE_PATH}/status.json ] && rsync -e "ssh -i ${INSECURE_PRIVATE_KEY}" ${BASE_PATH}/status.json user@${node}:${BASE_PATH}/status.json
done

if [ "$1" == "with_token" ]; then
    for node in $UPGRADE_HOST $(cat ${BASE_PATH}/rest_node_list);do
        echo [${HOSTNAME}] syncing token to $node ...
        [ -f ${BASE_PATH}/token ] && rsync -e "ssh -i ${INSECURE_PRIVATE_KEY}" ${BASE_PATH}/token user@${node}:${BASE_PATH}/token
    done
fi
