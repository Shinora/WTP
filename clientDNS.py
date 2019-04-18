import dns
import autresFonctions
import config
import threading

class DNSConfig(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		print("Welcome in the DNS center !\nWhat do you want to do ? (exit for quit this wizard)")
		action = autresFonctions.ask("1 : Add a domain name\n2 : Modify a domain name\n3 : Delete a domain name")
		if action == 1:
			ipport = autresFonctions.ask("Enter the IP and the Port of the DNS (format : IP:Port)")
			ndd = autresFonctions.ask("Enter the nomain name")
			sha = autresFonctions.ask("Enter the adress of the file (format : sha256.extention)")
			password = autresFonctions.ask("Enter the password")
			error = dns.addNDD(ipport, sha, ndd, password)
			if error != 0:
				# Error occured
				print("An error occurred : " + str(error))
			else:
				print("Wonderful ! It succeeded !")
		elif action == 2:
			ipport = autresFonctions.ask("Enter the IP and the Port of the DNS (format : IP:Port)")
			ndd = autresFonctions.ask("Enter the nomain name")
			sha = autresFonctions.ask("Enter the adress of the file (format : sha256.extention)")
			password = autresFonctions.ask("Enter the password")
			error = dns.modifNDD(ipport, ndd, adress, password)
			if error != 0:
				# Error occurred
				print("An error occurred : " + str(error))
			else:
				print("Wonderful ! It succeeded !")
		elif action == 3:
			ipport = autresFonctions.ask("Enter the IP and the Port of the DNS (format : IP:Port)")
			ndd = autresFonctions.ask("Enter the nomain name")
			password = autresFonctions.ask("Enter the password")
			error = dns.supprNDD(ipport, ndd, password)
			if error != 0:
				# Error occurred
				print("An error occurred : " + str(error))
			else:
				print("Wonderful ! It succeeded !")
		else:
			print("Your input isn't correct.")
