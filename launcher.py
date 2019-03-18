#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import os
import os.path
import platform
import logs
import BDD
import autresFonctions
import maj
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
import cmdLauncher


logs.addLogs("\n\n\n")
fExtW = open(".extinctionWTP", "w")
fExtW.write("ALLUMER")
fExtW.close()
# On vérifie que les sources sont correctes et pas modifiées
#maj.verifSources()
config.verifConfig()
host = '127.0.0.1'
port = int(config.readConfFile("defaultPort"))
status = loader("Start Up") # Ici et pas avant car si le fichier n'existe pas
status.start() # L'assistant est invisible.

class ServeurThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.serveur_lance = True
		self.ip = ""
		self.port = 0
		self.clientsocket = ""
	
	def run(self): 
		while self.serveur_lance:
			tcpsock.listen(10)
			tcpsock.settimeout(5)
			try:
				(self.clientsocket, (self.ip, self.port)) = tcpsock.accept()
			except socket.timeout:
				pass
			else:
				newthread = ThreadLauncher(self.ip, self.port, self.clientsocket)
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
				connNoeud = autresFonctions.connectionClient(peerIP)
				if str(connNoeud) != "=cmd ERROR":
					logs.addLogs("INFO : Connection with peer etablished")
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
		status.stop()
		status.join()
		autresFonctions.afficherLogo()
		logs.addLogs("INFO : WTP has started, he is now listening to the port " + str(port))
		newServ = ServeurThread()
		newServ.start()
		serveur_lance = True
		delAll = False
		while serveur_lance:
			# Gérer les commandes utilisateur
			# La première fois, le wtp@PC:$ ne s'affiche pas...
			userCmd = str(input("wtp@"+str(platform.uname()[1])+":$ "))
			retour = cmdLauncher.cmdLauncher(userCmd)
			if retour == -1:
				serveur_lance = False
			elif retour == -2:
				serveur_lance = False
				delAll = True
			print("") # Un saut de ligne entre chaque commande
except KeyboardInterrupt:
	pass
status = loader("Shutting down ...")
status.start()
newServ.stop()
try:
	ThrdParser.stop()
	ThrdParser.join()
except NameError:
	pass
try:
	ThrdDNS.stop()
	ThrdDNS.join()
except NameError:
	pass
try:
	ThrdVPN.stop()
	ThrdVPN.join()
except NameError:
	pass
ThrdMntc.stop()
# ThrdBrd.stop()
newServ.join()
ThrdMntc.join()
# ThrdBrd.join()
status.stop()
if delAll is True:
	fExtW = open(".extinctionWTP", "w")
	fExtW.write("ETEINDRE")
	fExtW.close()
	logs.addLogs("INFO : WTP has correctly stopped.")
