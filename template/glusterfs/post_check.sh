#!/bin/bash

source ${BASE_PATH}/common/pre_set.sh

#===============================================================================
function service_start()
{
    echo "=========================SERVICE START GlusterFS======================="
    service glusterd start
    [ -z "$(ps aux | grep "gluster" | grep -wv "grep\|sh\|bash")" ] && source ${BASE_PATH}/common/status.sh "Failed to start GlusterFS" && exit 1
    gluster peer status
    gluster volume status
    gluster volume info

    echo "=========================SERVICE START NFS Ganesha======================="
    daemon -r --command="/usr/bin/ganesha.nfsd -F -f /etc/ganesha/ganesha.conf -L /var/log/ganesha.log"
    retry=5 && while [ $retry -gt 0 ];do showmount -e && retry=0 || retry=$((retry-1));sleep 1;done

    for nfs_create in $(ls /var/user/resources/nfs_exports/ 2>/dev/null); do
        "/var/user/resources/nfs_exports/$nfs_create"
    done

    [ -z "$(ps aux | grep -v "grep" | grep "ganesha")" ] && source ${BASE_PATH}/common/status.sh "Failed to start NFS Ganesha" && exit 1
    showmount -e localhost
}

function rollback_start()
{
    echo "=========================ROLLBACK START======================="
    pkg_name=$(basename $(dirname $0))
    tar -C / -xvzf ${BACKUP_PATH}/${pkg_name}.tar.gz
}

function version_check()
{
    echo "========New version========="
    echo
    glusterd --version
    echo
    echo "============================"
    upgrade_major_ver=$(echo ${user_UPGRADE_PACKAGE_LIST_PKG_UPGRADE_VER} | sed 's/__.*$//g')

    [ "$(glusterd --version | grep built | awk '{print $2}')" != "${upgrade_major_ver}" ] && {
        echo "For this upgrade, Current version should be glusterfs ${upgrade_major_ver} "
        exit 1
    }
}

function vip_monitor_start()
{
    echo "=========================TODO: VIP/Monitor START======================="
}
#===============================================================================

[ ${user_PRE_CHECK_ROLLBACK} == "True" ] && rollback_start
[ ${user_UPGRADE_PACKAGE_LIST_PKG_SERVICE_OFF} == "True" ] && service_start && vip_monitor_start

version_check || :

source ${BASE_PATH}/common/status.sh ""
