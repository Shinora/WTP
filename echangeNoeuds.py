#!/usr/bin/python
# -*-coding:Utf-8 -*

import socket
import select
import logs
import BDD
import sqlite3
import config

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
	if autresFonctions.verifIPPORT(IppeerPort):
		ip = IppeerPort[:IppeerPort.find(":")]
		port = IppeerPort[IppeerPort.find(":")+1:]
		connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
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
				if autresFonctions.verifIPPORT(lsteTemp):
					if blacklist.searchBlackList(lsteTemp) == 0:
						BDD.ajouterEntree("Noeuds", lsteTemp)
					else:
						logs.addLogs("ERROR : This peer is part of the Blacklist : "+str(lsteTemp))
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
	error = 0
	if autresFonctions.verifIPPORT(ipport):
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
		serveur_lance = True
		clients_connectes = []
		while serveur_lance:
			connexions_demandees, wlist, xlist = select.select([mainConn], [], [], 0.05)
			for connexion in connexions_demandees:
				connexion_avec_client, infos_connexion = connexion.accept()
				clients_connectes.append(connexion_avec_client)
			clients_a_lire = []
			try:
				clients_a_lire, wlist, xlist = select.select(clients_connectes,
						[], [], 0.05)
			except select.error:
				pass
			else:
				for client in clients_a_lire:
					rcvCmd = client.recv(1024)
					rcvCmd = rcvCmd.decode()
					if rcvCmd == "=cmd DonListeNoeuds 48":
						#Oh, un noeud demande une liste de 48 noeuds sous la forme 000.000.000.000:00000 et séparés par une virgule
						# On va chercher dans la BDD une liste de noeuds
						sendCmd = b""
						verifExistBDD()
						conn = sqlite3.connect('WTP.db')
						cursor = conn.cursor()
						datetimeAct24H = str(time.time()-86400)
						datetime24H = datetimeAct24H[:datetimeAct24H.find(".")]
						try:
							cursor.execute("""SELECT IP FROM Noeuds WHERE DerSync > ? LIMIT ?""", (datetime24H, 48))
						except Exception as e:
							logs.addLogs("ERROR : Problem with database (envNoeuds()):" + str(e))
						rows = cursor.fetchall()
						nbRes = 0
						for row in rows:
							if nbRes == 0:
								sendCmd += row[0]
							else:
								sendCmd += "," + row[0]
								nbRes += 1
						conn.close()
						sendCmd = sendCmd.encode()
						client.send(sendCmd)
		logs.addLogs("INFO : Connections closed. (EnvoiNoeuds())")
		for client in clients_connectes:
			client.close()
		mainConn.close()
	else:
		error += 1
	return error
