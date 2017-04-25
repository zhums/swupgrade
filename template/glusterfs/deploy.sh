#!/bin/bash
source ${BASE_PATH}/common/pre_set.sh

#===============================================================================
function deploy()
{
	pushd . > /dev/null
	for path  in $(find . -maxdepth 1 -type d | sort);do
		[ $path == "." ] && continue
		cd ${path}
		./uninstall.sh
		if [ ${user_PRE_CHECK_ROLLBACK} == "False" ]; then
			./install.sh
		else
			./rollback.sh
		fi
		cd ..
	done
	popd > /dev/null
}

#===============================================================================

deploy

source ${BASE_PATH}/common/status.sh ""
#source ${BASE_PATH}/common/status.sh "Rebooting ..."
#echo "[$(hostname)] Start inexplicitly reboot ..."
#reboot && sleep 60
