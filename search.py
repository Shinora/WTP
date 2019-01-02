#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import BDD
import autresFonctions

# Les fonctions ici servent à chercher des fichiers sur le réseau

def searchFile(nomFichier):
	# Fonction qui a pour but de chercher sur le réseau un fichier
	# Il faut d'abord chercher dans la BDD, et si il n'y est pas on cherche plus spécifiquement
	# IPPortNoeud est la variable qui contient l'IP Port du noeud qui possède le fichier
	IPPortNoeud = BDD.searchFileBDD(nomFichier)
	if IPPortNoeud == "":
		# Il faut demander aux noeuds que l'on connait
		print("En cours...")
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
			if fonctionNoeud == "supernoeud":
				tableauSuperNoeuds.append(noeud)
		if len(tableauNoeudsSimple) < 6:
			# Il n'y a pas assez de noeuds simples dans la liste,
			# Il faut aller en rechercher
			print("Pas assez de noeuds simples")
		# On ajoute les super noeuds après les noeuds simples
		tblNoeuds = tableauNoeudsSimple + tableauSuperNoeuds
		for noeudActuel in tblNoeuds:
			# À chaque noeud on demande si il a le fichier ou s'il connait un noeud qui l'a
			IPNoeudActuel = noeudActuel[:noeudActuel.find(":")]
			PortNoeudActuel = noeudActuel[noeudActuel.find(":")+1:]
			# Maintenant on se connecte au noeud
			connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connexion_avec_serveur.connect((IPNoeudActuel, PortNoeudActuel))
			msg_a_envoyer = b""
			msg_a_envoyer = "=cmd rechercherFichier nom " + nomFichier
			msg_a_envoyer = msg_a_envoyer.encode()
			connexion_avec_serveur.send(msg_a_envoyer)
			msg_recu = connexion_avec_serveur.recv(1024)
			msg_recu = msg_recu.decode()
			connexion_avec_serveur.close()
			if msg_recu != "0":
				IPPortNoeud = msg_recu
				break
	return IPPortNoeud # Peut retourner "" si il ne trouve pas d'hébergeur

def chercherFichier(nomFichier):
	# Fonction qui regarde dans sa BDD si il y a le fichier en question
	retour = 0
	retour = BDD.chercherInfo("Fichiers", nomFichier)
	print("Retour : " + str(retour))
	if retour != 0 and str(retour) != "None":
		# Le noeud héberge le fichier demandé
		# Donc on retourne son IP
		print("azerty")
		return autresFonctions.connaitreIP()
	retour = BDD.chercherInfo("FichiersExt", nomFichier)
	# ATTENTION ! Si le fichier n'est pas connu, 0 est retourné
	return retour

def searchNDD(url):
	# Fonction qui vérifie si le nom de fichier envoyé est plus petit qu'un SHA256
	# Si c'est le cas, il va chercher chez les noeuds de DNS si ils connaissent ce nom de domaine
	# Renvoie un SHA256
	sha = ""
	if len(url) <= 64:
		# Ce n'est pas un nom de fichier, car il est plus petit qu'un SHA256
		tableau = BDD.searchNoeud("DNS", 25)
		for noeud in tableau:
			noeud = str(noeud[0])
			ip = noeud[:noeud.find(":")]
			port = int(noeud[noeud.find(":")+1:])
			connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connexion_avec_serveur.connect((ip, port))
			msg_a_envoyer = b""
			msg_a_envoyer = "=cmd DNS searchSHA ndd " + url
			print("MSG : " + str(msg_a_envoyer))
			msg_a_envoyer = msg_a_envoyer.encode()
			connexion_avec_serveur.send(msg_a_envoyer)
			msg_recu = connexion_avec_serveur.recv(1024)
			msg_recu = msg_recu.decode()
			connexion_avec_serveur.close()
			if msg_recu != "=cmd NNDInconnu" and msg_recu != "=cmd ERROR":
				# On a trouvé !!
				sha = msg_recu
				print("Trouvé")
				break
	return sha

def rechercheFichierEntiere(donnee):
	# Fonction qui cherche jusqu'à trouver l'IpPort d'un noeud qui héberge le fichier
	# La donnée passée en paramètres peut etre un nom de domaine, ou un sha256
	# Renvoi une erreur ou IP:Port;sha256
	retour = ""
	print("ICI")
	if len(str(donnee)) <= 63:
		print("NDD")
		# C'est un nom de domaine
		retour = ""
		nbre = 0
		while retour == "":
			print("WHILE")
			nbre += 1
			retour = searchNDD(donnee)
			if retour == "" and nbre > 9:
				print("IF")
				# La fonction n'a pas trouvé le sha256 associé à ce nom de domaine
				# Elle a pu demander jusqu'à 250 DNS différents
				return "=cmd BADDNS"
	# Si on arrive là c'est que l'on connait le sha256 du fichier (c'est retour)
	print("APRES")
	retour2 = str(chercherFichier(retour))
	print("retour2")
	if retour2 != "0" and str(retour2) != "None":
		print("if")
		# Le noeud héberge déjà le fichier ou le connait
		return str(retour2 + ";" + retour)
	# Le noeud ne connait pas le fichier
	print("cestlafin")
	retour3 = searchFile(retour)
	if retour3 != "":
		return str(retour3 + ";" + retour)
	return "=cmd NOHOST"
