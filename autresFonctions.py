#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import select
import sys
import sqlite3
import logs
import os
import BDD
import hashlib

def portLibre(premierPort):
	# Fonction qui cherche les ports de la machine qui sont libres
	# Et renvoie le premier trouvé, en partant du port initial, donné.
	port = True
	while port:
		clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
		    clientsocket.connect(('127.0.0.1' , premierPort))
		except ConnectionRefusedError:
		    # Le port est libre !
		    port = False
		else:
		    # Le port est déjà utilisé !
		    premierPort += 1
	return premierPort

def lsteFichiers():
	# Fonction qui retourne un fichier qui contient tous les
	# noms des fichers hébergés par le noeud,
	# et qui sont dans la BDD, un par ligne
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		BDD.creerBase()
	try: 
		os.makedirs("HOSTEDFILES")
	except OSError:
		if not os.path.isdir("HOSTEDFILES"):
			raise
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	cursor.execute("""SELECT Nom FROM Fichiers WHERE 1""")
	rows = cursor.fetchall()
	fileDir = "HOSTEDFILES/listeFichiers"
	# On vide le fichier au cas où
	vidage = open(fileDir, "w")
	vidage.write("")
	vidage.close()
	# Puis on commence l'importation
	fluxEcriture = open(fileDir, "a")
	for row in rows:
		fluxEcriture.write(row[0]+"\n")
	fluxEcriture.close()
	# Maintenant on va trouver le SHA256 du fichier
	fluxSHA = open(fileDir, "r")
	contenu = fluxSHA.read()
	fluxSHA.close()
	shaFichier = "HOSTEDFILES/" + hashlib.sha256(contenu.encode()).hexdigest()
	os.rename(fileDir, shaFichier)
	return shaFichier

def lsteNoeuds():
	# Fonction qui retourne un fichier qui contient toutes les
	# IP+PORT des noeuds connus par ce noeud
	# et qui sont dans la BDD, un par ligne
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		BDD.creerBase()
	try: 
		os.makedirs("HOSTEDFILES")
	except OSError:
		if not os.path.isdir("HOSTEDFILES"):
			raise
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	cursor.execute("""SELECT IP FROM Noeuds WHERE 1""")
	rows = cursor.fetchall()
	fileDir = "HOSTEDFILES/listeNoeuds"
	# On vide le fichier au cas où
	vidage = open(fileDir, "w")
	vidage.write("")
	vidage.close()
	# Puis on commence l'importation
	fluxEcriture = open(fileDir, "a")
	for row in rows:
		fluxEcriture.write(row[0]+"\n")
	fluxEcriture.close()
	# Maintenant on va trouver le SHA256 du fichier
	fluxSHA = open(fileDir, "r")
	contenu = fluxSHA.read()
	fluxSHA.close()
	shaFichier = "HOSTEDFILES/" + hashlib.sha256(contenu.encode()).hexdigest()
	os.rename(fileDir, shaFichier)
	return shaFichier