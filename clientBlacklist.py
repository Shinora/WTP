import blacklist
import autresFonctions
import threading
import BDD
import config

class configBlckLst(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		print("Welcome in the Blacklist center !\nWhat do you want to do ?")
		action = self.ask("1 : Add something in the BlackList\n2 : Delete something in the BlackList\n3 : Update the Blacklist with an other peer\n4 : Change the BlackList default peer")
		try:
			action = int(action)
		except ValueError as e:
			print("Your input isn't correct (between 1 and 4)\nError : "+str(e))
		if action == 1:
			entree = self.ask("What do you want to add in your BlackList ?")
			while 1:
				rank = self.ask("What is the rank of this new entry ?")
				try:
					if int(rank) > 0 and int(rank) <= 5:
						break
				except ValueError as e:
					print("Your input isn't correct. (between 1 and 5)\nError : "+str(e))
			error = BDD.ajouterEntree("BlackList", entree, rank)
			if error == 0:
				print(str(entree) + " has been added in the BlackList with the rank " + str(rank))
			else:
				print("An error occured. Look at the logs for more informations. ("+str(error)+")")
		elif action == 2:
			entree = self.ask("What do you want to delete in your BlackList ?")
			error = BDD.supprEntree("BlackList", entree)
			if error == 0:
				print(str(entree) + " has been deleted in the BlackList")
			else:
				print("An error occured. Look at the logs for more informations. ("+str(error)+")")
		elif action == 3:
			ipport = str(self.ask("With which peer do you want to update? (Press ENTER to update with the default peer : "+str(config.readConfFile("BlackList"))+")"))
			if ipport == "":
				status = loader("Work in progress")
				status.start()
				blacklist.maj()
				status.stop()
				status.join()
			elif autresFonctions.verifIPPORT(IppeerPort): # Si ipport est un ip:port
				status = loader("Work in progress")
				status.start()
				blacklist.maj(ipport)
				status.stop()
				status.join()
			else:
				print("This is not a IP:PORT")
		elif action == 4:
			value = str(self.ask("Which peer do you want to choose to be your default blacklist peer ? (The actual peer is "+str(config.readConfFile("Blacklist"))))
			if autresFonctions.verifIPPORT(value):
				config.modifConfigFile("Blacklist", value)
			else:
				print("Your input isn't a IP:PORT")
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
