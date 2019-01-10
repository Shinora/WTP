#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import math
import time
import logs
import sqlite3

def creerBase():
	# Fonction qui a pour seul but de créer la base de données
	# si le fichier la contenant n'existe pas.
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS NoeudsHorsCo(
				id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
				IP TEXT,
				NbVerifs INTEGER
			)
		""")
		conn.commit()
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS Fichiers(
				id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
				Nom TEXT,
				DateAjout TEXT,
				Taille INTEGER,
				Chemin TEXT
			)
		""")
		conn.commit()
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS Noeuds(
				id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
				IP TEXT,
				Fonction TEXT default simple,
				DerSync TEXT,
				DateAjout TEXT
			)
		""")
		conn.commit()
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS FichiersExt(
				id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
				Nom TEXT,
				IP TEXT
			)
		""")
		conn.commit()
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS Statistiques(
				NbNoeuds INTEGER,
				NbSN INTEGER,
				NbFichiersExt INTEGER,
				NbFichiers INTEGER,
				PoidsFichiers INTEGER,
				NbEnvsLstNoeuds INTEGER,
				NbEnvsLstFichiers INTEGER,
				NbEnvsLstFichiersExt INTEGER,
				NbEnvsFichiers INTEGER,
				NbPresence INTEGER,
				NbReceptFichiers INTEGER
			)
		""")
		conn.commit()
		# On initialise les Statistiques
		cursor.execute("""INSERT INTO Statistiques (NbNoeuds, NbSN, NbFichiersExt, NbFichiers, PoidsFichiers, NbEnvsLstNoeuds, NbEnvsLstFichiers, NbEnvsLstFichiersExt, NbEnvsFichiers, NbPresence, NbReceptFichiers) VALUES (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)""")
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database (creerBase()) :" + str(e))
	conn.close()
	ajouterEntree("Noeuds", "127.0.0.1:5557", "DNS")
	ajouterEntree("FichiersExt", "BBDEFA2950F49882F295B1285D4FA9DEC45FC4144BFB07EE6ACC68762D12C2E3", "127.0.0.1:5555")

def ajouterEntree(nomTable, entree, entree1 = ""):
	# Fonction qui permet d'ajouter une entrée à une table de la base
	verifExistBDD()
	# Vérifier si l'entrée existe déjà dans la BDD.
	# Si il existe on ne fait rien
	# Si il n'existe pas, on l'ajoute
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if nomTable == "Noeuds":
			cursor.execute("""SELECT id FROM Noeuds WHERE IP = ?""", (entree,))
		elif nomTable == "Fichiers":
			cursor.execute("""SELECT id FROM Fichiers WHERE Nom = ?""", (entree,))
		elif nomTable == "FichiersExt":
			cursor.execute("""SELECT id FROM FichiersExt WHERE Nom = ? AND IP = ?""", (entree, entree1))
		elif nomTable == "NoeudsHorsCo":
			cursor.execute("""SELECT id FROM NoeudsHorsCo WHERE IP = ?""", (entree,))
	except Exception as e:
		logs.ajtLogs("ERROR : Problem with database (ajouterEntree()):" + str(e))
	else:
		nbRes = 0
		rows = cursor.fetchall()
		for row in rows:
			nbRes += 1
		if nbRes != 0:
			# L'entrée existe déjà
			if nbRes > 1:
				logs.ajtLogs("ERROR : Entry presents several times in the database. (ajouterEntree())")
		else:
			datetimeAct = str(time.time())
			datetimeAct = datetimeAct[:datetimeAct.find(".")]
			# En fonction de la table, il n'y a pas les mêmes champs à remplir
			try:
				if nomTable == "Noeuds":
					if entree1 == "":
						entree1 = "Simple"
					cursor.execute("""INSERT INTO Noeuds (IP, Fonction, DerSync, DateAjout) VALUES (?, ?, ?, ?)""", (entree, entree1, datetimeAct, datetimeAct))
				elif nomTable == "Fichiers":
					cheminFichier = "HOSTEDFILES/" + entree
					cursor.execute("""INSERT INTO Fichiers (Nom, DateAjout, Taille, Chemin) VALUES (?, ?, ?, ?)""", (entree, datetimeAct, os.path.getsize(cheminFichier), cheminFichier))
				elif nomTable == "FichiersExt":
					cursor.execute("""INSERT INTO FichiersExt (Nom, IP) VALUES (?, ?)""", (entree, entree1))
				elif nomTable == "NoeudsHorsCo":
					cursor.execute("""INSERT INTO NoeudsHorsCo (IP, NbVerifs) VALUES (?, 0)""", (entree,))
				conn.commit()
			except Exception as e:
				conn.rollback()
				logs.ajtLogs("ERROR : Problem with database (ajouterEntree()):" + str(e))
	conn.close()

def envNoeuds(nbreNoeuds):
	# Fonction qui permet de lire un nombre de noeuds et de 
	# ... renvoyer une chaine de type 88.189.108.233:12345
	# Paramètre : Le nomnbre de noeuds à renvoyer
	listeNoeuds = ""
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	datetimeAct24H = str(time.time()-86400)
	datetime24H = datetimeAct24H[:datetimeAct24H.find(".")]
	try:
		cursor.execute("""SELECT IP FROM Noeuds WHERE DerSync > ? LIMIT ?""", (datetimeAct24H, nbreNoeuds))
	except Exception as e:
		logs.ajtLogs("ERROR : Problem with database (envNoeuds()):" + str(e))
	rows = cursor.fetchall()
	nbRes = 0
	for row in rows:
		if nbRes == 0:
			listeNoeuds += row[0]
		else:
			listeNoeuds += "," + row[0]
			nbRes += 1
	conn.close()
	return listeNoeuds

def supprEntree(nomTable, entree, entree1 = ""):
	# Fonction qui permet de supprimer une entrée dans une table
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if nomTable == "Noeuds":
			cursor.execute("""DELETE FROM Noeuds WHERE IP =  ?""", (entree,))
		elif nomTable == "Fichiers":
			cursor.execute("""DELETE FROM Fichiers WHERE Nom = ?""", (entree,))
		elif nomTable == "FichiersExt":
			cursor.execute("""DELETE FROM FichiersExt WHERE Nom = ? AND IP = ?""", (entree, entree1))
		elif nomTable == "NoeudsHorsCo":
			cursor.execute("""DELETE FROM NoeudsHorsCo WHERE IP =  ?""", (entree,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database (supprEntree()):" + str(e))
	else:
		if nomTable == "Noeuds":
			logs.ajtLogs("INFO : The peer " + entree + " has been removed from the database.")
		elif nomTable == "Fichiers":
			chemin = "HOSTEDFILES/" + entree
			os.remove(chemin)
			logs.ajtLogs("INFO : The file " + entree + " has been removed.")
		elif nomTable == "FichiersExt":
			logs.ajtLogs("INFO : The External file " + entree + " has been removed.")
		elif nomTable == "NoeudsHorsCo":
			logs.ajtLogs("INFO : The peer off " + entree + " has been permanently deleted from the database.")
	conn.close()

def incrNbVerifsHS(ipPort):
	# Vérifie que le noeud existe
	# Si il existe, le noeud est incémenté de 1.
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT ID FROM NoeudsHorsCo WHERE IP = ?""", (ipPort,))
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database (incrNbVerifsHS()):" + str(e))
	nbRes = 0
	for row in rows:
		nbRes += 1
	if nbRes != 0:
		# Le noeud existe, on peut l'incrémenter
		try:
			cursor.execute("""UPDATE NoeudsHorsCo SET NbVerifs = NbVerifs + 1 WHERE IP = ?""", (ipPort,))
			conn.commit()
		except Exception as e:
			conn.rollback()
			logs.ajtLogs("ERROR : Problem with database (incrNbVerifsHS()):" + str(e))
		logs.ajtLogs("INFO : The number of verifications of "+ ipPort +" has been incremented by 1.")
	else:
		# Le noeud n'existe pas, juste un warning dans les logs.
		logs.ajtLogs("ERREUR : The peer off "+ ipPort +" could not be incremented because it no longer exists.")
	conn.close()

def verifNbVerifsHS(ipPort):
	# Vérifie que le nombre de vérifications déjà effectuées
	# S'il y en a plus que 10, le noeud est définitivement supprimé
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT NbVerifs FROM NoeudsHorsCo WHERE IP = ?""", (ipPort,))
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database(verifNbVerifsHS()):" + str(e))
	nbRes = 0
	for row in rows:
		nbRes = row[0]
	if nbRes > 10:
		# Le noeud doit être supprimé
		try:
			cursor.execute("""DELETE FROM NoeudsHorsCo WHERE IP =  ?""", (ipPort,))
			conn.commit()
		except Exception as e:
			conn.rollback()
			logs.ajtLogs("ERROR : Problem with database (verifNbVerifsHS()):" + str(e))
		logs.ajtLogs("INFO : The peer off "+ ipPort +" has been removed, it no longer responds.")
	conn.close()

def verifFichier(nomFichier):
	# Fonction qui vérifie si le fichier existe dans la base de données
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT ID FROM Fichiers WHERE Nom = ?""", (nomFichier,))
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database (verifFichier()) : " + str(e))
	FichierExiste = False
	for row in rows:
		FichierExiste = True
	conn.close()
	return FichierExiste

def modifStats(colonne, valeur=-1):
	# Si valeur = -1, on incrémente, sinon on assigne la valeur en paramètres
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if valeur == -1:
			colonne2 = colonne
			cursor.execute("""UPDATE Statistiques SET ? = 1 WHERE 1""", (colonne, colonne2))
		else:
			cursor.execute("""UPDATE Statistiques SET ? = ? WHERE 1""", (colonne, int(valeur)))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database (modifStats()):" + str(e))
		logs.ajtLogs(str(valeur) + colonne)
	conn.close()

def compterStats(colonne):
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT ? FROM Statistiques WHERE 1""", (colonne,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database (compterStats()):" + str(e))
	conn.close()

def searchFileBDD(nomFichier):
	# Fonction qui a pour but de chercher dans la Base de données le noeud qui possède le fichier recherché
	# Elle retourne l'IP du noeud qui a le fichier, sinon elle retourne une chaine vide
	IPPortNoeud = "" # L'adresse du noeud sera ici
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	# On va chercher dans les fichiers hébergés
	try:
		cursor.execute("""SELECT id FROM Fichiers WHERE Nom = ?""", (nomFichier,))
	except Exception as e:
		logs.ajtLogs("ERROR : Problem with database (searchFile()):" + str(e))
	rows = cursor.fetchall()
	for row in rows:
		# Le fichier est hébergé par le noeud qui le cherche
		ipPortIci = "127.0.0.1:"+str(autresFonctions.readConfFile("Port par defaut"))
		IPPortNoeud = ipPortIci
	if IPPortNoeud != ipPortIci:
		# Si le fichier n'a pas été trouvé
		# Il faut chercher dans les fichiers connus externes
		try:
			cursor.execute("""SELECT IP FROM FichiersExt WHERE Nom = ?""", (nomFichier,))
		except Exception as e:
			logs.ajtLogs("ERROR : Problem with database (searchFile()):" + str(e))
		rows = cursor.fetchall()
		for row in rows:
			# Le fichier est hébergé par un noeud connu
			IPPortNoeud = str(row)
	return IPPortNoeud

def nbEntrees(nomTable):
	# Fonction qui a pour seul but de compter toutes les entrées de la table
	# Dont le nom a été passé en paramètres
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT COUNT(*) FROM ?""", (nomTable,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database (nbEntrees()):" + str(e))
	for row in cursor.fetchall():
		conn.close()
		return row

def aleatoire(nomTable, entree, nbEntrees):
	# Fonction qui a pour but de renvoyer sour forme d'un tableau nbEntrees lignes
	# contenues dans nomTable de façon aléatoire.
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if nomTable == "Noeuds":
			cursor.execute("""SELECT IP FROM Noeuds ORDER BY RANDOM() LIMIT ?""", (nbEntrees,))
			conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database (aleatoire()):" + str(e))
	rows = cursor.fetchall()
	tableau = []
	for row in rows:
		tableau.append(row)
		# On remplit le tableau avant de le retourner
	conn.close()
	return tableau

def chercherInfo(nomTable, info):
	# Fonction qui retourne une information demandée dans la table demandée dans une entrée demandé
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if nomTable == "Noeuds":
			cursor.execute("""SELECT Fonction FROM Noeuds WHERE IP = ?""", (info,))
		elif nomTable == "Fichiers":
			cursor.execute("""SELECT id FROM Fichiers WHERE Nom = ?""", (info,))
		elif nomTable == "FichiersExt":
			cursor.execute("""SELECT IP FROM FichiersExt WHERE Nom = ?""", (info,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database (chercherInfo()):" + str(e))
	for row in cursor.fetchall():
		conn.close()
		return row[0]

def verifExistBDD():
	# Fonction qui permet d'alèger le code en évitant les duplications
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERROR : Base not found ... Creating a new base.")
		creerBase()

def searchNoeud(role, nbre = 10):
	# Fonction qui  pour but de chercher 'nbre' noeuds ayant pour role 'role'
	verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT IP FROM Noeuds WHERE Fonction = ? ORDER BY RANDOM() LIMIT ?""", (role, nbre))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERROR : Problem with database (aleatoire()):" + str(e))
	rows = cursor.fetchall()
	tableau = []
	for row in rows:
		tableau.append(row)
		# On remplit le tableau avant de le retourner
	conn.close()
	return tableau
