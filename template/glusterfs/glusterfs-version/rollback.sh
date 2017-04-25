#!/bin/bash
source ${BASE_PATH}/common/pre_set.sh

deb_ver=$(echo ${user_UPGRADE_PACKAGE_LIST_PKG_UPGRADE_VER} | sed 's/^.*__//g')

dpkg --force-confold --force-confdef --force-confmiss --force-overwrite -i glusterfs_${deb_ver}.deb
ldconfig

source ${BASE_PATH}/common/status.sh ""
