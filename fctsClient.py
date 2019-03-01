#!/usr/bin/python
# -*-coding:Utf-8 -*

import autresFonctions
import echangeNoeuds
import echangeFichiers
import re
import search
import logs
from Crypto import Random
from Crypto.Cipher import AES
import config

def CmdDemandeNoeud(ip, port):
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(config.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
		request = "=cmd DemandeNoeud"
		request = request.encode()
		connNoeud.send(request)
		rcvCmd = connNoeud.recv(1024)
		connNoeud.close()
		echangeNoeuds.DemandeNoeuds(str(rcvCmd))
	return error

def CmdDemandeFichier(ip, port, file, special = "files"):
	# =cmd DemandeFichier  nom sha256.ext  ipPort IP:PORT
	# Dirriger vers la fonction DownloadFichier()
	# On va chercher l'info qu'il nous faut :
	# L'IP et le port du noeud qui va envoyer le file (sous forme IP:PORT)
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(config.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
		# Il faut trouver un port libre pour que le noeud donneur
		# puisse se connecter à ce noeud sur le bon port
		newIPPort = str(autresFonctions.connaitreIP()) + ":" + str(autresFonctions.portLibre(int(config.readConfFile("miniPort"))))
		sendCmd = "=cmd DemandeFichier  nom " + file
		sendCmd += " ipPort " + newIPPort
		sendCmd = sendCmd.encode()
		connNoeud.send(sendCmd)
		rcvCmd = connNoeud.recv(1024)
		connNoeud.close()
		if rcvCmd.decode() == "=cmd OK":
			# Le noeud distant a le file que l'on veut
			if echangeFichiers.DownloadFichier(newIPPort) == 0:
				if special == "noeuds":
					# C'est un file qui contient une liste de noeuds
					# Récuperer le nom du file
					fileName = sendCmd[sendCmd.find(" nom ")+5:sendCmd.find(" ipPort ")]
					autresFonctions.lireListeNoeuds(fileName)
				if special == "files":
					# C'est un file qui contient une liste de files
					# Récuperer le nom du file
					fileName = sendCmd[sendCmd.find(" nom ")+5:sendCmd.find(" ipPort ")]
					autresFonctions.lireListeFichiers(fileName)
			else:
				error += 1
				logs.addLogs("ERROR : Download failed")
		else:
			# Le noeud distant n'a pas le file que l'on veut
			logs.addLogs("ERROR : The peer doesn't have the file")
			error = 5
	return error

def CmdDemandeListeNoeuds(ip, port):
	sendCmd = "=cmd DemandeListeNoeuds"
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(config.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
		sendCmd = sendCmd.encode()
		connNoeud.send(sendCmd)
		fileName = connNoeud.recv(1024)
		connNoeud.close()
		CmdDemandeFichier(ip, port, fileName.decode(), "noeuds")
	return error

def CmdDemandeListeFichiers(ip, port, ext = 0):
	if ext == 1:
		sendCmd = "=cmd DemandeListeFichiersExt"
	else:
		sendCmd = "=cmd DemandeListeFichiers"
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(config.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
		sendCmd = sendCmd.encode()
		connNoeud.send(sendCmd)
		fileName = connNoeud.recv(1024)
		connNoeud.close()
		CmdDemandeFichier(ip, port, fileName.decode(), "files")
	return error

def CmdDemandeStatut(ip, port):
	error = 0
	# On demande le statut du noeud (Simple, Parser, DNS, VPN, Main)
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(config.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
		sendCmd = "=cmd status"
		connNoeud.send(sendCmd.encode())
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
		cipher = autresFonctions.createCipherAES(config.readConfFile("AESKey"))
		if str(connNoeud) == "=cmd ERROR":
			error += 1
		else:
			logs.addLogs("INFO : Connection with VPN peer etablished on port {}".format(port))
			# =cmd VPN noeud 127.0.0.1:5555 request =cmd DemandeFichier
			request = "=cmd VPN noeud " + ipPortExt + " request " + demande
			request = request.encode()
			connNoeud.send(request)
			print(connNoeud.recv(1024))
			connNoeud.close()
			# Maintenant que l'on a demandé au VPN d'executer la demande, il faut recuperer les donnnées
			# Pour cela, il faut analyser la request initiale
			if request[:19] == "=cmd DemandeFichier":
				# =cmd DemandeFichier nom sha256.ext
				CmdDemandeFichier(ip, port, request[24:])
			elif request[:17] == "=cmd DemandeNoeud":
				CmdDemandeNoeud(host, port)
			elif request[:28] == "=cmd DemandeListeFichiersExt":
				CmdDemandeListeFichiers(ip, port, 1)
			elif request[:25] == "=cmd DemandeListeFichiers":
				CmdDemandeListeFichiers(ip, port)
			elif request[:23] == "=cmd DemandeListeNoeuds":
				CmdDemandeListeNoeuds(host, port)
			elif request[:22] == "=cmd rechercher":
				# =cmd rechercher nom SHA256.ext
				search.rechercheFichierEntiere(sendCmd[20:])
			else:
				logs.addLogs("ERROR : Unknown request (VPN()) : " + str(request))
				error += 1
	else:
		error += 1
	return error

def sayHello():
	# Fonction dont le but est d'avertir des noeuds importants de sa présence
	error = 0
	ipPortMe = autresFonctions.connaitreIP()
	ip = ipport[:ipport.find(":")]
	port = ipport[ipport.find(":")+1:]
	connNoeud = autresFonctions.connectionClient(ip, port)
	cipher = autresFonctions.createCipherAES(config.readConfFile("AESKey"))
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with VPN peer etablished on port {}".format(port))
		request = "=cmd HELLO " + ipPortMe
		request = request.encode()
		connNoeud.send(request)
		print(connNoeud.recv(1024))
		connNoeud.close()
	return error
