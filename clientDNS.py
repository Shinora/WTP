import dns
import autresFonctions
import config
import threading

class DNSConfig(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		print("Welcome in the DNS center !\nWhat do you want to do ?")
		action = self.ask("1 : Add a domain name\n2 : Modify a domain name\n3 : Delete a domain name")
		if action == 1:
			ipport = self.ask("Enter the IP and the Port of the DNS (format : IP:Port)")
			ndd = self.ask("Enter the nomain name")
			sha = self.ask("Enter the adress of the file (format : sha256.extention)")
			password = self.ask("Enter the password")
			error = dns.addNDD(ipport, sha, ndd, password)
			if error != 0:
				# Error occured
				print("An error occurred : " + str(error))
			else:
				print("Wonderful ! It succeeded !")
		elif action == 2:
			ipport = self.ask("Enter the IP and the Port of the DNS (format : IP:Port)")
			ndd = self.ask("Enter the nomain name")
			sha = self.ask("Enter the adress of the file (format : sha256.extention)")
			password = self.ask("Enter the password")
			error = dns.modifNDD(ipport, ndd, adress, password)
			if error != 0:
				# Error occurred
				print("An error occurred : " + str(error))
			else:
				print("Wonderful ! It succeeded !")
		elif action == 3:
			ipport = self.ask("Enter the IP and the Port of the DNS (format : IP:Port)")
			ndd = self.ask("Enter the nomain name")
			password = self.ask("Enter the password")
			error = dns.supprNDD(ipport, ndd, password)
			if error != 0:
				# Error occurred
				print("An error occurred : " + str(error))
			else:
				print("Wonderful ! It succeeded !")
		else:
			print("Your input isn't correct.")

	def ask(self, question):
		while 1:
			try:
				result = str(input(str(question) + "\n>>> "))
			except ValueError as e:
				print("Your input isn't correct. Error : " + str(e))
			else:
				break
		return result
