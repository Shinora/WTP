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

# Toutes les fonctions ici permettent de créer une sorte de VPN au sein du réseau
# Une requete passe alors par un autre noeud avant d'aller chez le destinataire

hote = '127.0.0.1'
port = int(autresFonctions.readConfFile("Port VPN"))

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(5)
logs.ajtLogs("INFO : Le service VPN est démarré, il ecoute à présent sur le port " + str(port))

serveur_lance = True
clients_connectes = []
while serveur_lance:
	connexions_demandees, wlist, xlist = select.select([connexion_principale],
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
			msg_recu = client.recv(1024)
			msg_recu = msg_recu.decode()
			if msg_recu[:19] == "=cmd VPN noeud ":
				# =cmd VPN noeud 127.0.0.1:5555 commande =cmd DemandeFichier
				ipport = msg_recu[15:msg_recu.find(" commande ")]
				commande = msg_recu[msg_recu.find(" commande ")+10:]
				ip = ipport[:ipport.find(":")]
				port = ipport[ipport.find(":")+1:]
				if commande[:19] == "=cmd DemandeFichier":
					clientCMD.CmdDemandeFichier(ip, port, commande[24:])
					# Manque du code pour transmettre les infos au noeud qui les demandait
					cmdAEnvoyer = "=cmd TravailFini"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				elif commande[:17] == "=cmd DemandeNoeud":
					clientCMD.CmdDemandeNoeud(ip, port)
					# Manque du code pour transmettre les infos au noeud qui les demandait
					cmdAEnvoyer = "=cmd TravailFini"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				elif commande[:28] == "=cmd DemandeListeFichiersExt":
					clientCMD.CmdDemandeListeFichiers(ip, port, 1)
					# Manque du code pour transmettre les infos au noeud qui les demandait
					cmdAEnvoyer = "=cmd TravailFini"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				elif commande[:25] == "=cmd DemandeListeFichiers":
					clientCMD.CmdDemandeListeFichiers(ip, port)
					# Manque du code pour transmettre les infos au noeud qui les demandait
					cmdAEnvoyer = "=cmd TravailFini"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				elif commande[:23] == "=cmd DemandeListeNoeuds":
					clientCMD.CmdDemandeListeNoeuds(ip, port)
					# Manque du code pour transmettre les infos au noeud qui les demandait
					cmdAEnvoyer = "=cmd TravailFini"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				elif commande[:22] == "=cmd rechercherFichier":
					clientCMD.CmdRechercherNom(ip, port, commande[26:])
					# Manque du code pour transmettre les infos au noeud qui les demandait
					cmdAEnvoyer = "=cmd TravailFini"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				else:
					#
					print("Inconnu !")
			else:
				# Oups... Demande non-reconnue
				# On envoie le port par défaut du noeud
				if msg_recu != '':
					print("ERROR : " + msg_recu)
					cmdAEnvoyer = "=cmd ERROR DefaultPort "+str(autresFonctions.readConfFile("Port par defaut"))
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
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


print("Fermeture des connexions")
for client in clients_connectes:
	client.close()

connexion_principale.close()
logs.ajtLogs("INFO : WTP s'est correctement arrèté.")
