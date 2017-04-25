#!/bin/bash

source ${BASE_PATH}/common/pre_set.sh

cd ${TARBALL_PATH}/deploy_pkg
for path  in $(find . -maxdepth 1 -type d);do
    [ $path == "." ] && continue
    [ -f ${path}/snapshot.sh ] && ${path}/snapshot.sh
done

source ${BASE_PATH}/common/status.sh ""
