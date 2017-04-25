#!/bin/bash

source ${BASE_PATH}/common/pre_set.sh

#===============================================================================
function version_check()
{
    echo "========Current package version $(cat VERSION)========="

    if [ ${user_PRE_CHECK_ROLLBACK} == "True" ]; then
        check_ver=${user_UPGRADE_PACKAGE_LIST_PKG_CUR_VER}
    else
        check_ver=${user_UPGRADE_PACKAGE_LIST_PKG_UPGRADE_VER}
    fi

    [ "$(cat VERSION)" != "${check_ver}" ] && {
        echo "For this upgrade, Current package version should be glusterfs ${check_ver} "
        exit 1
    }

    echo "========Current application version========="
    echo
    glusterd --version
    echo
    echo "================================"
    cur_major_ver=$(echo ${user_UPGRADE_PACKAGE_LIST_PKG_CUR_VER} | sed 's/__.*$//g')

    [ "$(glusterd --version | grep built | awk '{print $2}')" != "${cur_major_ver}" ] && {
        echo "For this upgrade, Current version should be glusterfs ${cur_major_ver} "
        exit 1
    }
}
#===============================================================================

version_check || :

for path  in $(find . -maxdepth 1 -type d);do
    [ $path == "." ] && continue
    [ -f ${path}/pre_check.sh ] && ${path}/pre_check.sh
done

source ${BASE_PATH}/common/status.sh ""
