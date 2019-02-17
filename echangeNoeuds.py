#!/usr/bin/python
# -*-coding:Utf-8 -*

import socket
import select
import logs
import BDD
import re
from Crypto import Random
from Crypto.Cipher import AES

 ####################################################
#                                                    #
# Sont ici les fonctions qui permettent de s'envoyer #
# des listes de noeuds présents sur le réseau        #
# Fonctions présetes ici :                           #
# DemandeNoeuds(IppeerPort)                         #
# EnvoiNoeuds(host, port)                            #
#                                                    #
 ####################################################


########################
#
# Ce code va permettre au noeud de demander de nouveaux 
# noeuds à un autre Noeud (Super-Noeud (SN) ou Noeud "simple")
# Il va envoyer une requete qui demande 48 noeuds. 
# (Le minimum d'IP+Ports qui peuvent tenir dans 1024 octets)
# Puis il va analiser la réponse du SN
# Et pour terminer, il va mettre le tout dans sa BDD
#
#########################

def DemandeNoeuds(IppeerPort):
	#Le paramètre à donner est l'ip suivie du port du Noeud à contacter sous la forme 000.000.000.000:00000
	#Départager l'IP et le port
	error = 0
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(IppeerPort): # Si ipport est un ip:port
		ip = IppeerPort[:IppeerPort.find(":")]
		port = IppeerPort[IppeerPort.find(":")+1:]
		connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
		cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			logs.addLogs("INFO : Connection with peer etablished (DemandeNoeuds())")
			sendCmd = b""
			sendCmd = "=cmd DonListeNoeuds 48"
			sendCmd = sendCmd.encode()
			# On envoie le message
			ConnectionDemande.send(sendCmd)
			ListeNoeudsEnc = ConnectionDemande.recv(1024)
			ListeNoeuds = ListeNoeudsEnc.decode()
			ConnectionDemande.close()
			#Les 48 IP+port sont sous la forme 000.000.000.000:00000 et sont séparés par une virgule
			#Départager les IP et les ports et envoi à la BDD par l'intermédiaire 
			# de la fonction spécifique
			for loop in range(ListeNoeuds.count(',')+1):
				lsteTemp = ListeNoeuds[:ListeNoeuds.find(',')]
				ListeNoeuds = ListeNoeuds[ListeNoeuds.find(',')+1:]
				reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})$")
				if reg.match(lsteTemp): # Si lsteTemp est un ip:port
					BDD.ajouterEntree("Noeuds", lsteTemp)
				else:
					logs.addLogs("ERROR : The variable isn't a IP:PORT in DemandeNoeuds() : "+str(lsteTemp))
			logs.addLogs("INFO : Connection closed. (DemandeNoeuds())")
	else:
		error += 1
	return error

########################
#
# Ce code va permettre au noeud d'envoyer de nouveaux
# noeuds au demandeur
# Il va envoyer une requete qui contient 48 noeuds.
# (Le minimum d'IP+Ports qui peuvent tenir dans 1024 octets)
#
#########################

def EnvoiNoeuds(IppeerPort):
	#Départager l'IP et le port
	error = 0
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(ipport): # Si ipport est un ip:port
		pos1 = IppeerPort.find(":")
		pos1 = pos1+1
		pos2 = len(IppeerPort)
		port = IppeerPort[pos1:pos2]
		pos1 = pos1-1
		host = IppeerPort[0:pos1]
		mainConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		mainConn.bind((host, int(port)))
		mainConn.listen(5)
		logs.addLogs("INFO : Listen on port " + str(port) + ". (EnvoiNoeuds())")
		cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
		serveur_lance = True
		clients_connectes = []
		while serveur_lance:
			# On va vérifier que de nouveaux clients ne demandent pas à se connecter
			# Pour cela, on écoute la mainConn en lecture
			# On attend maximum 50ms
			connexions_demandees, wlist, xlist = select.select([mainConn], [], [], 0.05)
			for connexion in connexions_demandees:
				connexion_avec_client, infos_connexion = connexion.accept()
				# On ajoute le socket connecté à la liste des clients
				clients_connectes.append(connexion_avec_client)
			# Maintenant, on écoute la liste des clients connectés
			# Les clients renvoyés par select sont ceux devant être lus (recv)
			# On attend là encore 50ms maximum
			# On enferme l'appel à select.select dans un bloc try
			# En effet, si la liste de clients connectés est vide, une exception
			# Peut être levée
			clients_a_lire = []
			try:
				clients_a_lire, wlist, xlist = select.select(clients_connectes,
						[], [], 0.05)
			except select.error:
				pass
			else:
				# On parcourt la liste des clients à lire
				for client in clients_a_lire:
					# Client est de type socket
					rcvCmd = client.recv(1024)
					# Peut planter si le message contient des caractères spéciaux
					rcvCmd = rcvCmd.decode()
					if rcvCmd == "=cmd DonListeNoeuds 48":
						#Oh, un noeud demande une liste de 48 noeuds sous la forme 000.000.000.000:00000 et séparés par une virgule
						# On va chercher dans la BDD une liste de noeuds
						sendCmd = b""
						sendCmd = BDD.envNoeuds(48)
						sendCmd = sendCmd.encode()
						client.send(sendCmd)
		logs.addLogs("INFO : Connections closed. (EnvoiNoeuds())")
		for client in clients_connectes:
			client.close()
		mainConn.close()
	else:
		error += 1
	return error
