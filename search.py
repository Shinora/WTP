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
		for x in range(10):
			# On verifie chaque noeud
			fonctionNoeud = BDD.chercherInfo("Noeuds", tblNoeuds[x], "Fonction")
			if fonctionNoeud == "simple":
				tableauNoeudsSimple.append(tblNoeuds[x])
			if fonctionNoeud == "supernoeud":
				tableauSuperNoeuds.append(tblNoeuds[x])
	return IPPortNoeud

