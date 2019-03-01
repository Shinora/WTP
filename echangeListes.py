#!/usr/bin/python
# -*-coding:Utf-8 -*

import socket
import select
import logs
import BDD
import re
from Crypto import Random
from Crypto.Cipher import AES
import config

def demandeListeFichiers(IppeerPort):
	# Fonction qui demande l'intégralité de la liste de files que contient le noeud.
	# Le noeud va chercher dans sa BDD, et faire un file temporel qui contiendra le nom des files.
	# Il va l'envoyer, puis cette fonction va le rencevoir, l'avaniser puis l'envoyer dans la BDD
	error = 0
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(IppeerPort): # Si ipport est un ip:port
		ip = IppeerPort[:IppeerPort.find(":")]
		port = IppeerPort[IppeerPort.find(":")+1:]
		connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
		cipher = autresFonctions.createCipherAES(config.readConfFile("AESKey"))
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			logs.addLogs("Connection with the peer established. (demandeListeFichiers())")
			sendCmd = b""
			sendCmd = "=cmd ListeIntegraleFichiers"
			sendCmd = sendCmd.encode()
			# On envoie le message
			ConnectionDemande.send(sendCmd)
			ListeNoeudsEnc = ConnectionDemande.recv(1024)
			ListeNoeuds = ListeNoeudsEnc.decode()
	else:
		error += 1
	return error
