import os
import math
import hashlib
import logs
import BDD
import threading
import autresFonctions
import time

 ####################################################
#													#
# Sont ici les threads qui permettent d'envoyer	    #
# et recevoir des fichiers  présents sur le réseau  #
#													#
 ####################################################

class downFile(threading.Thread):
	# Nouveau Thread serveur qui reçoit le fichier
	def __init__(self, file, port, temp):
		threading.Thread.__init__(self)
		self.file = file
		self.port = port
		self.conn = ""
		self.ipExt = ""
		self.portExt = ""
		self.size = 0
		self.temp = temp

	def run(self):
		error = 0
		autresFonctions.verifFiles()
		# Lancement du serveur
		tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		tcpsock.bind(("127.0.0.1", self.port))
		tcpsock.listen(10)
		tcpsock.settimeout(10)
		try:
			(self.conn, (self.ipExt, self.portExt)) = tcpsock.accept()
		except socket.timeout:
			logs.addLogs("ERROR : Timeout in downFile. No peer has connected")
			error += 1
		except socket.error:
			logs.addLogs("ERROR : The port is already used in downFile")
		else:
			# GO !
			cmdRecu = self.conn.recv(1024)
			cmdRecu = cmdRecu.decode()
			if cmdRecu[:24] == '=cmd StartTransfer size ':
				self.size = int(cmdRecu[24:])
				# Le noeud est OK
				#On vide le file (on ne sait jamais)
				f = open("HOSTEDFILES/" + self.file, "w")
				f.write("")
				f.close()
				# On ouvre le file vide en mode append et binaire
				# (donc les données n'ont pas besoin d'êtres converties et elles seront ajoutées à la fin du file)
				f = open("HOSTEDFILES/" + self.file, "ab")
				if self.size > 1024:
					# Le file va arriver en morceaux
					nbPaquetsCalcule = math.ceil(self.size/1024)
					nbPaquetsRecu = 0
					while nbPaquetsCalcule > nbPaquetsRecu:
						recu = ""
						recu = self.conn.recv(1024)
						if not recu :
							logs.addLogs("ERROR : An error occured during the transfer in downFile")
							break
						f.write(recu)
						nbPaquetsRecu = nbPaquetsRecu+1
				else:
					# Le file va arriver d'un seul coup
					recu = ""
					recu = self.conn.recv(1024)
					f.write(recu)
				f.close()
				self.conn.close()
				# Maintenant, il faut vérifier que le ficher a le meme SHA256
				file = open("HOSTEDFILES/" + self.file, "rb")
				contenu = file.read()
				file.close()
				hashFichier = hashlib.sha256(str(contenu).encode('utf-8')).hexdigest()
				if hashFichier == self.file[:self.file.find('.')] or self.file[12:16] == "TEMP":
					# Le transfert s'est bien passé
					# Ajouter le file à la BDD
					BDD.ajouterEntree("Fichiers", self.file)
				else:
					# Ah, il y a un problème, on suppr
					logs.addLogs("ERROR: The Hash of the file is different in downFile")
					os.remove("HOSTEDFILES/" + self.file)
					error += 1
			else:
				logs.addLogs("ERROR : The peer refused the transfert in downFile")
				error += 1
		if error != 0 :
			logs.addLogs("ERROR : An error has occured in downFile ("+str(error)+").")
		tcpsock.close()
		f = open(".TEMP/"+str(self.temp), "w")
		f.write(str(error))
		f.close()

class upFile(threading.Thread):
	# Nouveau Thread client qui envoie le fichier
	def __init__(self, ipport, file, temp):
		threading.Thread.__init__(self)
		self.file = file
		self.ip = "127.0.0.1"#ipport[:ipport.find(":")]
		self.port = int(ipport[ipport.find(":")+1:])
		self.conn = ""
		self.temp = temp

	def run(self):
		error = 0
		autresFonctions.verifFiles()
		i = 0
		while i < 50:
			i += 1
			self.conn = autresFonctions.connectionClient(self.ip, self.port)
			if self.conn != "=cmd ERROR":
				break
			else:
				time.sleep(0.2)
		if str(self.conn) == "=cmd ERROR":
			error += 1
		else:
			# Vérifier que l'on a le fichier
			try:
				tailleFichier = os.path.getsize("HOSTEDFILES/"+self.file)
				if tailleFichier < 1:
					error += 1
					logs.addLogs("ERROR : The file is empty in upFile")
			except Exception:
				logs.addLogs("ERROR : The file doesn't exist")
				error += 1
			if error == 0:
				# On peut continuer
				sendCmd = "=cmd StartTransfer size "+str(tailleFichier)
				self.conn.send(sendCmd.encode())
				#Maintenant, on vérifie si le file peut être envoyé en une seule foie, ou si il faut le "découper"
				pathFichier = "HOSTEDFILES/"+self.file
				if tailleFichier > 1024:
					#Le file doit être découpé avant d'être envoyé
					fich = open(pathFichier, "rb")
					num = 0
					nbPaquets = math.ceil(tailleFichier/1024)
					deplacementFichier = 0
					while num < nbPaquets:
						fich.seek(deplacementFichier, 0) # on se deplace par rapport au numero de caractere (de 1024 a 1024 octets)
						donnees = fich.read(1024) # Lecture du file en 1024 octets
						self.conn.send(donnees) # Envoi du file par paquet de 1024 octets
						num = num + 1
						deplacementFichier = deplacementFichier + 1024
				else:
					#Le file peut être envoyé en une seule fois
					fich = open(pathFichier, "rb")
					donnees = fich.read() # Lecture du file
					self.conn.send(donnees) # Envoi du file
				self.conn.close()
		if error != 0 :
			logs.addLogs("ERROR : An error has occured in upFile ("+str(error)+").")
		f = open(".TEMP/"+str(self.temp), "w")
		f.write(str(error))
		f.close()
