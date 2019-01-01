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

hote = '127.0.0.1'
port = int(autresFonctions.readConfFile("Port DNS"))

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(5)
logs.ajtLogs("INFO : Le service DNS est démarré, il ecoute à présent sur le port " + str(port))

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
			if msg_recu[:9] == "=cmd DNS ":
				# =cmd DNS ...
				commande = msg_recu[9:]
				if commande[:7] == "AddNDD ":
					# =cmd DNS AddDNS sha ******* ndd ******* pass *******
					sha256 = commande[11:commande.find(" ndd ")]
					ndd = commande[commande.find(" nnd ")+5:commande.find(" pass ")]
					password = commande[commande.find(" pass ")+6:]
					erreur = dns.ajouterEntree("DNS", sha256, ndd, password)
					if erreur != 0:
						# Une erreur s'est produite et le nom de domaine n'a pas été ajouté
						if erreur == 7:
							# Le nom de domaine ets déjà pris
							cmdAEnvoyer = "=cmd NDDDejaUtilise"
						else:
							cmdAEnvoyer = "=cmd ERROR"
					else:
						cmdAEnvoyer = "=cmd SUCCESS"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				elif commande[:9] == "AddDNSExt":
					# =cmd DNS AddDNSExt ipport ******
					erreur = dns.ajouterEntree("DNSExt", commande[17:])
					if erreur != 0:
						# Une erreur s'est produite et le noeud DNS n'a pas été ajouté
						if erreur == 7:
							# Le noeud est déjà connu
							cmdAEnvoyer = "=cmd IPPORTDejaUtilise"
						else:
							cmdAEnvoyer = "=cmd ERROR"
					else:
						cmdAEnvoyer = "=cmd SUCCESS"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				elif commande[:8] == "modifNDD":
					# =cmd DNS modifNDD ndd ****** adress ****** pass ******
					ndd = commande[22:commande.find(" adress ")]
					adress = commande[commande.find(" adress ")+8:commande.find(" pass ")]
					password = commande[commande.find(" pass ")+6:]
					erreur = dns.modifEntree("DNS", adress, ndd, password)
					if erreur > 0:
						if erreur == 5:
							cmdAEnvoyer = "=cmd MDPInvalide"
						else:
							cmdAEnvoyer = "=cmd ERROR"
					else:
						cmdAEnvoyer = "=cmd SUCCESS"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				elif commande[:8] == "supprNDD":
					# =cmd DNS supprNDD ndd ****** pass ******
					ndd = commande[22:commande.find(" pass ")]
					password = commande[commande.find(" pass ")+6:]
					erreur = dns.supprEntree("DNS", ndd, password)
					if erreur > 0:
						if erreur == 5:
							cmdAEnvoyer = "=cmd MDPInvalide"
						else:
							cmdAEnvoyer = "=cmd ERROR"
					else:
						cmdAEnvoyer = "=cmd SUCCESS"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				elif commande[:9] == "searchSHA":
					# =cmd DNS searchSHA ndd ******
					sortie = str(dns.searchSHA(ndd))
					if len(sortie) >= 64:
						cmdAEnvoyer = sortie
					else:
						if sortie == "INCONNU":
							cmdAEnvoyer = "=cmd NNDInconnu"
						else:
							cmdAEnvoyer = "=cmd ERROR"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
				else:
					#
					print("Inconnu !")
					cmdAEnvoyer = "=cmd Inconnu"
					cmdAEnvoyer = cmdAEnvoyer.encode()
					client.send(cmdAEnvoyer)
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
logs.ajtLogs("INFO : Le serveur DNS s'est correctement arrèté.")
