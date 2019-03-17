import autresFonctions
import echangeNoeuds
import echangeFichiers
import search
import logs
import config
import echangeListes
import threading
import time
import os
import blacklist

def CmdDemandeNoeud(ip, port):
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
		request = "=cmd DemandeNoeud"
		request = request.encode()
		connNoeud.send(request)
		rcvCmd = connNoeud.recv(1024)
		connNoeud.close()
		error += echangeNoeuds.DemandeNoeuds(str(rcvCmd))
	return error

def CmdDemandeFichier(ip, port, file):
	if blacklist.searchBlackList(file) != 0:
		logs.addLogs("ERROR : This file is part of the Blacklist : "+str(file))
		return 1
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
		# Il faut trouver un port libre pour que le noeud donneur
		# puisse se connecter à ce noeud sur le bon port
		freePort = autresFonctions.portLibre(int(config.readConfFile("miniPort")))
		temp = str(time.time())
		thrdDown = echangeFichiers.downFile(file, int(freePort), temp)
		thrdDown.start()
		newIPPort = str(autresFonctions.connaitreIP()) + ":" + str(freePort)
		sendCmd = "=cmd DemandeFichier  nom " + str(file) + " ipport " + str(newIPPort)
		connNoeud.send(sendCmd.encode())
		connNoeud.close()
		thrdDown.join()
		# Lire le fichier temporaire pour savoir si il y a eut des erreurs
		try:
			f = open(".TEMP/"+temp, "r")
			error += int(f.read())
			f.close()
			os.remove(".TEMP/"+temp)
		except Exception as e:
			error += 1
			logs.addLogs("ERROR : An error occured in CmdDemandeFichier : "+str(e))
	return error

def CmdDemandeListeNoeuds(ip, port):
	sendCmd = "=cmd DemandeListeNoeuds"
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
		sendCmd = sendCmd.encode()
		connNoeud.send(sendCmd)
		fileName = connNoeud.recv(1024)
		connNoeud.close()
		error += CmdDemandeFichier(ip, port, fileName.decode())
		echangeListes.filetoTable(fileName.decode(), "Noeuds")
	return error

def CmdDemandeListeFichiers(ip, port, ext = 0):
	if ext == 1:
		sendCmd = "=cmd DemandeListeFichiersExt"
	else:
		sendCmd = "=cmd DemandeListeFichiers"
	error = 0
	connNoeud = autresFonctions.connectionClient(ip, port)
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with peer etablished on port {}".format(port))
		sendCmd = sendCmd.encode()
		connNoeud.send(sendCmd)
		fileName = connNoeud.recv(1024)
		connNoeud.close()
		CmdDemandeFichier(ip, port, fileName.decode())
		echangeListes.filetoTable(filename.decode(), "Fichiers")
	return error

def CmdDemandeStatut(ip, port):
	error = 0
	# On demande le statut du noeud (Simple, Parser, DNS, VPN, Main)
	connNoeud = autresFonctions.connectionClient(ip, port)
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
	if autresFonctions.verifIPPORT(ipPortExt) and reg.match(ipPortVPN):
		ip = ipPortVPN[:ipPortVPN.find(":")]
		port = ipPortVPN[ipPortVPN.find(":")+1:]
		connNoeud = autresFonctions.connectionClient(ip, port)
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
				error += CmdDemandeFichier(ip, port, request[24:])
			elif request[:17] == "=cmd DemandeNoeud":
				CmdDemandeNoeud(ip, port)
			elif request[:28] == "=cmd DemandeListeFichiersExt":
				CmdDemandeListeFichiers(ip, port, 1)
			elif request[:25] == "=cmd DemandeListeFichiers":
				CmdDemandeListeFichiers(ip, port)
			elif request[:23] == "=cmd DemandeListeNoeuds":
				CmdDemandeListeNoeuds(ip, port)
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
	connNoeud = autresFonctions.connectionClient(ipport)
	if str(connNoeud) == "=cmd ERROR":
		error += 1
	else:
		logs.addLogs("INFO : Connection with VPN peer etablished")
		request = "=cmd HELLO " + ipPortMe
		request = request.encode()
		connNoeud.send(request)
		print(connNoeud.recv(1024))
		connNoeud.close()
	return error
