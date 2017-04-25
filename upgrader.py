import json, sys
import glob, os
import os
import socket
import filecmp
from time import sleep
from netifaces import interfaces, ifaddresses, AF_INET
import datetime
import inspect

from collections import OrderedDict
flat = OrderedDict()
list_flag = False
init_load = True
new_list = False
token = ""
status_data = {}

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

def parser(prefix_key,jsn):
	global flat
	global list_flag
	global init_load
	global new_list
	for key in jsn.keys():
		if isinstance(jsn[key],dict):
			flat[str(key)] = jsn[key]
			prefix_key_dict = prefix_key
			prefix_key = prefix_key + "." + str(key)
			parser(prefix_key,jsn[key])
			prefix_key = prefix_key_dict
		elif isinstance(jsn[key],list):
			prefix_key_list = prefix_key
			prefix_key = prefix_key + "." + str(key)
			flat[prefix_key] = jsn[key]
			#TODO: Not support nest list yet
			list_flag = True
			new_list = True
			list_parser(prefix_key,jsn[key])
			list_flag = False
			new_list = False
			prefix_key = prefix_key_list
		else:
			key1 = str(prefix_key + "." + key)
			if (init_load == True or list_flag == True) and key1 in flat.keys():
				if new_list == True:
					flat[key1] = [str(jsn[key])]
				else:
					if not isinstance(flat[key1],list):
						flat[key1] = [str(flat[key1])]
					flat[key1].append(str(jsn[key]))
			else:
				if list_flag == True:
					flat[key1] = [str(jsn[key])]
				else:
					flat[key1] = str(jsn[key])

def list_parser(prefix_key,lst):
	global flat
	global new_list
	for element in lst:
		if isinstance(element,unicode):
			pass
		elif isinstance(element,list):
			list_parser(element)
		elif isinstance(element,dict):
			parser(prefix_key,element)
		new_list = False

def get_value(keys, *default):
	global flat
	value_array = flat
	if value_array.has_key(keys) == True:
		for key in keys.split(":"):
			value_array = value_array[key]
		print keys + " =", value_array
		if not isinstance(flat[keys],list):
			os.environ["user"+keys.upper().replace(".","_")]=value_array
		return value_array
	else:
		if not default:
			print "The key "+ keys + " is not found in the json file"
			sys.exit(1)
		else:
			values_str = ', '.join(str(x) for x in default)
			print keys + " =", values_str
			os.environ["user"+keys.upper().replace(".","_")]=values_str
			return values_str

def get_num(keys):
    global flat
    value_array = flat
    cnt = 0
    if value_array.has_key(keys) == True:
        cnt = 1
        if isinstance(flat[keys],list):
            cnt = len(flat[keys])
    print keys + ".num =", cnt
    return cnt

def set_value(keys, *value):
	global flat
	value_array = flat
	if value_array.has_key(keys) == True:
		for key in keys.split(":"):
			values_str = ', '.join(str(x) for x in value)
			flat[key] = values_str
	else:
		print "The key no exist"

def load_cfg():
	global init_load
	global status_data

	dirname, filename = os.path.split(os.path.abspath(__file__))
	os.environ["BASE_PATH"]=dirname
	os.environ["HOSTNAME"]=socket.gethostname()
	os.environ["SYSTEM_OS"]=dirname

	file = open("/etc/lsb-release","r")
	DISTRIB_ID = file.readlines()
	file.close()
	os.environ["SYSTEM_OS"] = DISTRIB_ID[0].strip()[11:]

	print os.environ["HOSTNAME"], ":", os.environ["BASE_PATH"], ":", os.environ["SYSTEM_OS"]

	if os.environ["SYSTEM_OS"] == "userOS":
		os.environ["INSECURE_PRIVATE_KEY"] = "/etc/ansible/insecure_private_key"
		os.environ["user_RELEASE"] = "/usr/share/ros/os-release"
	else:
		os.environ["INSECURE_PRIVATE_KEY"] = "/home/user/user/insecure_private_key"
		os.environ["user_RELEASE"] = "/etc/user-release"

	os.chdir(dirname)
	with open(os.environ["BASE_PATH"] + '/status.json', 'r') as f:
		status_data = json.load(f)
		print status_data

	for file in glob.glob("./*/upgrade.json"):
		dirname, filename = os.path.split(os.path.abspath(file))
		os.environ["TARBALL_PATH"]=dirname
		upgrade_file=dirname + "/upgrade.json"
		print upgrade_file
		json_file = open(upgrade_file,'r')
		json_contents = json.loads(json_file.read(),object_pairs_hook=OrderedDict)
		parser("",json_contents)
		json_file.close()
		init_load = False
		break

	for index in range(1,len(sys.argv)):
		upgrade_file=sys.argv[index]
		print upgrade_file
		json_file = open(upgrade_file,'r')
		json_contents = json.loads(json_file.read(),object_pairs_hook=OrderedDict)
		parser("",json_contents)
		json_file.close()
		init_load = False

def check_permission():
	user = os.getenv("SUDO_USER")
	if user is not None:
		log_status("=========================START UPGRADE=======================")
		update_status("status", "START_UPGRADE")
	else:
		log_status("This program need 'sudo' permission!")
		update_status("status", "FAILURE")
		sys.exit(1)

def upgrade_execute(cmd):
	ERR = os.system(cmd)
	if ERR != 0:
		log_status("=========================Failure=======================")
		log_status("COMMAND[" + cmd + "] failed !")
		update_status("status", "FAILURE")
		sys.exit(1)

def log_status(msg):
	os.system("echo [" + os.environ["HOSTNAME"] + "] " + msg + " | tee -a " + os.environ["BASE_PATH"] + "/status.txt")
	os.system(os.environ["BASE_PATH"] + "/common/sync.sh")

def wait_for_token(timeout):
    global token
    log_status("=========================Waiting For Token=======================")
    cnt = 0
    while True:
        #os.system("echo " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  + " >>  " + os.environ["BASE_PATH"] + "/time.txt")
        if os.path.exists(os.environ["BASE_PATH"] + "/token") == True:
            file = open(os.environ["BASE_PATH"] + "/token","r")
            token_temp = str(file.read()).strip()
            file.close()
            if token != token_temp:
                token = token_temp
                log_status("=========================Received token: " + token + "=======================")

                if True == filecmp.cmp(os.environ["BASE_PATH"] + "/token", os.environ["BASE_PATH"] + "/self_node"):
                    update_status("token", token)
                    break
        if cnt < timeout:
            sleep(1)
        else:
            log_status("=========================Waiting For Token: timeout=======================")
            sys.exit(1)
        cnt = cnt + 1

def pass_token():
    global token
    log_status("=========================Passed Token=======================")
    update_status("status", "PASSED_TOKEN")
    file = open(os.environ["BASE_PATH"] + "/token_queque_list","r")
    token_queuque_list = file.read().split()
    file.close()
    for index in range(len(token_queuque_list)):
        if token == token_queuque_list[index]:
            index = index + 1
            if index == len(token_queuque_list):
                log_status("=========================END OF UPGRADE @ " + token + "=======================")
                update_status("status", "END_OF_UPGRADE")
                os.system("echo -n  > %s " % (os.environ["BASE_PATH"] + "/token"))
                os.system(os.environ["BASE_PATH"] + "/common/sync.sh with_token")
            else:
                token = str(token_queuque_list[index])
                log_status("=========================Next Token: " + token + " =======================")
                os.system("echo " + str(token) + " > " + os.environ["BASE_PATH"] + "/token")
                update_status("status", "Initilization")
                update_status("package_name", "")
                update_status("progress_val", 0)
                #After this point, should not  have any data sync with other nodes from this node
                update_status('token', token, "sync")
            break

def init_token():
	global token
	token = ""
	#if os.path.exists(os.environ["BASE_PATH"] + "/token") == True:
	#	file = open(os.environ["BASE_PATH"] + "/token","r")
	#	token = str(file.read()).strip()
	#	file.close()

def set_nodeip():
	node_list = get_value(".node_list")
	for ifaceName in interfaces():
		if ifaceName != "lo":
			addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
			if addresses[0] in [x.encode('UTF8') for x in node_list]:
				os.environ["NODENAME"] = addresses[0]
				return
	sys.exit(1)

def update_status(key, value, *option):
	global status_data
	status_data[key] = value
	with open(os.environ["BASE_PATH"] + '/status.json', 'w') as f:
		json.dump(status_data, f, indent=4)
		os.system(os.environ["BASE_PATH"] + "/common/sync.sh")

	if option:
		values_str = ', '.join(str(x) for x in option)
		if values_str == "sync":
			os.system(os.environ["BASE_PATH"] + "/common/sync.sh with_token")

def post_action(action):
	os.system("touch " + os.environ["BASE_PATH"] + "/" + action +"_DONE")

def pre_action(action):
	if os.path.exists(os.environ["BASE_PATH"] + "/" + action +"_DONE") == True:
		log_status(action + " has already been done!")
		return False
	else:
		return True

def main():
	try:
		#TODO: VERSION display
		load_cfg()
		#TODO: sync new token/new status/new bar

		debug_python = get_value(".debug.python")
		debug_shell = get_value(".debug.shell")
		if debug_shell == "True":
			os.environ["UPGRADE_DEBUG"] = "true"
		else:
			os.environ["UPGRADE_DEBUG"] = "false"

		upgrade_host = get_value(".upgrade_host", "")
		node_list = get_value(".node_list")
		node_list_num = get_num(".node_list")
		if not node_list:
			#TODO: auto-generate
			print "Missing node list!"
		else:
			os.environ["NODE_LIST"] = ' '.join(map(str, node_list))

		if not upgrade_host in node_list:
			os.environ["UPGRADE_HOST"] = upgrade_host

		set_nodeip()

		upgrader_version = get_value(".upgrader_version")
		timeout = (int(get_value(".timeout"))*node_list_num)
        	print "timeout = ", timeout
		iso_version = get_value(".pre_check.iso_version")
		cur_version = get_value(".pre_check.cur_version")
		upgrade_version = get_value(".pre_check.upgrade_version")
		service_off = get_value(".pre_check.service_off")
		service_off_confirmation = get_value(".pre_check.service_off_confirmation", "False")
		rollback = get_value(".pre_check.rollback", "False")
		snapshot = get_value(".snapshot")
		package_name = get_value(".upgrade.package_list.package_name")
		pkg_service_off = get_value(".upgrade.package_list.pkg_service_off")
		#pkg_rollback = get_value(".upgrade.package_list.pkg_rollback", rollback)
		pkg_cur_ver = get_value(".upgrade.package_list.pkg_cur_ver")
		pkg_upgrade_ver = get_value(".upgrade.package_list.pkg_upgrade_ver")
		reboot = get_value(".upgrade.reboot")
		snapshot_check = get_value(".snapshot_check")
		post_check = get_value(".post_check")
		clean = get_value(".clean")
		os.system("printenv")

		check_permission()

		if service_off == "True" and  service_off_confirmation == "False":
			log_status("=========================Failure=======================")
			update_status("status", "FAILURE")
			log_status("System need turn off Service for this upgrade, please check the responding checkbox !")
			sys.exit(1)

		os.chdir(os.environ["TARBALL_PATH"])
		if rollback == "False":
			os.environ["BACKUP_PATH"]="/home/user/tarball/tarball_" + cur_version + "-" + upgrade_version + "_backup"
			os.system("mkdir -p " + os.environ["BACKUP_PATH"])
		else:
			os.environ["BACKUP_PATH"]="/home/user/tarball/tarball_" + upgrade_version + "-" + cur_version + "_backup"

		if pre_action("PRE_CHECK") == True:
			print "\r\n======================================PRE-CEHCK======================================"
			update_status("status", "PRE_CHECK")
			upgrade_execute("../pre_check.sh ")
			for index in range(len(package_name)):
				os.environ["user_UPGRADE_PACKAGE_LIST_PACKAGE_NAME"] = package_name[index]
				os.environ["user_UPGRADE_PACKAGE_LIST_PKG_SERVICE_OFF"] = pkg_service_off[index]
				os.environ["user_UPGRADE_PACKAGE_LIST_PKG_CUR_VER"] = pkg_cur_ver[index]
				os.environ["user_UPGRADE_PACKAGE_LIST_PKG_UPGRADE_VER"] = pkg_upgrade_ver[index]
				upgrade_execute("./deploy_pkg/" + package_name[index] + "/pre_check.sh " + " " + pkg_cur_ver[index] + " " + pkg_upgrade_ver[index])
			post_action("PRE_CHECK")

		if snapshot == "True" and   pre_action("SNAPSHOT") == True:
			print "\r\n======================================SNAPSHOT======================================"
			update_status("status", "SNAPSHOT")
			upgrade_execute("../snapshot.sh ")
			post_action("SNAPSHOT")

		init_token()
		wait_for_token(timeout)
		#TODO: modulize the function block

		progress_scale = 100 / (3 * len(package_name) + 5)
		progress_val = progress_scale
		update_status("progress_val", progress_val)
		if pre_action("UPGRADE") == True:
			print "\r\n======================================UPGRADE======================================"
			update_status("status", "UPGRADING")
			for index in range(len(package_name)):
				os.environ["user_UPGRADE_PACKAGE_LIST_PACKAGE_NAME"] = package_name[index]
				os.environ["user_UPGRADE_PACKAGE_LIST_PKG_SERVICE_OFF"] = pkg_service_off[index]
				os.environ["user_UPGRADE_PACKAGE_LIST_PKG_CUR_VER"] = pkg_cur_ver[index]
				os.environ["user_UPGRADE_PACKAGE_LIST_PKG_UPGRADE_VER"] = pkg_upgrade_ver[index]
				update_status("package_name", package_name[index])
				print "\r\n============Processing package_name[" + package_name[index] + "]===========\r\n"
				upgrade_execute("./deploy_pkg/" + package_name[index] + "/backup.sh " + pkg_service_off[index] + " " + rollback)
				progress_val = progress_val + progress_scale
				update_status("progress_val", progress_val)
				upgrade_execute("./deploy_pkg/" + package_name[index] + "/deploy.sh " + " " + rollback + " " + pkg_cur_ver[index] + " " + pkg_upgrade_ver[index])
				progress_val = progress_val + progress_scale
				update_status("progress_val", progress_val)
				upgrade_execute("./deploy_pkg/" + package_name[index] + "/post_check.sh " + pkg_service_off[index]  + " "  + rollback + " " + pkg_cur_ver[index] + " " + pkg_upgrade_ver[index])
				progress_val = progress_val + progress_scale
				update_status("progress_val", progress_val)
			post_action("UPGRADE")
        	update_status("package_name", "")

		if reboot == "True" and pre_action("REBOOT") == True:
			print "\r\n======================================Reboot======================================"
			update_status("status", "REBOOT")
			post_action("REBOOT")
			upgrade_execute("reboot")
			sys.exit(1)
		progress_val = progress_val + progress_scale
		update_status("progress_val", progress_val)

		if snapshot_check == "True" and  pre_action("SNAPSHOT_CEHCK") == True:
			print "\r\n======================================SNAPSHOT-CEHCK======================================"
			update_status("status", "SNAPSHOT_CEHCK")
			upgrade_execute("../snapshot_check.sh ")
			post_action("SNAPSHOT_CEHCK")
		progress_val = progress_val + progress_scale
		update_status("progress_val", progress_val)

		if post_check == "True" and pre_action("POST_CHECK") == True:
			print "\r\n======================================POST_CHECK======================================"
			update_status("status", "POST_CHECK")
			upgrade_execute("../post_check.sh" + " " + rollback + " " + upgrade_version)
			post_action("POST_CHECK")
		progress_val = progress_val + progress_scale
		update_status("progress_val", progress_val)

		if clean == "True" and pre_action("CLEAN") == True:
			print "\r\n======================================CLEAN======================================"
			update_status("status", "CLEAN")
			upgrade_execute("../common/clean.sh")
			post_action("CLEAN")

		update_status("progress_val", 100)
        #After the below function, should not  have any data sync with other nodes
		pass_token()

		if os.environ["SYSTEM_OS"] == "userOS":
			upgrade_execute("sudo rm -f /var/lib/rancher/conf/upgrade.sh || :")
		else:
			upgrade_execute("sudo update-rc.d -f upgrade.sh remove 2>/dev/null || :")
	except Exception as ex:
		template = "An exception of type {0} occured. Arguments:\n{1!r}"
		message = template.format(type(ex).__name__, ex.args)
		print message

if __name__ == "__main__":
	main()
