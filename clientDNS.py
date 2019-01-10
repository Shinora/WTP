#! /usr/bin/python
# -*- coding:utf-8 -*-

import logs
import sys
import os
import dns
import autresFonctions

def ask(question):
	try:
		result = str(input(str(question) + "\n>>> "))
	except ValueError as e:
		print("Your input isn't correct... Sorry !\nError : " + str(e))
		sys.exit()
	return result

autresFonctions.afficherLogo()
print("Welcome in the DNS center !\nWhat do you want to do ?")
print("1 : Add a domain name\n2 : Modify a domain name\n3 : Delete a domain name")
try:
	action = int(input(">>> "))
except ValueError as e:
	print("Your input isn't correct... Sorry !\n Error : " + str(e))
else:
	if action == 1:
		ipport = ask("Enter the IP and the Port of the DNS (format : IP:Port)")
		ndd = ask("Enter the nomain name")
		sha = ask("Enter the adress of the file (format : sha256.extention)")
		password = ask("Enter the password")
		error = dns.addNDD(ipport, sha, ndd, password)
		if error != 0:
			# Error occured
			print("An error occurred : " + str(error))
		else:
			print("Wonderful ! It succeeded !")
	elif action == 2:
		ipport = ask("Enter the IP and the Port of the DNS (format : IP:Port)")
		ndd = ask("Enter the nomain name")
		sha = ask("Enter the adress of the file (format : sha256.extention)")
		password = ask("Enter the password")
		error = dns.modifNDD(ipport, ndd, adress, password)
		if error != 0:
			# Error occurred
			print("An error occurred : " + str(error))
		else:
			print("Wonderful ! It succeeded !")
	elif action == 3:
		ipport = ask("Enter the IP and the Port of the DNS (format : IP:Port)")
		ndd = ask("Enter the nomain name")
		password = ask("Enter the password")
		error = dns.supprNDD(ipport, ndd, password)
		if error != 0:
			# Error occurred
			print("An error occurred : " + str(error))
		else:
			print("Wonderful ! It succeeded !")
	else:
		print("Your input isn't correct... Sorry !")
