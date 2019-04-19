import logs
import BDD
import autresFonctions
import echangeNoeuds
import echangeFichiers
import time
import search
import threading
import config
import os
import stats

# Le thread principal du launcher est ici

class ThreadLauncher(threading.Thread):
	def __init__(self, ip, port, clientsocket):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsocket = clientsocket
	
	def run(self):
		rcvCmd = self.clientsocket.recv(1024)
		rcvCmd = rcvCmd.decode()
		# Maintenant, vérifions la demande du client.
		if rcvCmd != '':
			if rcvCmd[:19] == "=cmd DemandeFichier":
				# =cmd DemandeFichier  nom sha256.ext  ipport IP:PORT
				# Dirriger vers la fonction UploadFichier()
				# Le noeud distant demande le file, donc on lui envoi, Up !
				# On va chercher les deux informations qu'il nous faut :
				# Le nom du file (sous forme sha256.ext)
				# L'IP et le port du noeud qui a fait la demande (sous forme IP:PORT)
				fileName = rcvCmd[rcvCmd.find(" nom ")+5:rcvCmd.find(" ipport ")]
				IppeerPort = rcvCmd[rcvCmd.find(" ipport ")+8:]
				if BDD.verifFichier(fileName):
					error = 0
					# Le file est présent dans la BDD, on peut l'envoyer
					temp = str(time.time())
					thrdUp = echangeFichiers.upFile(IppeerPort, fileName, temp)
					thrdUp.start()
					thrdUp.join()
					# Lire le fichier temporaire pour savoir si il y a eut des erreurs
					try:
						f = open(".TEMP/"+temp, "r")
						error += int(f.read())
						f.close()
						os.remove(".TEMP/"+temp)
					except Exception as e:
						error += 1
						logs.addLogs("\033[31mERROR : An error occured in CmdDemandeFichier : "+str(e)+"\033[0m")
					os.remove(".TEMP/"+temp)
					if error != 0:
						stats.modifStats("NbEnvsFichiers")
					else:
						logs.addLogs("\033[31mERROR : An error occured for upload "+str(fileName)+" in thrdLnch.py ("+str(error)+")\033[0m")
				else:
					print("\033[31mThis file isn't on this computer : '"+str(fileName)+"'\033[0m")
			elif rcvCmd[:17] == "=cmd DemandeNoeud": # Fonction Serveur
				# Dirriger vers la fonction EnvoiNoeuds()
				# Le noeud distant a demandé les noeuds, on lui envoi !
				# On trouve le premier port qui peut être attribué
				IppeerPort = "127.0.0.1:" + str(autresFonctions.portLibre(int(config.readConfFile("miniPort"))))
				sendCmd = IppeerPort # On envoie au demandeur l'adresse à contacter
				self.clientsocket.send(sendCmd.encode())
				echangeNoeuds.EnvoiNoeuds(IppeerPort)
				stats.modifStats("NbEnvsLstNoeuds")
			elif rcvCmd[:25] == "=cmd DemandeListeFichiers":
				# On va récuperer le nom du file qui contient la liste
				# Ensuite, on la transmet au noeud distant pour qu'il puisse
				# faire la demande de réception du file pour qu'il puisse l'analyser
				if rcvCmd[:28] == "=cmd DemandeListeFichiersExt":
					file = autresFonctions.lsteFichiers(1)
					stats.modifStats("NbEnvsLstFichiers")
				else:
					file = autresFonctions.lsteFichiers()
					stats.modifStats("NbEnvsLstFichiersExt")
				self.clientsocket.send(file.encode())
			elif rcvCmd[:23] == "=cmd DemandeListeNoeuds":
				# On va récuperer le nom du file qui contient la liste
				# Ensuite, on la transmet au noeud distant pour qu'il puisse
				# faire la demande de réception du file pour qu'il puisse l'analyser
				file = autresFonctions.lsteNoeuds()
				self.clientsocket.send(file.encode())
				stats.modifStats("NbEnvsLstNoeuds")
			elif rcvCmd[:20] == "=cmd DemandePresence":
				# C'est tout bête, pas besoin de fonction
				# Il suffit de renvoyer la request informant que l'on est connecté au réseau.
				sendCmd = "=cmd Present"
				self.clientsocket.send(sendCmd.encode())
				stats.modifStats("NbPresence")
			elif rcvCmd[:15] == "=cmd rechercher":
				# =cmd rechercher nom SHA256.ext
				# Renvoie le retour de la fonction, qui elle même retourne une IP+Port ou 0
				# Chercher le nom du file
				donnee = rcvCmd[20:]
				sendCmd = str(search.rechercheFichierEntiere(donnee))
				self.clientsocket.send(sendCmd.encode())
			elif rcvCmd[:11] == "=cmd status":
				# On demande le statut du noeud (Simple, Parser, DNS, VPN, Main)
				if(config.readConfFile("Parser") == "Oui"):
					sendCmd = "=cmd Parser"
					self.clientsocket.send(sendCmd.encode())
				else:
					sendCmd = "=cmd Simple"
					self.clientsocket.send(sendCmd.encode())
			elif rcvCmd[:25] == "=cmd newFileNetwork name ":
				# =cmd newFileNetwork name ****** ip ******
				# Un nouveau file est envoyé sur le réseau
				fileName = rcvCmd[25:]
				ipport = rcvCmd[rcvCmd.find(" ip ")+4:]
				if(config.readConfFile("Parser") == "Oui"):
					# On prend en charge l'import de files,
					# On l'ajoute à la base de données et on le télécharge
					BDD.ajouterEntree("FichiersExt", fileName, ipport)
					sendCmd = "=cmd fileAdded"
					self.clientsocket.send(sendCmd.encode())
					ip = ipport[:ipport.find(":")]
					port = ipport[ipport.find(":")+1:]
					fctsClient.CmdDemandeFichier(ip, port, fileName)
				else:
					# On ne prend pas en charge l'import de files,
					# Mais on l'ajoute quand même à la base de données
					BDD.ajouterEntree("FichiersExt", fileName, ipport)
					sendCmd = "=cmd noParser"
					self.clientsocket.send(sendCmd.encode())
			elif rcvCmd[:23] == "=cmd newPeerNetwork ip ":
				# =cmd newPeerNetwork ip ******
				# Un nouveau peer est envoyé sur le réseau
				ipport = rcvCmd[23:]
				if(config.readConfFile("Parser") == "True"):
					# On prend en charge l'ajout de peers
					# On l'ajoute à la base de données
					BDD.ajouterEntree("Noeuds", ipport)
					sendCmd = "=cmd peerAdded"
					self.clientsocket.send(sendCmd.encode())
				else:
					# On ne prend pas en charge l'import de files,
					# Mais on l'ajoute quand même à la base de données
					BDD.ajouterEntree("FichiersExt", fileName, ipport)
					sendCmd = "=cmd noParser"
					self.clientsocket.send(sendCmd.encode())
			elif rcvCmd[10:] == "BlackList ":
				# Les fonctionnalitées de la BlackList
				rcvCmd = rcvCmd[10:]
				if rcvCmd[:4] == "name":
					# Le peer veut savoir si cet élément fait partie de la BlackList,
					# et si oui quel est son rang (de 0 à 5)
					rank = search.chercherInfo("BlackList", rcvCmd[4:])
					self.clientsocket.send(rank.encode())
				if rcvCmd[4:] == "sync":
					# Le peer veut recevoir l'intégralité de cette base
					# On va donc la mettre dans un fichier
					filename = echangeListes.tableToFile("BlackList")
					try:
						filename = int(filename)
					except ValueError:
						# Si c'est un chiffre, c'est un code d'erreur
						sendCmd = "=cmd Filename " + str(filename) + "ipport " + config.readConfFile("MyIP") + ":" + config.readConfFile("defaultPort")
					else:
						sendCmd = "=cmd ERROR"
					self.clientsocket.send(sendCmd.encode())
			else:
				# Oups... Demande non-reconnue...
				logs.addLogs("ERROR : Unknown request : " + str(rcvCmd))
				self.clientsocket.send("=cmd UNKNOW".encode())
