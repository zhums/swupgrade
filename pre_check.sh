#!/bin/bash

source ${BASE_PATH}/common/pre_set.sh

iso_version=${user_PRE_CHECK_ISO_VERSION}
upgrade_cur_version=${user_PRE_CHECK_CUR_VERSION}
upgrade_version=${user_PRE_CHECK_UPGRADE_VERSION}
rollback=${user_PRE_CHECK_ROLLBACK}
node_list=${NODE_LIST}
echo node_list $node_list


if [ "${SYSTEM_OS}" == "userOS" ]; then
	cur_iso_version=$(cat ${user_RELEASE} | grep  VERSION_ID | cut -d"=" -f2)
else
	cur_iso_version=$(cat ${user_RELEASE} | grep  user_RELEASE | cut -d"=" -f2)
fi
if [ "${cur_iso_version}" != "${iso_version}" ]; then
	echo "Running nodes ISO version: $cur_iso_version does not match with this upgrade base ISO version： $iso_version"
	exit 1
fi

[ ! -d $(dirname ${TARBALL_RELEASE}) ] && mkdir $(dirname ${TARBALL_RELEASE})
[ ! -f ${TARBALL_RELEASE} -a \( -z "$upgrade_cur_version" -o "$upgrade_cur_version" == "0.0" \) ] && echo 0.0 > ${TARBALL_RELEASE}
cur_version=$(cat ${TARBALL_RELEASE})
if [ "$cur_version" != "$upgrade_cur_version" ]; then
	echo "Running nodes current version: $cur_version does not match with this upgrade request version： $upgrade_cur_version"
	exit 1
fi

tarball_version=$(cat ${TARBALL_PATH}/VERSION)
if [ "$rollback" == "True" ]; then
	if [ "$tarball_version" != "$upgrade_cur_version" ]; then
		echo "Running nodes tarball version: $tarball_version does not match with this current version： $upgrade_cur_version"
		exit 1
	fi
else
	if [ "$tarball_version" != "$upgrade_version" ]; then
		echo "Running nodes tarball version: $tarball_version does not match with this upgrade request version： $upgrade_version"
		exit 1
	fi
fi

if [ "$rollback" == "True" ] && [ ! -d ${BACKUP_PATH} ]; then
	echo "Rollback path: $BACKUP_PATH does not exist"
	exit 1
else
	cp ${TARBALL_PATH}/VERSION ${BACKUP_PATH}/
	cp ${TARBALL_PATH}/*.json ${BACKUP_PATH}/
fi

rm -f ${BASE_PATH}/rest_node_list
touch ${BASE_PATH}/rest_node_list
for node in $node_list; do
	#self=$(ifconfig | grep ${node} || :)
	if [ $node != $NODENAME ]; then
		echo "Checking node $node ..."
		echo $node  >> ${BASE_PATH}/rest_node_list
		ssh -oPasswordAuthentication=no -oBatchMode=yes -o "StrictHostKeyChecking no" -i ${INSECURE_PRIVATE_KEY} user@${node}  "hostname && exit" || exit 1
	else
		echo $node  > ${BASE_PATH}/self_node
	fi
done

[ ! -z "${UPGRADE_HOST}" ] && ssh -oPasswordAuthentication=no -oBatchMode=yes -o "StrictHostKeyChecking no" -i ${INSECURE_PRIVATE_KEY} user@${UPGRADE_HOST}  "hostname && exit"

echo $node_list >  ${BASE_PATH}/token_queque_list

source ${BASE_PATH}/common/status.sh ""
