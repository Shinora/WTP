#! /usr/bin/python
# -*- coding:utf-8 -*-

import logs
import sys
import os
import math
import time
import re
import hashlib
import sqlite3
import autresFonctions
from Crypto import Random
from Crypto.Cipher import AES

def addNDD(ipport, sha, ndd, password):
	error = 0
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(ipport): # Si ipport est un ip:port
		ip = ipport[:ipport.find(":")]
		port = ipport[ipport.find(":")+1:]
		connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
		cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			logs.ajtLogs("Connection established with the DNS on the port {}".format(port))
			# =cmd DNS AddDNS sha ******* ndd ******* pass *******
			commande = "=cmd DNS AddDNS sha " + str(sha) + " ndd " + str(ndd) + " pass " + str(password)
			commande = commande.encode()
			connexion_avec_serveur.send(commande)
			message = connexion_avec_serveur.recv(1024)
			connexion_avec_serveur.close()
			if message == "=cmd NDDDejaUtilise":
				error = 5
				print("The domain name is already used. If it belongs to you, you can modify it provided you know the password.")
			elif message == "=cmd SUCCESS":
				print("The domain name and address SHA256 have been associated.")
			else:
				print("An undetermined error occurred. Please try again later or change DNS peer.")
				error = 1
	else:
		error += 1
	return error

def addNoeudDNS(ipport, ipportNoeud):
	errror = 0
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(ipport): # Si ipport est un ip:port
		ip = ipport[:ipport.find(":")]
		port = ipport[ipport.find(":")+1:]
		connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
		cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			logs.ajtLogs("Connection established with the DNS on the port {}".format(port))
			# =cmd DNS AddDNSExt ipport ******
			commande = "=cmd DNS AddDNSExt ipport " + ipportNoeud
			commande = commande.encode()
			connexion_avec_serveur.send(commande)
			message = connexion_avec_serveur.recv(1024)
			connexion_avec_serveur.close()
			if message == "=cmd IPPORTDejaUtilise":
				error = 5
				print("The peer DNS is already known by the receiver.")
			elif message == "=cmd SUCCESS":
				print("The DNS pair has been added to the receiver base.")
			else:
				print("An undetermined error occurred. Please try again later or change DNS peer.")
				error = 1
	else:
		error += 1
	return error

def modifNDD(ipport, ndd, adress, password):
	error = 0
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(ipport): # Si ipport est un ip:port
		ip = ipport[:ipport.find(":")]
		port = ipport[ipport.find(":")+1:]
		connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
		cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			logs.ajtLogs("Connection established with the DNS on the port {}".format(port))
			# =cmd DNS modifNDD ndd ****** adress ****** pass ******
			commande = "=cmd DNS modifNDD ndd " + str(ndd) + " adress " + str(adress) + " pass " + str(password)
			commande = commande.encode()
			connexion_avec_serveur.send(commande)
			message = connexion_avec_serveur.recv(1024)
			connexion_avec_serveur.close()
			error = 0
			if message == "=cmd IPPORTDejaUtilise":
				error = 5
				print("Le noeud DNS est déjà connu par le receveur.")
			elif message == "=cmd SUCCESS":
				print("Le noeud DNS a bien été ajouté à la base du receveur.")
			else:
				print("An undetermined error occurred. Please try again later or change DNS peer.")
				error += 1
	else:
		error += 1
	return error

def supprNDD(ipport, ndd, password):
	error = 0
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(ipport): # Si ipport est un ip:port
		ip = ipport[:ipport.find(":")]
		port = ipport[ipport.find(":")+1:]
		connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
		cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			logs.ajtLogs("Connection established with the DNS on the port {}".format(port))
			# =cmd DNS supprNDD ndd ****** pass ******
			commande = "=cmd DNS supprNDD ndd " + str(ndd) + " pass " + str(password)
			commande = commande.encode()
			connexion_avec_serveur.send(commande)
			message = connexion_avec_serveur.recv(1024)
			if message != "=cmd SUCCESS":
				error += 1
			connexion_avec_serveur.close()
	else:
		error += 1
	return error


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
		logs.ajtLogs("DNS : ERROR : Problem with the database (creerBase()) :" + str(e))
	conn.close()

def ajouterEntree(nomTable, entree, entree1 = "", entree2 = ""):
	# Fonction qui permet d'ajouter une entrée à une table de la base
	verifExistBDD()
	# Vérifier si l'entrée existe déjà dans la BDD.
	# Si il existe on ne fait rien
	# Si il n'existe pas, on l'ajoute
	conn = sqlite3.connect('WTPDNS.db')
	cursor = conn.cursor()
	problem = 0
	try:
		if nomTable == "DNS":
			cursor.execute("""SELECT id FROM DNS WHERE NDD = ?""", (entree,))
		elif nomTable == "DNSExt":
			cursor.execute("""SELECT id FROM DNSExt WHERE IPPORT = ?""", (entree,))
		else:
			logs.ajtLogs("DNS : ERROR: The table name was not recognized (ajouterEntree()) : " + str(nomTable))
			problem += 1
	except Exception as e:
		logs.ajtLogs("DNS : ERROR : Problem with the database (ajouterEntree()):" + str(e))
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
				logs.ajtLogs("DNS : ERROR: Entry is multiple times in the database. (ajouterEntree())")
				problem = 7
		else:
			datetimeAct = str(time.time())
			datetimeAct = datetimeAct[:datetimeAct.find(".")]
			# En fonction de la table, il n'y a pas les mêmes champs à remplir
			try:
				if nomTable == "DNS":
					if entree1 != "" and entree2 != "":
						passwordHash = hashlib.sha256(str(entree2).encode()).hexdigest()
						try:
							cursor.execute("""INSERT INTO DNS (SHA256, NDD, PASSWORD, DateAjout) VALUES (?, ?, ?, ?)""", (entree1, entree, passwordHash, datetimeAct))
							conn.commit()
						except Exception as e:
							logs.ajtLogs("DNS : ERREUR :" + str(e))
					else:
						logs.ajtLogs("DNS : ERROR: Parameters missing when calling the function (ajouterEntree())")
						problem += 1
				elif nomTable == "DNSExt":
					cursor.execute("""INSERT INTO DNSExt (IPPORT, DateAjout) VALUES (?, ?)""", (entree, datetimeAct))
					conn.commit()
			except Exception as e:
				conn.rollback()
				logs.ajtLogs("DNS : ERROR : Problem with the database (ajouterEntree()):" + str(e))
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
			logs.ajtLogs("DNS : ERROR: The table name was not recognized (envLste()) : " + str(nomTable))
	except Exception as e:
		logs.ajtLogs("DNS : ERROR : Problem with the database (envLste()):" + str(e))
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
						conn.commit()
					else:
						# Le mot de passe n'est pas valide
						problem = 5
			else:
				logs.ajtLogs("DNS : ERROR: There is a missing parameter to perform this action (supprEntree())")
				problem += 1
		elif nomTable == "DNSExt":
			cursor.execute("""DELETE FROM DNSExt WHERE IPPORT = ?""", (entree,))
			conn.commit()
		else:
			logs.ajtLogs("DNS : ERROR: The table name was not recognized (supprEntree()) : " + str(nomTable))
			problem += 1
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("DNS : ERROR : Problem with the database (supprEntree()):" + str(e))
		problem += 1
	else:
		if problem == 0:
			logs.ajtLogs("DNS : INFO : The " + entree + " entry of the " + nomTable + " table has been removed.")
		else:
			logs.ajtLogs("DNS : ERROR : The " + entree + " entry of the " + nomTable + " table could not be deleted")
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
					nbRes += 1
					if row[0] == hashlib.sha256(str(entree2).encode()).hexdigest():
						cursor.execute("""UPDATE DNS SET SHA256 = ? WHERE NDD = ?""", (entree, entree1))
						conn.commit()
					else:
						# Le mot de passe n'est pas valide.
						problem = 5
				if nbRes == 0:
					logs.ajtLogs("DNS : ERROR: The domain name to modify does not exist (modifEntree())")
					problem = 8
					problem += ajouterEntree("DNS", entree1, entree, entree2)
			else:
				logs.ajtLogs("DNS : ERROR: There is a missing parameter to perform this action (modifEntree())")
				problem += 1
		else:
			logs.ajtLogs("DNS : ERROR: The table name was not recognized (modifEntree()) : " + str(nomTable))
			problem += 1
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("DNS : ERROR : Problem with the database (modifEntree()):" + str(e))
		problem += 1
	else:
		logs.ajtLogs("DNS : INFO : The domain name "+ entree1 +" has been modified.")
	conn.close()
	return problem

def verifExistBDD():
	# Fonction qui permet d'alèger le code en évitant les duplications
	try:
		with open('WTPDNS.db'):
			pass
	except IOError:
		logs.ajtLogs("DNS : ERROR: Base not found ... Creating a new database.")
		creerBase()

def searchSHA(ndd):
	# Fonction qui a pour but de chercher le sha256 correspondant
	# au nom de domaine passé en paramètres s'il existe
	verifExistBDD()
	problem = 0
	sha256 = "0"
	conn = sqlite3.connect('WTPDNS.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT SHA256 FROM DNS WHERE NDD = ?""", (ndd,))
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("DNS : ERROR : Problem with the database (searchSHA()):" + str(e))
		problem += 1
	else:
		nbRes = 0
		for row in rows:
			nbRes += 1
			if nbRes > 1:
				# On trouve plusieurs fois le même nom de domaine dans la base
				problem = 5
				logs.ajtLogs("DNS : ERROR: The domain name "+ ndd +" is present several times in the database")
			sha256 = row[0]
	conn.close()
	if problem > 1:
		return problem
	if sha256 == "0":
		return "INCONNU"
	return sha256

def majDNS():
	# Fonction pour noeud DNS qui permet de mettre à jour toute sa base avec un autre noeud
	verifExistBDD()
	problem = 0
	conn = sqlite3.connect('WTPDNS.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT IPPORT FROM DNSExt ORDER BY RANDOM() LIMIT 1""")
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("DNS : ERROR : Problem with the database (majDNS()):" + str(e))
		problem += 1
	else:
		for row in rows:
			ipport = row[0]
		# Maintenant on va demander au noeud DNS distant d'envoyer toutes ses entrées DNS pour
		# Que l'on puisse ensuite analyser, et ajouter/mettre à jour notre base
	conn.close()
	if problem > 1:
		return problem
	if sha256 == "0":
		return "INCONNU"
	return sha256