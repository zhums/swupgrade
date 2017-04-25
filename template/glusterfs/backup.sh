#!/bin/bash

source ${BASE_PATH}/common/pre_set.sh

#===============================================================================
function service__stop()
{
    echo "=========================SERVICE STOP NFS Ganesha======================="
    nfs_pids=$(ps aux | grep "ganesha" | grep -v "grep" | awk '{print $2}')
    [ ! -z "${nfs_pids}" ] && {
        kill -9 ${nfs_pids}
        ps aux | grep "ganesha" | grep -wv "grep\|sh\|bash"
    }

    echo "=========================SERVICE STOP GlusterFS======================="
    service glusterd stop
    service glusterd status
    killall glusterfsd glusterfs
    ps aux | grep -v "grep\|backup" | grep "gluster"
}

function backup()
{
    echo "=========================BACKUP======================="
    mkdir -p /var/user/resources/nfs_exports /etc/user/nfs
    tar -cvzf ${BACKUP_PATH}/${user_UPGRADE_PACKAGE_LIST_PACKAGE_NAME}.tar.gz /etc/ganesha /etc/user/nfs /var/user/resources/nfs_exports
}

function vip_monitor_stop()
{
    echo "=========================TODO: VIP/Monitor STOP======================="
}
#===============================================================================

[ ${user_UPGRADE_PACKAGE_LIST_PKG_SERVICE_OFF} == "True" ] && vip_monitor_stop && service__stop || :
[ ${user_PRE_CHECK_ROLLBACK} == "False" ] && backup

source ${BASE_PATH}/common/status.sh ""
