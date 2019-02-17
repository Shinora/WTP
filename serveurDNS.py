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
import dns
from Crypto import Random
from Crypto.Cipher import AES

fExtW = open(".extinctionWTP", "w")
fExtW.write("ALLUMER")
fExtW.close()

host = '127.0.0.1'
port = int(autresFonctions.readConfFile("DNSPort"))

mainConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mainConn.bind((host, port))
mainConn.listen(5)
logs.addLogs("INFO : The DNS service has started, he is now listening to the port " + str(port))
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
			if rcvCmd[:9] == "=cmd DNS ":
				# =cmd DNS ...
				request = rcvCmd[9:]
				if request[:7] == "AddNDD ":
					# =cmd DNS AddNDD sha ******* ndd ******* pass *******
					sha256 = request[11:request.find(" ndd ")]
					ndd = request[request.find(" ndd ")+5:request.find(" pass ")]
					password = request[request.find(" pass ")+6:]
					erreur = dns.ajouterEntree("DNS", ndd, sha256, password)
					if erreur != 0:
						# Une erreur s'est produite et le nom de domaine n'a pas été ajouté
						if erreur == 5:
							# Le nom de domaine ets déjà pris
							sendCmd = "=cmd NDDDejaUtilise"
						else:
							sendCmd = "=cmd ERROR"
					else:
						sendCmd = "=cmd SUCCESS"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
					print(erreur)
				elif request[:9] == "AddDNSExt":
					# =cmd DNS AddDNSExt ipport ******
					erreur = dns.ajouterEntree("DNSExt", request[17:])
					if erreur != 0:
						# Une erreur s'est produite et le noeud DNS n'a pas été ajouté
						if erreur == 5:
							# Le noeud est déjà connu
							sendCmd = "=cmd IPPORTDejaUtilise"
						else:
							sendCmd = "=cmd ERROR"
					else:
						sendCmd = "=cmd SUCCESS"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
					print(erreur)
				elif request[:8] == "modifNDD":
					# =cmd DNS modifNDD ndd ****** adress ****** pass ******
					ndd = request[13:request.find(" adress ")]
					adress = request[request.find(" adress ")+8:request.find(" pass ")]
					password = request[request.find(" pass ")+6:]
					erreur = dns.modifEntree("DNS", adress, ndd, password)
					if erreur > 0:
						if erreur == 5:
							sendCmd = "=cmd MDPInvalide"
						elif erreur == 8:
							sendCmd = "=cmd NDDInconnuCree"
						else:
							sendCmd = "=cmd ERROR"
					else:
						sendCmd = "=cmd SUCCESS"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
					print(erreur)
				elif request[:8] == "supprNDD":
					# =cmd DNS supprNDD ndd ****** pass ******
					ndd = request[22:request.find(" pass ")]
					password = request[request.find(" pass ")+6:]
					erreur = dns.supprEntree("DNS", ndd, password)
					if erreur > 0:
						if erreur == 5:
							sendCmd = "=cmd MDPInvalide"
						else:
							sendCmd = "=cmd ERROR"
					else:
						sendCmd = "=cmd SUCCESS"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
					print(erreur)
				elif request[:9] == "searchSHA":
					# =cmd DNS searchSHA ndd ******
					sortie = str(dns.searchSHA(request[14:]))
					if len(sortie) >= 64:
						sendCmd = sortie
					else:
						if sortie == "INCONNU":
							sendCmd = "=cmd NNDInconnu"
						else:
							sendCmd = "=cmd ERROR"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
				elif request[:11] == "=cmd status":
					# On demande le statut du noeud (Simple, Parser, DNS, VPN, Main)
					sendCmd = "=cmd DNS"
					client.send(sendCmd.encode())
				else:
					sendCmd = "=cmd Inconnu"
					sendCmd = sendCmd.encode()
					client.send(sendCmd)
			elif rcvCmd == "=cmd DemandePresence":
				sendCmd = "=cmd Present"
				sendCmd = sendCmd.encode()
				client.send(sendCmd)
			else:
				# Oups... Demande non-reconnue
				# On envoie le port par défaut du noeud
				if rcvCmd != '':
					logs.addLogs("ERROR : Unknown error (serveurDNS.py) : " + str(rcvCmd))
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
logs.addLogs("INFO : The DNS service has been stoped successfully.")
