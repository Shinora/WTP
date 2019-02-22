#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import select
import sys
import os
import os.path
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
	autresFonctions.fillConfFile()
BDD.ajouterEntree("Noeuds", "88.189.108.233:5555", "Parser")
BDD.ajouterEntree("Noeuds", "88.189.108.233:5556")
BDD.ajouterEntree("Noeuds", "88.189.108.233:5557")

host = '127.0.0.1'
port = int(autresFonctions.readConfFile("defaultPort"))

class ClientThread(threading.Thread):

	def __init__(self, ip, port, clientsocket):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsocket = clientsocket
		print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))
	
	def run(self): 
		cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
		rcvCmd = self.clientsocket.recv(1024)
		rcvCmd = rcvCmd.decode()
		# Maintenant, vérifions la demande du client.
		if rcvCmd != '':
			status = loader("Connection with a peer")
			status.start()
			if rcvCmd[:19] == "=cmd DemandeFichier": # Fonction Client OPPÉRATIONNEL
				# =cmd DemandeFichier  nom sha256.ext  ipPort IP:PORT
				# Dirriger vers la fonction UploadFichier()
				# Le noeud distant demande le file, donc on lui envoi, Up !
				# On va chercher les deux informations qu'il nous faut :
				# Le nom du file (sous forme sha256.ext)
				# L'IP et le port du noeud qui a fait la demande (sous forme IP:PORT)
				pos1 = rcvCmd.find(" nom ")
				pos1 = pos1+5
				pos2 = rcvCmd.find(" ipPort ")
				fileName = rcvCmd[pos1:pos2]
				pos2 = pos2+8
				pos3 = len(rcvCmd)
				IppeerPort = rcvCmd[pos2:pos3]
				if BDD.verifFichier(fileName):
					# Le file est présent dans la BDD, on peut l'envoyer
					self.clientsocket.send("=cmd OK".encode())
					time.sleep(0.5) # Le temps que le noeud distant mette en place son serveur
					if echangeFichiers.UploadFichier(fileName, IppeerPort) != 0:
						self.clientsocket.send("=cmd ERROR".encode())
					else:
						self.clientsocket.send(")cmd SUCCESS".encode())
						BDD.modifStats("NbEnvsFichiers")
				else:
					self.clientsocket.send("=cmd ERROR".encode())
			elif rcvCmd[:17] == "=cmd DemandeNoeud": # Fonction Serveur
				# Dirriger vers la fonction EnvoiNoeuds()
				# Le noeud distant a demandé les noeuds, on lui envoi !
				# On trouve le premier port qui peut être attribué
				IppeerPort = "127.0.0.1:" + str(autresFonctions.portLibre(int(autresFonctions.readConfFile("miniPort"))))
				sendCmd = IppeerPort # On envoie au demandeur l'adresse à contacter
				self.clientsocket.send(sendCmd.encode())
				echangeNoeuds.EnvoiNoeuds(IppeerPort)
				BDD.modifStats("NbEnvsLstNoeuds")
			elif rcvCmd[:25] == "=cmd DemandeListeFichiers":
				# On va récuperer le nom du file qui contient la liste
				# Ensuite, on la transmet au noeud distant pour qu'il puisse
				# faire la demande de réception du file pour qu'il puisse l'analyser
				if rcvCmd[:28] == "=cmd DemandeListeFichiersExt":
					file = autresFonctions.lsteFichiers(1)
					BDD.modifStats("NbEnvsLstFichiers")
				else:
					file = autresFonctions.lsteFichiers()
					BDD.modifStats("NbEnvsLstFichiersExt")
				self.clientsocket.send(file.encode())
			elif rcvCmd[:23] == "=cmd DemandeListeNoeuds":
				# On va récuperer le nom du file qui contient la liste
				# Ensuite, on la transmet au noeud distant pour qu'il puisse
				# faire la demande de réception du file pour qu'il puisse l'analyser
				file = autresFonctions.lsteNoeuds()
				self.clientsocket.send(file.encode())
				BDD.modifStats("NbEnvsLstNoeuds")
			elif rcvCmd[:20] == "=cmd DemandePresence": # OPPÉRATIONNEL
				# C'est tout bête, pas besoin de fonction
				# Il suffit de renvoyer la request informant que l'on est connecté au réseau.
				sendCmd = "=cmd Present"
				self.clientsocket.send(sendCmd.encode())
				BDD.modifStats("NbPresence")
			elif rcvCmd[:15] == "=cmd rechercher": 
				# =cmd rechercher nom SHA256.ext
				# Renvoie le retour de la fonction, qui elle même retourne une IP+Port ou 0
				# Chercher le nom du file
				donnee = rcvCmd[20:]
				sendCmd = str(search.rechercheFichierEntiere(donnee))
				self.clientsocket.send(sendCmd.encode())
			elif rcvCmd[:11] == "=cmd status":
				# On demande le statut du noeud (Simple, Parser, DNS, VPN, Main)
				if(autresFonctions.readConfFile("Parser") == "Oui"):
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
				if(autresFonctions.readConfFile("Parser") == "Oui"):
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
				if(autresFonctions.readConfFile("Parser") == "True"):
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
			else:
				# Oups... Demande non-reconnue...
				logs.addLogs("ERROR : Unknown request : " + str(rcvCmd))
				self.clientsocket.send("=cmd UNKNOW".encode())
			status.stop()
			status.join()

try:
	try:
		tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		tcpsock.bind((host, port))
		serveur_lance = True
	except OSError as e:
		logs.addLogs("ERROR : In launcher.py : "+str(e))
		logs.addLogs("Stop everything and restart after...")
		fExtW = open(".extinctionWTP", "w")
		fExtW.write("ETEINDRE")
		fExtW.close()
		time.sleep(15)
		logs.addLogs("Try to restart...")
		fExtW = open(".extinctionWTP", "w")
		fExtW.write("ETEINDRE")
		fExtW.close()
	else:
		# On lance les programmes externes
		os.popen('python3 maintenance.py', 'r')
		if(str(autresFonctions.readConfFile("Parser")) == "True"):
			# Le noeud est un parseur, on lance la fonction.
			os.popen('python3 parser.py', 'r')
		if(str(autresFonctions.readConfFile("DNS")) == "True"):
			# Le noeud est un DNS, on lance la fonction.
			os.popen('python3 serveurDNS.py', 'r')
		if(str(autresFonctions.readConfFile("VPN")) == "True"):
			# Le noeud est un VPN, on lance la fonction.
			os.popen('python3 vpn.py', 'r')
		# On indique notre présence à quelques parseurs
		tableau = BDD.aleatoire("Noeuds", "IP", 15, "Parser")
		if type(tableau) != int and len(tableau) > 0:
			# On envoi la request à chaque noeud sélectionné
			for peerIP in tableau:
				peerIP = peerIP[0]
				ip = peerIP[:peerIP.find(":")]
				port = peerIP[peerIP.find(":")+1:]
				connNoeud = autresFonctions.connectionClient(ip, port)
				cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
				if str(connNoeud) != "=cmd ERROR":
					logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
					request = "=cmd newPeerNetwork ip " + str(autresFonctions.readConfFile("MyIP")) + str(autresFonctions.readConfFile("defaultPort"))
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
					logs.addLogs("ERROR : An error occured in launcher.py : "+str(connNoeud))
		else:
			# Une erreur s'est produite
			logs.addLogs("ERROR : There is not enough IP in launcher.py : "+str(tableau))
			print(len(tableau))
			print(str(tableau))
		status.stop()
		status.join()
		autresFonctions.afficherLogo()
		logs.addLogs("INFO : WTP has started, he is now listening to the port " + str(port))
		while serveur_lance:
			tcpsock.listen(10)
			(clientsocket, (ip, port)) = tcpsock.accept()
			newthread = ClientThread(ip, port, clientsocket)
			newthread.start()
			# Vérifier si WTP a recu une demande d'extinction
			fExt = open(".extinctionWTP", "r")
			contenu = fExt.read()
			fExt.close()
			if contenu == "ETEINDRE":
				# On doit éteindre WTP.
				serveur_lance = False
			elif contenu != "ALLUMER":
				fExtW = open(".extinctionWTP", "w")
				fExtW.write("ALLUMER")
				fExtW.close()
except KeyboardInterrupt:
	print(" pressed: Shutting down ...")
	print("")
fExtW = open(".extinctionWTP", "w")
fExtW.write("ETEINDRE")
fExtW.close()
logs.addLogs("INFO : WTP has correctly stopped.")
