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
		for x in range(len(tblNoeuds)):
			# On verifie chaque noeud
			fonctionNoeud = BDD.chercherInfo("Noeuds", tblNoeuds[x], "Fonction")
			if fonctionNoeud == "simple":
				tableauNoeudsSimple.append(tblNoeuds[x])
			if fonctionNoeud == "supernoeud":
				tableauSuperNoeuds.append(tblNoeuds[x])
		if len(tableauNoeudsSimple) < 6:
			# Il n'y a pas assez de noeuds simples dans la liste,
			# Il faut aller en rechercher
			print("Pas assez de noeuds simples")
		# On ajoute les super noeuds après les noeuds simples
		tblNoeuds = tableauNoeudsSimple + tableauSuperNoeuds
		for x in range(len(tblNoeuds)):
			# À chaque noeud on demande si il a le fichier ou s'il connait un noeud qui l'a
			noeudActuel = tblNoeuds[x]
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
	return IPPortNoeud

def chercherFichier(nomFichier):
	# Fonction qui regarde dans sa BDD si il y a le fichier en question
	retour = 0
	retour = BDD.chercherInfo("Fichiers", "Nom", "id")
	if retour != 0:
		# Le noeud héberge le fichier demandé
		# Donc on retourne son IP
		return autresFonctions.connaitreIP()
	else:
		retour = BDD.chercherInfo("FichiersExt", "Nom", "IP")
		# ATTENTION ! Si le fichier n'est pas connu, 0 est retourné
		return retour