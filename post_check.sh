#!/bin/bash

source ${BASE_PATH}/common/pre_set.sh

upgrade_version=${user_PRE_CHECK_UPGRADE_VERSION}
rollback=${user_PRE_CHECK_ROLLBACK}

#TODO: tracking tarball version with rollback
[ $rollback == "False" ] && {
    cat ${TARBALL_PATH}/VERSION > ${TARBALL_RELEASE}
} || {
    echo ${upgrade_version} > ${TARBALL_RELEASE}
}

source ${BASE_PATH}/common/status.sh ""
