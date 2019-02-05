#!/usr/bin/python
# -*-coding:Utf-8 -*

import socket
import autresFonctions
import echangeNoeuds
import echangeFichiers
import re
import search
import logs
from Crypto import Random
from Crypto.Cipher import AES

def CmdDemandeNoeud(ip, port):
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.ajtLogs("INFO : Connection with peer etablished on port {}".format(port))
		commande = "=cmd DemandeNoeud"
		commande = commande.encode()
		connNoeud.send(commande)
		msg_recu = connNoeud.recv(1024)
		connNoeud.close()
		echangeNoeuds.DemandeNoeuds(str(msg_recu))
	return error

def CmdDemandeFichier(ip, port, fichier, special = "non"):
	# =cmd DemandeFichier  nom sha256.ext  ipPort IP:PORT
	# Dirriger vers la fonction DownloadFichier()
	# On va chercher l'info qu'il nous faut :
	# L'IP et le port du noeud qui va envoyer le fichier (sous forme IP:PORT)
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.ajtLogs("INFO : Connection with peer etablished on port {}".format(port))
		# Il faut trouver un port libre pour que le noeud donneur
		# puisse se connecter à ce noeud sur le bon port
		newIPPort = str(autresFonctions.connaitreIP()) + ":" + str(autresFonctions.portLibre(int(autresFonctions.readConfFile("Port Min"))))
		msg_a_envoyer = "=cmd DemandeFichier  nom " + fichier
		msg_a_envoyer += " ipPort " + newIPPort
		msg_a_envoyer = msg_a_envoyer.encode()
		connNoeud.send(msg_a_envoyer)
		msg_recu = connNoeud.recv(1024)
		connNoeud.close()
		if msg_recu.decode() == "=cmd OK":
			# Le noeud distant a le fichier que l'on veut
			if echangeFichiers.DownloadFichier(newIPPort) == 0:
				if special == "noeuds":
					# C'est un fichier qui contient une liste de noeuds
					# Récuperer le nom du fichier
					nomFichier = msg_a_envoyer[msg_a_envoyer.find(" nom ")+5:msg_a_envoyer.find(" ipPort ")]
					autresFonctions.lireListeNoeuds(nomFichier)
				if special == "fichiers":
					# C'est un fichier qui contient une liste de fichiers
					# Récuperer le nom du fichier
					nomFichier = msg_a_envoyer[msg_a_envoyer.find(" nom ")+5:msg_a_envoyer.find(" ipPort ")]
					autresFonctions.lireListeFichiers(nomFichier)
			else:
				error += 1
				logs.ajtLogs("ERROR : Download failed")
		else:
			# Le noeud distant n'a pas le fichier que l'on veut
			logs.ajtLogs("ERROR : The peer doesn't have the file")
			error = 5
	return error

def CmdDemandeListeNoeuds(ip, port):
	msg_a_envoyer = "=cmd DemandeListeNoeuds"
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.ajtLogs("INFO : Connection with peer etablished on port {}".format(port))
		msg_a_envoyer = msg_a_envoyer.encode()
		connNoeud.send(msg_a_envoyer)
		nomFichier = connNoeud.recv(1024)
		connNoeud.close()
		CmdDemandeFichier(ip, port, nomFichier.decode(), "noeuds")
	return error

def CmdDemandeListeFichiers(ip, port, ext = 0):
	if ext == 1:
		msg_a_envoyer = "=cmd DemandeListeFichiersExt"
	else:
		msg_a_envoyer = "=cmd DemandeListeFichiers"
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.ajtLogs("INFO : Connection with peer etablished on port {}".format(port))
		msg_a_envoyer = msg_a_envoyer.encode()
		connNoeud.send(msg_a_envoyer)
		nomFichier = connNoeud.recv(1024)
		connNoeud.close()
		CmdDemandeFichier(ip, port, nomFichier.decode(), "fichiers")
	return error

def CmdDemandeStatut(ip, port):
	error = 0
	# On demande le statut du noeud (Simple, Parser, DNS, VPN, Main)
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.ajtLogs("INFO : Connection with peer etablished on port {}".format(port))
		msg_a_envoyer = "=cmd status"
		connNoeud.send(msg_a_envoyer.encode())
		statut = connNoeud.recv(1024)
		connNoeud.close()
		if(statut[:5] == "=cmd "):
			statut = statut[5:] # On enlève "=cmd "
		else:
			error += 1
	if error != 0:
		return error
	return statut

def VPN(demande, ipPortVPN, ipPortExt):
	error = 0
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(ipPortExt) and reg.match(ipPortVPN): # Si ipport est un ip:port
		ip = ipPortVPN[:ipPortVPN.find(":")]
		port = ipPortVPN[ipPortVPN.find(":")+1:]
		connNoeud = autresFonctions.connectionClient(ip, port)
		cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
		if str(connNoeud) == "=cmd ERROR":
			error += 1
		else:
			logs.ajtLogs("INFO : Connection with VPN peer etablished on port {}".format(port))
			# =cmd VPN noeud 127.0.0.1:5555 commande =cmd DemandeFichier
			commande = "=cmd VPN noeud " + ipPortExt + " commande " + demande
			commande = commande.encode()
			connNoeud.send(commande)
			print(connNoeud.recv(1024))
			connNoeud.close()
			# Maintenant que l'on a demandé au VPN d'executer la demande, il faut recuperer les donnnées
			# Pour cela, il faut analyser la commande initiale
			if commande[:19] == "=cmd DemandeFichier":
				# =cmd DemandeFichier nom sha256.ext
				CmdDemandeFichier(ip, port, commande[24:])
			elif commande[:17] == "=cmd DemandeNoeud":
				CmdDemandeNoeud(hote, port)
			elif commande[:28] == "=cmd DemandeListeFichiersExt":
				CmdDemandeListeFichiers(ip, port, 1)
			elif commande[:25] == "=cmd DemandeListeFichiers":
				CmdDemandeListeFichiers(ip, port)
			elif commande[:23] == "=cmd DemandeListeNoeuds":
				CmdDemandeListeNoeuds(hote, port)
			elif commande[:22] == "=cmd rechercher":
				# =cmd rechercher nom SHA256.ext
				search.rechercheFichierEntiere(msg_a_envoyer[20:])
			else:
				logs.ajtLogs("ERROR : Unknown request (VPN()) : " + str(commande))
				error += 1
	else:
		error += 1
	return error
