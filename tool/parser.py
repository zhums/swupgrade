import json, sys
from collections import OrderedDict
flat = OrderedDict()
def parser(jsn):
	global flat
	for key in jsn.keys():
		if isinstance(jsn[key],dict):
			flat[key] = jsn[key]
			parser(jsn[key])
		elif isinstance(jsn[key],list):
			flat[str(key)] = jsn[key]
			list_parser(jsn[key])
		else:
			if str(key) in flat.keys():
				if not isinstance(flat[key],list):
					flat[key] = [flat[key]]
				flat[key].append(jsn[key])
			else:
				flat[key] = jsn[key]
def list_parser(lst):
	global flat
	for element in lst:
		if isinstance(element,unicode):
			pass
		elif isinstance(element,list):
			list_parser(element)
		elif isinstance(element,dict):
			parser(element)

def get_next(dct,key):
	if isinstance(dct,list):
		for item in dct:
			dct = get_next(item,key)
	elif isinstance(dct,OrderedDict):
		if key in dct.keys():
			return dct[key]
		print "The key "+ key + " is not found in the "+str(dict(value))+" json"
	return dct

length = len(sys.argv)

if length == 1 or sys.argv[-1].lower() == "help":
	print "Usage: python parser.py file.json key[:subkey[:subkey]] [index]"
	print "Example: python parser.py upgrade.json command 0"
	print "Example: python parser.py upgrade.json post_script:package_list"
	sys.exit(0)
if length > 1:
	json_file = open(sys.argv[1],'r')
	json_contents = json.loads(json_file.read(),object_pairs_hook=OrderedDict)
	parser(json_contents)
	if length > 2:
		keys = sys.argv[2]
		num = None
		if length > 3 and sys.argv[3].isdigit():
			num = int(sys.argv[3])
	else:
		print "Please provide a key to search the json for"
		print flat
		sys.exit(0)
else:
	print "Please provide a json file to parse"
	sys.exit(0)


value = flat
try:
	for key in keys.split(":"):
		value = get_next(value,key)
	if num is not None:
		value = value[num-1]
	print value
except IndexError:
	print "There are less than "+str(num)+" values in the list"
