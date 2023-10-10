#!/usr/bin/python3
import hashlib
import json
import sys, os

appDir = os.path.dirname(os.path.abspath(__file__)) + "/../"

def main(argv):
	if (len(argv) == 3):
		name = argv[1]
		pwHash = hashlib.sha512(argv[2].encode()).hexdigest()
		print ("User %s" %(argv[1]))
		print ("Password: %.16s...." %(pwHash))

		# read users.json file and convert it to dictionary in python3
		with open (f'{appDir}users.json', 'r') as fp:
			datain = json.load(fp)

		# check if the user already exists
		for i in datain:
			if i['username'] == name:
				print ('!!! USER ALREADY EXISTS !!!')
				return 1

		# append user data if user doesn't exit
		datain.append({"username": name, "passHash": pwHash, "config": f"notes/{name}/{name}.conf.json"})

		# update users.json file
		with open (f'{appDir}users.json', 'w') as fp:
			fp.write(json.dumps(datain, indent=4))

		# creates important files for user
		os.system (f'mkdir {appDir}notes/{name}')
		os.system (f'echo "[]" > {appDir}notes/{name}/{name}.conf.json')
	else:
		print ("***\n\nadd.py {username} {password}\n\n***")

if __name__=="__main__":
	main(sys.argv)
