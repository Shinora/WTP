#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import os
import os.path
import platform
import logs
import BDD
import autresFonctions
import echangeNoeuds
import echangeFichiers
import time
import maj
import search
from Crypto import Random
from Crypto.Cipher import AES
from loader import loader
import threading
from maintenance import Maintenance
from parser import Parser
from serveurDNS import ServDNS
from vpn import ServVPN
from bridge import Bridge
import config
from clientDNS import DNSConfig
from thrdLnch import ThreadLauncher


logs.addLogs("\n\n\n")
status = loader("Start Up")
status.start()

fExtW = open(".extinctionWTP", "w")
fExtW.write("ALLUMER")
fExtW.close()

# On vérifie que les sources sont correctes et pas modifiées
#maj.verifSources()

# On vérifie que le file de config existe
try:
	with open('wtp.conf'):
		pass
except IOError:
	# Le file n'existe pas, on lance le créateur
	config.fillConfFile()
BDD.ajouterEntree("Noeuds", "88.189.108.233:5555", "Parser")
BDD.ajouterEntree("Noeuds", "88.189.108.233:5556")
BDD.ajouterEntree("Noeuds", "88.189.108.233:5557")

host = '127.0.0.1'
port = int(config.readConfFile("defaultPort"))

class ServeurThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.serveur_lance = True
	
	def run(self): 
		while self.serveur_lance:
			tcpsock.listen(10)
			tcpsock.settimeout(5)
			try:
				(clientsocket, (ip, port)) = tcpsock.accept()
			except socket.timeout:
				break
			newthread = ThreadLauncher(ip, port, clientsocket)
			newthread.start()

	def stop(self):
		self.serveur_lance = False

try:
	try:
		tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		tcpsock.bind((host, port))
		serveur_lance = True
	except OSError as e:
		logs.addLogs("ERROR : In launcher.py : "+str(e))
		logs.addLogs("INFO : Stop everything and restart after...")
		os.popen("python3 reload.py", 'r')
	else:
		# On lance les programmes externes
		ThrdMntc = Maintenance()
		ThrdMntc.start()
		if(str(config.readConfFile("Parser")) == "True"):
			# Le noeud est un parseur, on lance la fonction.
			ThrdParser = Parser()
			ThrdParser.start()
		if(str(config.readConfFile("DNS")) == "True"):
			# Le noeud est un DNS, on lance la fonction.
			ThrdDNS = ServDNS()
			ThrdDNS.start()
		if(str(config.readConfFile("VPN")) == "True"):
			# Le noeud est un VPN, on lance la fonction.
			ThrdVPN = ServVPN()
			ThrdVPN.start()
		#ThrdBrd = Bridge()
		#ThrdBrd.start()
		# On indique notre présence à quelques parseurs
		tableau = BDD.aleatoire("Noeuds", "IP", 15, "Parser")
		if isinstance(tableau, list) and tableau:
			# On envoi la request à chaque noeud sélectionné
			for peerIP in tableau:
				peerIP = peerIP[0]
				ip = peerIP[:peerIP.find(":")]
				port = peerIP[peerIP.find(":")+1:]
				connNoeud = autresFonctions.connectionClient(ip, port)
				cipher = autresFonctions.createCipherAES(config.readConfFile("AESKey"))
				if str(connNoeud) != "=cmd ERROR":
					logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
					request = "=cmd newPeerNetwork ip " + str(config.readConfFile("MyIP")) + str(config.readConfFile("defaultPort"))
					request = request.encode()
					connNoeud.send(request)
					rcvCmd = connNoeud.recv(1024)
					connNoeud.close()
					if rcvCmd == "=cmd noParser":
						# Il faut changer le paramètre du noeud, il n'est pas parseur mais simple
						BDD.supprEntree("Noeuds", peerIP)
						BDD.ajouterEntree("Noeuds", peerIP)
					elif rcvCmd != "=cmd peerAdded":
						# Une erreur s'est produite
						logs.addLogs("ERROR : The request was not recognized in launcher.py : "+str(rcvCmd))
				else:
					logs.addLogs("INFO : Unable to connect to the peer in launcher.py : "+str(connNoeud))
		else:
			# Une erreur s'est produite
			logs.addLogs("ERROR : There is not enough IP in launcher.py : "+str(tableau))
			print(len(tableau))
			print(str(tableau))
		status.stop()
		status.join()
		autresFonctions.afficherLogo()
		logs.addLogs("INFO : WTP has started, he is now listening to the port " + str(port))
		newServ = ServeurThread()
		newServ.start()
		serveur_lance = True
		while serveur_lance:
			# Gérer les commandes utilisateur
			# La première fois, le wtp@PC:$ ne s'affiche pas...
			userCmd = str(input("wtp@"+str(platform.uname()[1])+":$ "))
			if userCmd == "help":
				# Afficher toutes les options
				print("Here are the main functions:")
				print("update		Check for updates")
				print("stats 		Shows your peer statistics")
				print("config 		Edit the configuration")
				print("exit 		Stop WTP")
				print("reload 		Restart WTP")
				print("dns 			Edit the VPN configuration")
			elif userCmd == "update":
				# Vérifier les MAJ
				#maj.verifMAJ()
				#maj.verifSources()
				print("Done.")
			elif userCmd == "stats":
				# Affiche les statistiques
				print("Number of peers in the database : " + str(BDD.compterStats("NbNoeuds")))
				print("Number of special peers in the database : " + str(BDD.compterStats("NbSN")))
				print("Number of external files in the database : " + str(BDD.compterStats("NbFichiersExt")))
				print("Number of files on this hard drive : " + str(BDD.compterStats("NbFichiers")))
				print("Size of all files : " + str(BDD.compterStats("PoidsFichiers")))
				print("Number of peers lists sent : " + str(BDD.compterStats("NbEnvsLstNoeuds")))
				print("Number of file lists sent : " + str(BDD.compterStats("NbEnvsLstFichiers")))
				print("Number of external file lists sent : " + str(BDD.compterStats("NbEnvsLstFichiersExt")))
				print("Number of files sent : " + str(BDD.compterStats("NbEnvsFichiers")))
				print("Number of presence requests received : " + str(BDD.compterStats("NbPresence")))
				print("Number of files received : " + str(BDD.compterStats("NbReceptFichiers")))
			elif userCmd == "config":
				# Modifier le fichier de configuration
				config.modifConfig()
			elif userCmd == "dns":
				# Entrer dans le programme de configuration du DNS
				thrdDNS = DNSConfig()
				thrdDNS.start()
				thrdDNS.join()
			elif userCmd == "exit":
				# On arrète WTP
				print("Pro tip : You can also stop WTP at any time by pressing Ctrl + C.")
				break
			elif userCmd == "reload": # Ne fonctionne pas. Trouver une alternative à .extinctionWTP
				os.popen("python3 reload.py", 'r')
				serveur_lance = False
			else:
				print("Unknow request.")
			print("") # Un saut de ligne entre chaque commande
except KeyboardInterrupt:
	pass
status = loader("Shutting down ...")
status.start()
newServ.stop()
fExtW = open(".extinctionWTP", "w")
fExtW.write("ETEINDRE")
fExtW.close()
if(str(config.readConfFile("Parser")) == "True"):
	# Le noeud est un parseur, on arrète le thread.
	ThrdParser.stop()
	ThrdParser.join()
if(str(config.readConfFile("DNS")) == "True"):
	# Le noeud est un DNS, on arrète le thread.
	ThrdDNS.stop()
	ThrdDNS.join()
if(str(config.readConfFile("VPN")) == "True"):
	# Le noeud est un VPN, on arrète le thread.
	ThrdVPN.stop()
	ThrdVPN.join()
ThrdMntc.stop()
# ThrdBrd.stop()
newServ.join()
ThrdMntc.join()
# ThrdBrd.join()
logs.addLogs("INFO : WTP has correctly stopped.")
status.stop()
