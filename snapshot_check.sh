#!/bin/bash

source ${BASE_PATH}/common/pre_set.sh

cd ${TARBALL_PATH}/deploy_pkg
for path  in $(find . -maxdepth 1 -type d);do
    [ $path == "." ] && continue
    [ -f ${path}/snapshot_check.sh ] && ${path}/snapshot_check.sh
done

source ${BASE_PATH}/common/status.sh ""
