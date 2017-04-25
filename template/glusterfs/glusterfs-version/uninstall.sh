#!/bin/bash
source ${BASE_PATH}/common/pre_set.sh

dpkg -r glusterfs

source ${BASE_PATH}/common/status.sh ""
