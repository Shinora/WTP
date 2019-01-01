#! /usr/bin/python
# -*- coding:utf-8 -*-

import logs
import sys
import os
import math
import time
import hashlib
import sqlite3

def addNDD(ipport, sha, ndd, password):
	ip = ipport[:ipport.find(":")]
	port = ipport[ipport.find(":")+1:]
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	print("Connexion établie avec le DNS sur le port {}".format(port))
	# =cmd DNS AddDNS sha ******* ndd ******* pass *******
	commande = "=cmd DNS AddDNS sha " + str(sha) + " ndd " + str(ndd) + " pass " + str(password)
	commande = commande.encode()
	connexion_avec_serveur.send(commande)
	message = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()
	erreur = 0
	if message == "=cmd NDDDejaUtilise":
		erreur = 5
		print("Le nom de domaine est déjà utilisé. S'il vous appartient, vous pouvez le modifier à condition de connaitre le mot de passe")
	elif message == "=cmd SUCCESS":
		print("Le nom de domaine et l'adresse SHA256 ont bien été associés.")
	else:
		print("Une erreur indeterminée s'est produite. Veuillez réessayer plus tard ou changer de noeud DNS.")
		erreur = 1
	return erreur

def addNoeudDNS(ipport, ipportNoeud):
	ip = ipport[:ipport.find(":")]
	port = ipport[ipport.find(":")+1:]
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	print("Connexion établie avec le DNS sur le port {}".format(port))
	# =cmd DNS AddDNSExt ipport ******
	commande = "=cmd DNS AddDNSExt ipport " + ipportNoeud
	commande = commande.encode()
	connexion_avec_serveur.send(commande)
	message = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()
	erreur = 0
	if message == "=cmd IPPORTDejaUtilise":
		erreur = 5
		print("Le noeud DNS est déjà connu par le receveur.")
	elif message == "=cmd SUCCESS":
		print("Le noeud DNS a bien été ajouté à la base du receveur.")
	else:
		print("Une erreur indeterminée s'est produite. Veuillez réessayer plus tard ou changer de noeud DNS.")
		erreur = 1
	return erreur

def modifNDD(ipport, ndd, adress, password):
	ip = ipport[:ipport.find(":")]
	port = ipport[ipport.find(":")+1:]
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	print("Connexion établie avec le DNS sur le port {}".format(port))
	# =cmd DNS modifNDD ndd ****** adress ****** pass ******
	commande = "=cmd DNS modifNDD ndd " + str(ndd) + " adress " + str(adress) + " pass " + str(password)
	commande = commande.encode()
	connexion_avec_serveur.send(commande)
	message = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()
	erreur = 0
	if message == "=cmd IPPORTDejaUtilise":
		erreur = 5
		print("Le noeud DNS est déjà connu par le receveur.")
	elif message == "=cmd SUCCESS":
		print("Le noeud DNS a bien été ajouté à la base du receveur.")
	else:
		print("Une erreur indeterminée s'est produite. Veuillez réessayer plus tard ou changer de noeud DNS.")
		erreur = 1
	return erreur

def supprNDD(ipport, ndd, password):
	ip = ipport[:ipport.find(":")]
	port = ipport[ipport.find(":")+1:]
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	print("Connexion établie avec le DNS sur le port {}".format(port))
	# =cmd DNS supprNDD ndd ****** pass ******
	commande = "=cmd DNS supprNDD ndd " + str(ndd) + " pass " + str(password)
	commande = commande.encode()
	connexion_avec_serveur.send(commande)
	message = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()

def remAdr(NDD):
	# Fonction pour supprimer une adresse au DNS
	print("BONJOUR")

def searchAdr(NDD):
	# Fonction pour chercher le SHA256 correspondant à l'adresse
	print("BONJOUR")

def showAll(limit = 150):
	# Fonction qui affiche un certain nombre de noms de domaines (défaut 150)
	# Qui sont dans la base du noeud DNS
	print("BONJOUR")

######################################################################
##########################  BASE DE DONNÉES ##########################
######################################################################

def creerBase():
	# Fonction qui a pour seul but de créer la base de données
	# si le fichier la contenant n'existe pas.
	conn = sqlite3.connect('WTPDNS.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS DNS(
				id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
				SHA256 TEXT,
				NDD TEXT,
				PASSWORD TEXT,
				DateAjout INTEGER
			)
		""")
		conn.commit()
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS DNSExt(
				id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
				IPPORT TEXT,
				DateAjout TEXT
			)
		""")
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("DNS : ERREUR : Problème avec base de données (creerBase()) :" + str(e))
	conn.close()

def ajouterEntree(nomTable, entree, entree1 = "", entree2 = ""):
	# Fonction qui permet d'ajouter une entrée à une table de la base
	verifExistBDD()
	# Vérifier si l'entrée existe déjà dans la BDD.
	# Si il existe on ne fait rien
	# Si il n'existe pas, on l'ajoute
	conn = sqlite3.connect('WTPDNS.db')
	cursor = conn.cursor()
	try:
		if nomTable == "DNS":
			cursor.execute("""SELECT id FROM ? WHERE NDD = ?""", (nomTable, entree))
		elif nomTable == "DNSExt":
			cursor.execute("""SELECT id FROM ? WHERE IPPORT = ?""", (nomTable, entree))
		else:
			logs.ajtLogs("DNS : ERREUR : Nom de la table non reconnu (ajouterEntree()) : " + str(nomTable))
			problem += 1
	except Exception as e:
		logs.ajtLogs("DNS : ERREUR : Problème avec base de données (ajouterEntree()):" + str(e))
		problem += 1
	else:
		nbRes = 0
		rows = cursor.fetchall()
		for row in rows:
			nbRes += 1
		if nbRes != 0:
			# L'entrée existe déjà
			problem = 5
			if nbRes > 1:
				logs.ajtLogs("DNS : ERREUR : Entrée présente plusieurs fois dans la base. (ajouterEntree())")
				problem = 7
		else:
			datetimeAct = str(time.time())
			datetimeAct = datetimeAct[:datetimeAct.find(".")]
			# En fonction de la table, il n'y a pas les mêmes champs à remplir
			try:
				if nomTable == "DNS":
					if entree1 != "" and entree2 != "":
						passwordHash = hashlib.sha256(str(entree2).encode()).hexdigest()
						cursor.execute("""INSERT INTO ? (SHA256, NDD, PASSWORD, DateAjout) VALUES (?, ?, ?, ?)""", (nomTable, entree, entree1, passwordHash, datetimeAct))
					else:
						logs.ajtLogs("DNS : ERREUR : Il manque des paramètres lors de l'appel de la fonction (ajouterEntree())")
						problem += 1
				elif nomTable == "DNSExt":
					cheminFichier = "HOSTEDFILES/" + entree
					cursor.execute("""INSERT INTO ? (IPPORT, DateAjout) VALUES (?, ?)""", (nomTable, entree, datetimeAct))
			except Exception as e:
				conn.rollback()
				logs.ajtLogs("DNS : ERREUR : Problème avec base de données (ajouterEntree()):" + str(e))
				problem += 1
	conn.close()
	return problem

def envLste(nomTable, nbreEntrees = 150):
	# Fonction qui permet de lire un nombre d'entrées et de les renvoyer
	# Paramètre : Le nomnbre de noeuds à renvoyer (par défaut 150)
	listeEntrees = ""
	verifExistBDD()
	conn = sqlite3.connect('WTPDNS.db')
	cursor = conn.cursor()
	try:
		if nomTable == "DNS":
			cursor.execute("""SELECT SHA256, NDD FROM DNS LIMIT ? ORDER BY id DESC""", (nbreEntrees,))
		elif nomTable == "DNSExt":
			cursor.execute("""SELECT IPPORT FROM DNSExt LIMIT ? ORDER BY id DESC""", (nbreEntrees,))
		else:
			logs.ajtLogs("DNS : Erreur : Nom de la table non reconnu (envLste()) : " + str(nomTable))
	except Exception as e:
		logs.ajtLogs("DNS : ERREUR : Problème avec base de données (envLste()):" + str(e))
	rows = cursor.fetchall()
	nbRes = 0
	for row in rows:
		if nbRes == 0:
			nbRes = 1
			listeEntrees += row[0]
			if nomTable == "DNS": # Sous la forme SHA256:NDD,SHA256:NDD sinon IPPORT,IPPORT
				listeEntrees += ":" + row[1]
		else:
			listeEntrees += "," + row[0]
			if nomTable == "DNS": # Sous la forme SHA256:NDD,SHA256:NDD sinon IPPORT,IPPORT
				listeEntrees += ":" + row[1]
	conn.close()
	return listeEntrees

def supprEntree(nomTable, entree, entree1 = ""):
	# Fonction qui permet de supprimer une entrée dans une table
	problem = 0
	verifExistBDD()
	conn = sqlite3.connect('WTPDNS.db')
	cursor = conn.cursor()
	try:
		if nomTable == "DNS":
			if entree1 != "":
				# On vérifie que le mot de passe hashé est égal à celui de la base de données,
				# et si c'est le cas on peut suprimer la ligne
				cursor.execute("""SELECT PASSWORD FROM DNS WHERE NDD = ?""", (entree1,))
				rows = cursor.fetchall()
				nbRes = 0
				passwordHash = hashlib.sha256(str(entree1).encode()).hexdigest()
				for row in rows:
					if row[0] == passwordHash:
						cursor.execute("""DELETE FROM DNS WHERE NDD = ? AND PASSWORD = ?""", (entree, passwordHash))
					else:
						print("ERREUR : Le mot de passe n'est pas valide.")
						problem = 5
			else:
				logs.ajtLogs("DNS : ERREUR : Il manque un paramètre pour effectuer cette action (supprEntree())")
				problem += 1
		elif nomTable == "DNSExt":
			cursor.execute("""DELETE FROM DNSExt WHERE IPPORT = ?""", (entree,))
		else:
			logs.ajtLogs("DNS : ERREUR : Nom de la table non reconnu (supprEntree()) : " + str(nomTable))
			problem += 1
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("DNS : ERREUR : Problème avec base de données (supprEntree()):" + str(e))
		problem += 1
	else:
		logs.ajtLogs("DNS : INFO : L'entrée' " + entree + " de la table " + nomTable + " a bien été supprimé.")
	conn.close()
	return problem

def modifEntree(nomTable, entree, entree1 = "", entree2 = ""):
	# Fonction qui permet de supprimer une entrée dans une table
	# Paramètres : Le nom de la table; le nouveau SHA256; le nom de domaine; le mot de passe non hashé
	problem = 0
	verifExistBDD()
	conn = sqlite3.connect('WTPDNS.db')
	cursor = conn.cursor()
	try:
		if nomTable == "DNS":
			if entree1 != "" and entree2 != "":
				# On vérifie que le mot de passe hashé est égal à celui de la base de données,
				# et si c'est le cas on peut suprimer la ligne
				cursor.execute("""SELECT PASSWORD FROM DNS WHERE NDD = ?""", (entree1,))
				rows = cursor.fetchall()
				nbRes = 0
				for row in rows:
					if row[0] == hashlib.sha256(str(entree2).encode()).hexdigest():
						cursor.execute("""UPDATE DNS SET SHA256 = ? WHERE NDD = ?""", (entree, entree1))
					else:
						print("ERREUR : Le mot de passe n'est pas valide.")
						problem = 5
			else:
				logs.ajtLogs("DNS : ERREUR : Il manque un paramètre pour effectuer cette action (supprEntree())")
				problem += 1
		else:
			logs.ajtLogs("DNS : ERREUR : Nom de la table non reconnu (supprEntree()) : " + str(nomTable))
			problem += 1
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("DNS : ERREUR : Problème avec base de données (supprEntree()):" + str(e))
		problem += 1
	else:
		logs.ajtLogs("DNS : INFO : L'entrée' " + entree + " de la table " + nomTable + " a bien été supprimé.")
	conn.close()
	return problem

def verifExistBDD():
	# Fonction qui permet d'alèger le code en évitant les duplications
	try:
		with open('WTPDNS.db'):
			pass
	except IOError:
		logs.ajtLogs("DNS : ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
