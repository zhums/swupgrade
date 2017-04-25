from subprocess import Popen, PIPE
import sys

#Converts a string to a boolean
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

#Runs the bash command given to it
def runProcess(command):
	process = Popen(command.split(), stdout=PIPE)
	output, error = process.communicate()
	return output

#packageName=name of debian package to download
#downloaded=list of packages currently downloaded
#dry=boolean. if true, won't download, will just list files it will download
def getPackage(packageName, downloaded, dry):

	#Downloading the debian	
	if not dry:
		runProcess("sudo apt-get download "+ packageName)

	print "Downloading "+packageName
	downloaded.append(packageName)

	#Getting the dependencies of the debian
	depends = ["".join(line.split()) for line in runProcess("sudo apt-cache depends "+ packageName).split('\n')]
	
	#Iterating through the dependencies
	for dependency in depends:

		#Get the package name seperate from the Depends tag
		split = dependency.split(':')

		#If it is a Depends tag, and there's two values and we havn't already downloaded it and it's not one of those weird generic package names
		if split[0] == "Depends" and len(split) == 2 and split[1] not in downloaded and "<" not in split[1]:

			#recursively call this function with each dependency
			downloaded = getPackage(split[1], downloaded, dry)

	return downloaded

if len(sys.argv) == 1 or sys.argv[-1].lower() == "help":
	print "Usage: python tarball.py package1 package2 package3 ... packageN true/false"
	print "The last parameter is whether you want to run it dry or not. True will only list files that would be downloaded. False will download them."

try:
	dry = str2bool(sys.argv[-1])
except:
	dry = False
for i in range(1,len(sys.argv)-1):
	#Setting parameter variables
	packageName = sys.argv[i]

	#Calling the initial function
	downloaded = getPackage(packageName,[],dry)
	
	if not dry:

		#Creating a directory for the package
		runProcess("mkdir -p "+packageName)
		
		#Getting all files in current directory
		ls = runProcess('ls').split('\n')
		
		for filename in ls:		#Iterating through files
			if filename.split('.')[-1] == 'deb':	#If it's a debian
				runProcess('mv '+filename+' '+packageName+'/')		#Move it to the directory for it
		order = open(packageName+"/install.sh",'w')		#Create a file to write the installation to
		downloaded.reverse()	#Reverse the list of packages downloaded to get the correct order
		order.write("sudo dpkg -i "+" ".join([d + "*" for d in downloaded]))	#Write the order to the file
		order.close()	#Close the file
		runProcess("chmod +x "+packageName+"/install.sh")
		runProcess("tar -zcvf "+packageName+".tar -C "+packageName+" .")	#Creating the tar file
		runProcess("sudo rm -r "+packageName)
