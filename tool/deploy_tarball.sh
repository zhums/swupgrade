#!/bin/bash
set -e
#set -x
#TODO: Clean up

if [ "$(cat /etc/lsb-release  | grep DISTRIB_ID | cut -d"=" -f2)" == "userOS" ]; then
    export SYSTEM_OS="userOS"
    export INSECURE_PRIVATE_KEY="/etc/ansible/insecure_private_key"
else
    export SYSTEM_OS="Ubuntu"
    export INSECURE_PRIVATE_KEY="/home/user/user/insecure_private_key"
fi

PKG_PATH=$(readlink -f $(dirname $(find /home/user/user-swupgrade/ -name upgrade.json)))
TARBALL_NAME=$(basename ${PKG_PATH})

debug_python=$(jq '.debug.python'  ${PKG_PATH}/customer.json | sort -u | tr -d '"')

cd /home/user/user-swupgrade
sudo rm -f rest_node_list log self_node token token1 token_queque_list status.txt time.txt nohup.out $(find . -name "*DONE") || :
echo > status.txt
cat << EOF > status.json
{
    "status": "Initilization",
    "package_name": "",
    "token": "",
    "progress_val": 0
}
EOF

i=0
while true;do
    [ $(jq '.node_list | length'  ${PKG_PATH}/customer.json) -eq $i ] && break
    node=$(jq '.node_list['$i']'  ${PKG_PATH}/customer.json | sort -u | tr -d '"')

    ssh -oPasswordAuthentication=no -oBatchMode=yes -o "StrictHostKeyChecking no" -i ${INSECURE_PRIVATE_KEY} user@${node}  "hostname" || exit 1
    remains=$(ssh -i ${INSECURE_PRIVATE_KEY} user@$node ps aux | grep "python upgrader.py" | grep customer.json | awk '{print $2}')
    echo Killing remain application $remains on node ${node}
    [ ! -z "${remains}" ] && ssh -i ${INSECURE_PRIVATE_KEY} user@$node sudo kill -9 $remains || :

    ifconfig | grep $node || {
        echo Deploying $node ...
        ssh -i ${INSECURE_PRIVATE_KEY} user@$node sudo rm -rf /home/user/user-swupgrade
        rsync -re "ssh -i ${INSECURE_PRIVATE_KEY}" /home/user/user-swupgrade user@${node}:/home/user/
    }

    i=$((i+1))
done

sleep 2

i=0
while true;do
    [ $(jq '.node_list | length'  ${PKG_PATH}/customer.json) -eq $i ] && break
    node=$(jq '.node_list['$i']'  ${PKG_PATH}/customer.json | sort -u | tr -d '"')
    if [ "$i" == "0" ]; then
        first_node=${node}
        echo ${first_node} > /home/user/user-swupgrade/token1
    else
        rsync -e "ssh -i ${INSECURE_PRIVATE_KEY}" /home/user/user-swupgrade/token1 user@${node}:/home/user/user-swupgrade/token
    fi

    i=$((i+1))
    if [ "$debug_python" == "true" ]; then
        if [ "$VERBOSE" == "true" ]; then
            ssh -f -i ${INSECURE_PRIVATE_KEY} user@$node 'cd /home/user/user-swupgrade;sudo nohup script -af log -c "python -m trace --trace  upgrader.py '${TARBALL_NAME}'/customer.json"&'
        else
            ssh -f -i ${INSECURE_PRIVATE_KEY} user@$node 'cd /home/user/user-swupgrade;sudo nohup script -af log -c "python -m trace --trace  upgrader.py '${TARBALL_NAME}'/customer.json"  > /dev/null 2>&1 &'
        fi
        echo 'cd /home/user/user-swupgrade;sudo script -af log -c "python -m trace --trace  upgrader.py '${TARBALL_NAME}'/customer.json"&' > /home/user/user-swupgrade/upgrade.sh
    else
        if [ "$VERBOSE" == "true" ]; then
            ssh -f -i ${INSECURE_PRIVATE_KEY} user@$node 'cd /home/user/user-swupgrade;sudo nohup script -af log -c "python upgrader.py '${TARBALL_NAME}'/customer.json"&'
        else
            ssh -f -i ${INSECURE_PRIVATE_KEY} user@$node 'cd /home/user/user-swupgrade;sudo nohup script -af log -c "python upgrader.py '${TARBALL_NAME}'/customer.json"  > /dev/null 2>&1 &'
        fi
        echo 'cd /home/user/user-swupgrade;sudo script -af log -c "python upgrader.py '${TARBALL_NAME}'/customer.json"&' > /home/user/user-swupgrade/upgrade.sh
    fi
    echo "Started upgrade application on node ${node}, Waiting For Token ..."
    sleep 2
    j=0
    while [ "$(grep "Waiting For Token" status.txt | wc -l)" != "$i" ] ; do
        sleep 1
        j=$((j+1))
        if [ $j -eq 100 ]; then
            echo Failed to receive started message from ${node}. | tee -a /home/user/user-swupgrade/status.txt
            exit 1
        fi
    done
done

i=0
while true;do
    [ $(jq '.node_list | length'  ${PKG_PATH}/customer.json) -eq $i ] && break
    node=$(jq '.node_list['$i']'  ${PKG_PATH}/customer.json | sort -u | tr -d '"')

    echo "Set up reboot/resume on node ${node} ..."
    chmod 755 /home/user/user-swupgrade/upgrade.sh
    rsync -re "ssh -i ${INSECURE_PRIVATE_KEY}" /home/user/user-swupgrade/upgrade.sh user@${node}:/home/user/user-swupgrade/upgrade.sh

    if [ "${SYSTEM_OS}" == "userOS" ]; then
        ssh -i ${INSECURE_PRIVATE_KEY} user@$node 'sudo ln -snf /home/user/user-swupgrade/upgrade.sh /var/lib/rancher/conf/upgrade.sh || :'
    else
        ssh -i ${INSECURE_PRIVATE_KEY} user@$node 'sudo ln -snf /home/user/user-swupgrade/upgrade.sh /etc/init.d/upgrade.sh || :'
        ssh -i ${INSECURE_PRIVATE_KEY} user@$node 'sudo update-rc.d -f upgrade.sh defaults 99 || :'
    fi
    i=$((i+1))
done

rsync -e "ssh -i ${INSECURE_PRIVATE_KEY}" /home/user/user-swupgrade/token1 user@${first_node}:/home/user/user-swupgrade/token
rm /home/user/user-swupgrade/token1
