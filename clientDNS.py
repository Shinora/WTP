import dns
import autresFonctions
import config
import threading

class DNSConfig(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		print("Welcome in the DNS center !\nWhat do you want to do ? (exit for quit this wizard)")
		try:
			action = int(autresFonctions.ask("1 : Add a domain name\n2 : Modify a domain name\n3 : Delete a domain name"))
		except ValueError:
			print("\033[91mYour input isn't correct.\033[0m")
		else:
			if action == 1:
				ipport = autresFonctions.ask("Enter the IP and the Port of the DNS (format : IP:Port)")
				ndd = autresFonctions.ask("Enter the nomain name")
				sha = autresFonctions.ask("Enter the adress of the file (format : sha256.extention)")
				password = autresFonctions.ask("Enter the password")
				error = dns.addNDD(ipport, sha, ndd, password)
				if error != 0:
					# Error occured
					print("\033[91mAn error occurred : " + str(error)+"\033[0m")
				else:
					print("\033[92mWonderful ! It succeeded !\033[0m")
			elif action == 2:
				ipport = autresFonctions.ask("Enter the IP and the Port of the DNS (format : IP:Port)")
				ndd = autresFonctions.ask("Enter the nomain name")
				sha = autresFonctions.ask("Enter the adress of the file (format : sha256.extention)")
				password = autresFonctions.ask("Enter the password")
				error = dns.modifNDD(ipport, ndd, sha, password)
				if error != 0:
					# Error occurred
					print("\033[91mAn error occurred : " + str(error)+"\033[0m")
				else:
					print("\033[92mWonderful ! It succeeded !\033[0m")
			elif action == 3:
				ipport = autresFonctions.ask("Enter the IP and the Port of the DNS (format : IP:Port)")
				ndd = autresFonctions.ask("Enter the nomain name")
				password = autresFonctions.ask("Enter the password")
				error = dns.supprNDD(ipport, ndd, password)
				if error != 0:
					# Error occurred
					print("\033[91mAn error occurred : " + str(error)+"\033[0m")
				else:
					print("\033[92mWonderful ! It succeeded !\033[0m")
			else:
				print("\033[91mYour input isn't correct.\033[0m")
