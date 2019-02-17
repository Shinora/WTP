#!/usr/bin/python
# -*-coding:Utf-8 -*

import socket
import autresFonctions
import echangeNoeuds
import echangeFichiers
import re
import search
import fctsClient
from Crypto import Random
from Crypto.Cipher import AES

host = "127.0.0.1"
port = int(autresFonctions.readConfFile("defaultPort"))

autresFonctions.afficherLogo()
sendCmd = b""
while sendCmd != b"fin":
	sendCmd = input(">>> ")
	if sendCmd == "=cmd DemandeNoeud":
		fctsClient.CmdDemandeNoeud(host, port)
	elif sendCmd[:19] == "=cmd DemandeFichier":
		# =cmd DemandeFichier nom sha256.ext
		fctsClient.CmdDemandeFichier(host, port, sendCmd[24:])
	elif sendCmd == "=cmd DemandeListeNoeuds":
		fctsClient.CmdDemandeListeNoeuds(host, port)
	elif sendCmd == "=cmd DemandeListeFichiers":
		fctsClient.CmdDemandeListeFichiers(host, port)
	elif sendCmd[:19] == "=cmd rechercher nom":
		# =cmd rechercher nom SHA256.ext
		sortie = search.rechercheFichierEntiere(sendCmd[20:])
		ipport = sortie[:sortie.find(";")]
		sha = sortie[sortie.find(";")+1:]
		if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', ipport):
			# C'est un IPPort
			# On envoi vers la fonction qui télécharge le file
			ip = ipport[:ipport.find(":")]
			port = int(ipport[ipport.find(":")+1:])
			fctsClient.CmdDemandeFichier(host, port, sha)
		else:
			# C'est une erreur
			print(sortie)
	else:
		error = 0
		connexion_avec_serveur = autresFonctions.connectionClient(host, port)
		cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			connexion_avec_serveur.send(sendCmd.encode())
			rcvCmd = connexion_avec_serveur.recv(1024).decode()
			connexion_avec_serveur.close()
			print(rcvCmd)
	print("Fait.")
