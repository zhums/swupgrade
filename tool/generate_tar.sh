#!/bin/bash
set -e

TOOL_PATH=$(dirname $(readlink -f $0))

PKG_PATH=$(readlink -f $(dirname $(find ${TOOL_PATH}/.. -name upgrade.json)))
PKG_NAME=$(basename $(dirname $(find ${TOOL_PATH}/.. -name upgrade.json)))

UPGRADE_PATH=$(readlink -f ${PKG_PATH}/..)

cd ${UPGRADE_PATH}/..

tar --exclude .git --exclude template --exclude test -cvzf ${PKG_NAME}.tar.gz ${UPGRADE_PATH}
sha512sum ${PKG_NAME}.tar.gz > ${PKG_NAME}.sha512

echo
sha512sum -c upgrade-tarball-0.1.sha512
