#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import BDD
import autresFonctions
import logs
from Crypto import Random
from Crypto.Cipher import AES

# Les fonctions ici servent à chercher des files sur le réseau

def searchFile(fileName):
	# Fonction qui a pour but de chercher sur le réseau un file
	# Il faut d'abord chercher dans la BDD, et si il n'y est pas on cherche plus spécifiquement
	# IPpeerPort est la variable qui contient l'IP Port du noeud qui possède le file
	IPpeerPort = BDD.searchFileBDD(fileName)
	if IPpeerPort == "":
		# Il faut demander aux noeuds que l'on connait
		tblNoeuds = BDD.aleatoire("Noeuds", "IP", 10)
		# On a 10 noeuds dans le tableau
		# Maintenant, il faut vérifier que au moins la moitiée des noeuds choisis aléatoirement
		# sont des noeuds "simple", puis mettre les noeuds "simple" au début du tableau
		tableauNoeudsSimple = []
		tableauSuperNoeuds = []
		for noeud in tblNoeuds:
			# On verifie chaque noeud
			fonctionNoeud = BDD.chercherInfo("Noeuds", noeud)
			if fonctionNoeud == "simple":
				tableauNoeudsSimple.append(noeud)
			if fonctionNoeud == "supernoeud" or fonctionNoeud == "DNS":
				tableauSuperNoeuds.append(noeud)
		if len(tableauNoeudsSimple) < 6:
			# Il n'y a pas assez de noeuds simples dans la liste,
			# Il faut aller en rechercher
			logs.addLogs("WARNING : Not enough simple peers")
		# On ajoute les super noeuds après les noeuds simples
		tblNoeuds = tableauNoeudsSimple + tableauSuperNoeuds
		for noeudActuel in tblNoeuds:
			# À chaque noeud on demande si il a le file ou s'il connait un noeud qui l'a
			peerIPActuel = noeudActuel[:noeudActuel.find(":")]
			peerPortActuel = noeudActuel[noeudActuel.find(":")+1:]
			# Maintenant on se connecte au noeud
			error = 0
			connexion_avec_serveur = autresFonctions.connectionClient(peerIPActuel, peerPortActuel)
			cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
			if str(connexion_avec_serveur) == "=cmd ERROR":
				error += 1
			else:
				sendCmd = b""
				sendCmd = "=cmd rechercherFichier nom " + fileName
				sendCmd = sendCmd.encode()
				connexion_avec_serveur.send(sendCmd)
				rcvCmd = connexion_avec_serveur.recv(1024)
				rcvCmd = rcvCmd.decode()
				connexion_avec_serveur.close()
				if rcvCmd != "0":
					IPpeerPort = rcvCmd
					break
	return IPpeerPort # Peut retourner "" si il ne trouve pas d'hébergeur

def chercherFichier(fileName):
	# Fonction qui regarde dans sa BDD si il y a le file en question
	retour = 0
	retour = BDD.chercherInfo("Fichiers", fileName)
	if retour != 0 and str(retour) != "None":
		# Le noeud héberge le file demandé
		# Donc on retourne son IP
		return autresFonctions.connaitreIP()+":"+str(autresFonctions.readConfFile("defaultPort"))
	retour = BDD.chercherInfo("FichiersExt", fileName)
	# ATTENTION ! Si le file n'est pas connu, 0 est retourné
	return retour

def searchNDD(url):
	# Fonction qui vérifie si le nom de file envoyé est plus petit qu'un SHA256
	# Si c'est le cas, il va chercher chez les noeuds de DNS si ils connaissent ce nom de domaine
	# Renvoie un SHA256
	sha = ""
	if len(url) <= 64:
		# Ce n'est pas un nom de file, car il est plus petit qu'un SHA256
		tableau = BDD.searchNoeud("DNS", 25)
		for noeud in tableau:
			noeud = str(noeud[0])
			ip = noeud[:noeud.find(":")]
			port = int(noeud[noeud.find(":")+1:])
			error = 0
			connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
			cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
			if str(connexion_avec_serveur) == "=cmd ERROR":
				error += 1
			else:
				sendCmd = b""
				sendCmd = "=cmd DNS searchSHA ndd " + url
				sendCmd = sendCmd.encode()
				connexion_avec_serveur.send(sendCmd)
				rcvCmd = connexion_avec_serveur.recv(1024)
				rcvCmd = rcvCmd.decode()
				connexion_avec_serveur.close()
				if rcvCmd != "=cmd NNDInconnu" and rcvCmd != "=cmd ERROR":
					# On a trouvé !!
					sha = rcvCmd
					break
	return sha

def rechercheFichierEntiere(donnee):
	# Fonction qui cherche jusqu'à trouver l'IpPort d'un noeud qui héberge le file
	# La donnée passée en paramètres peut etre un nom de domaine, ou un sha256
	# Renvoi une erreur ou IP:Port;sha256
	retour = donnee
	if len(str(donnee)) <= 63:
		# C'est un nom de domaine
		retour = ""
		nbre = 0
		while retour == "":
			nbre += 1
			retour = searchNDD(donnee)
			if retour == "" and nbre > 9:
				# La fonction n'a pas trouvé le sha256 associé à ce nom de domaine
				# Elle a pu demander jusqu'à 250 DNS différents
				return "=cmd BADDNS"
	# Si on arrive là c'est que l'on connait le sha256 du file (c'est retour)
	retour2 = str(chercherFichier(retour))
	if retour2 != "0" and str(retour2) != "None":
		# Le noeud héberge déjà le file ou le connait
		return str(retour2 + ";" + retour)
	# Le noeud ne connait pas le file
	retour3 = searchFile(retour)
	if retour3 != "":
		return str(retour3 + ";" + retour)
	return "=cmd NOHOST"
