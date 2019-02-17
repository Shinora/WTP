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
import fctsClient
from Crypto import Random
from Crypto.Cipher import AES

# Toutes les fonctions ici permettent de créer une sorte de VPN au sein du réseau
# Une requete passe alors par un autre noeud avant d'aller chez le destinataire

host = '127.0.0.1'
port = int(autresFonctions.readConfFile("VPNPort"))
fExtW = open(".extinctionWTP", "w")
fExtW.write("ALLUMER")
fExtW.close()

mainConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mainConn.bind((host, port))
mainConn.listen(5)
logs.addLogs("INFO : The VPN service has started, he is now listening to the port " + str(port))
cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
serveur_lance = True
clients_connectes = []
while serveur_lance:
	connexions_demandees, wlist, xlist = select.select([mainConn],
		[], [], 0.05)
	for connexion in connexions_demandees:
		connexion_avec_client, infos_connexion = connexion.accept()
		clients_connectes.append(connexion_avec_client)
	clients_a_lire = []
	try:
		clients_a_lire, wlist, xlist = select.select(clients_connectes, [], [], 0.05)
	except select.error:
		pass
	else:
		for client in clients_a_lire:
			rcvCmd = client.recv(1024)
			rcvCmd = rcvCmd.decode()
			if rcvCmd[:15] == "=cmd VPN noeud ":
				# =cmd VPN noeud 127.0.0.1:5555 request =cmd DemandeFichier
				ipport = rcvCmd[15:rcvCmd.find(" request ")]
				request = rcvCmd[rcvCmd.find(" request ")+10:]
				ip = ipport[:ipport.find(":")]
				port = ipport[ipport.find(":")+1:]
				if request[:19] == "=cmd DemandeFichier":
					fctsClient.CmdDemandeFichier(ip, port, request[24:])
					# Manque du code pour transmettre les infos au noeud qui les demandait
					sendCmd = "=cmd TravailFini"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
				elif request[:17] == "=cmd DemandeNoeud":
					fctsClient.CmdDemandeNoeud(ip, port)
					# Manque du code pour transmettre les infos au noeud qui les demandait
					sendCmd = "=cmd TravailFini"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
				elif request[:28] == "=cmd DemandeListeFichiersExt":
					fctsClient.CmdDemandeListeFichiers(ip, port, 1)
					# Manque du code pour transmettre les infos au noeud qui les demandait
					sendCmd = "=cmd TravailFini"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
				elif request[:25] == "=cmd DemandeListeFichiers":
					fctsClient.CmdDemandeListeFichiers(ip, port)
					# Manque du code pour transmettre les infos au noeud qui les demandait
					sendCmd = "=cmd TravailFini"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
				elif request[:23] == "=cmd DemandeListeNoeuds":
					fctsClient.CmdDemandeListeNoeuds(ip, port)
					# Manque du code pour transmettre les infos au noeud qui les demandait
					sendCmd = "=cmd TravailFini"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
				elif request[:22] == "=cmd rechercher":
					# =cmd rechercher nom ******
					search.rechercheFichierEntiere(request[20:])
					# Manque du code pour transmettre les infos au noeud qui les demandait
					sendCmd = "=cmd TravailFini"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
				elif request[:11] == "=cmd status":
					# On demande le statut du noeud (Simple, Parser, DNS, VPN, Main)
					sendCmd = "=cmd VPN"
					client.send(sendCmd.encode())
				else:
					logs.addLogs("ERROR : Unknown request (vpn.py) : " + str(request))
			else:
				# Oups... Demande non-reconnue
				# On envoie le port par défaut du noeud
				if rcvCmd != '':
					logs.addLogs("ERROR : Unknown request (vpn.py) : " + str(rcvCmd))
					sendCmd = "=cmd ERROR DefaultPort "+str(autresFonctions.readConfFile("defaultPort"))
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
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
for client in clients_connectes:
	client.close()
mainConn.close()
logs.addLogs("INFO : WTP service has been stoped successfully.")
