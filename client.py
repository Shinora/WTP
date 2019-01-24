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

hote = "127.0.0.1"
port = int(autresFonctions.readConfFile("Port par defaut"))

autresFonctions.afficherLogo()
msg_a_envoyer = b""
while msg_a_envoyer != b"fin":
	msg_a_envoyer = input(">>> ")
	if msg_a_envoyer == "=cmd DemandeNoeud":
		fctsClient.CmdDemandeNoeud(hote, port)
	elif msg_a_envoyer[:19] == "=cmd DemandeFichier":
		# =cmd DemandeFichier nom sha256.ext
		fctsClient.CmdDemandeFichier(hote, port, msg_a_envoyer[24:])
	elif msg_a_envoyer == "=cmd DemandeListeNoeuds":
		fctsClient.CmdDemandeListeNoeuds(hote, port)
	elif msg_a_envoyer == "=cmd DemandeListeFichiers":
		fctsClient.CmdDemandeListeFichiers(hote, port)
	elif msg_a_envoyer[:19] == "=cmd rechercher nom":
		# =cmd rechercher nom SHA256.ext
		sortie = search.rechercheFichierEntiere(msg_a_envoyer[20:])
		ipport = sortie[:sortie.find(";")]
		sha = sortie[sortie.find(";")+1:]
		if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', ipport):
			# C'est un IPPort
			# On envoi vers la fonction qui télécharge le fichier
			ip = ipport[:ipport.find(":")]
			port = int(ipport[ipport.find(":")+1:])
			fctsClient.CmdDemandeFichier(hote, port, sha)
		else:
			# C'est une erreur
			print(sortie)
	else:
		error = 0
		connexion_avec_serveur = autresFonctions.connectionClient(hote, port)
		cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			connexion_avec_serveur.send(msg_a_envoyer.encode())
			msg_recu = connexion_avec_serveur.recv(1024).decode()
			connexion_avec_serveur.close()
			print(msg_recu)
print("Fait.")
