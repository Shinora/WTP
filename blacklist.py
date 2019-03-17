import os
import logs
import config
import BDD

# Sont ici toutes les fonctions qui se réferrent à la Blacklist

def maj(ipport = ""):
	# Fonction pour noeud DNS qui permet de mettre à jour toute sa base avec un autre noeud
	BDD.verifExistBDD()
	error = 0
	if ipport == "":
		ipport = str(config.readConfFile("Blacklist"))
	else:
		if ipport != "":
			ip = ipport[:ipport.find(":")]
			port = ipport[ipport.find(":")+1:]
			connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
			if str(connexion_avec_serveur) != "=cmd ERROR":
				sendCmd = b""
				sendCmd = "=cmd BlackList sync"
				connexion_avec_serveur.send(sendCmd.encode())
				rcvCmd = connexion_avec_serveur.recv(1024)
				rcvCmd = rcvCmd.decode()
				connexion_avec_serveur.close()
				# Le noeud renvoie le nom du fichier à télécharger
				# Et son IP:PortPrincipal, sinon =cmd ERROR
				if rcvCmd != "=cmd ERROR":
					# =cmd Filename ****** ipport ******
					filename = rcvCmd[14:rcvCmd.find(" ipport ")]
					ipport = rcvCmd[rcvCmd.find(" ipport ")+8:]
					ip = ipport[:ipport.find(":")]
					port = ipport[ipport.find(":")+1:]
					error += fctsClient.CmdDemandeFichier(ip, port, filename)
					if error == 0:
						echangeListes.filetoTable(filename, "BlackList")
					else:
						error += 1
				else:
					error += 1
			else:
				error += 1
		else:
			error += 1
			logs.addLogs("ERROR : No peer ip was found in Blacklist.maj()")
	return error

def searchBlackList(name, Isrank = False):
	error = 0
	rank = 0
	rank = BDD.chercherInfo(name)
	if rank == 0:
		ipport = str(config.readConfFile("Blacklist"))
		ip = ipport[:ipport.find(":")]
		port = ipport[ipport.find(":")+1:]
		connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
		if str(connexion_avec_serveur) != "=cmd ERROR":
			sendCmd = "=cmd BlackList name "+str(name)
			connexion_avec_serveur.send(sendCmd.encode())
			rcvCmd = connexion_avec_serveur.recv(1024)
			rcvCmd = rcvCmd.decode()
			connexion_avec_serveur.close()
			rank = rcvCmd
			# Le noeud renvoie le nom du fichier à télécharger
			# Et son IP:PortPrincipal, sinon =cmd ERROR
		else:
			logs.addLogs("ERROR : Can not check the "+str(name)+" item in the blacklist")
			return 0
	if Isrank:
		return rank
	if rank == 0:
		return 0
	return 1
