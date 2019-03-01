#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import os
import os.path
import logs
import BDD
import autresFonctions
import echangeNoeuds
import echangeFichiers
import time
import search
from Crypto import Random
from Crypto.Cipher import AES
from loader import loader
import threading
import config

# Le thread principal du launcher est ici

class ThreadLauncher(threading.Thread):
	def __init__(self, ip, port, clientsocket):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsocket = clientsocket
	
	def run(self): 
		cipher = autresFonctions.createCipherAES(config.readConfFile("AESKey"))
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
				IppeerPort = "127.0.0.1:" + str(autresFonctions.portLibre(int(config.readConfFile("miniPort"))))
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
			else:
				# Oups... Demande non-reconnue...
				logs.addLogs("ERROR : Unknown request : " + str(rcvCmd))
				self.clientsocket.send("=cmd UNKNOW".encode())
			status.stop()
			status.join()
