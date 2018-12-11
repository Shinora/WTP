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
				NbEnvois INTEGER,
				NbReceptions INTEGER
			)
		""")
		conn.commit()
		# On initialise les Statistiques
		cursor.execute("""INSERT INTO Statistiques (NbNoeuds, NbSN, NbFichiersExt, NbFichiers, PoidsFichiers, NbEnvois, NbReceptions) VALUES (0, 0, 0, 0, 0, 0, 0)""")
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (creerBase()) :" + str(e))
	conn.close()

def ajouterEntree(nomTable, entree, entree1 = ""):
	# Fonction qui permet d'ajouter une entrée à une table de la base
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	# Vérifier si l'entrée existe déjà dans la BDD.
	# Si il existe on ne fait rien
	# Si il n'existe pas, on l'ajoute
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if nomTable == "Noeuds":
			cursor.execute("""SELECT id FROM ? WHERE IP = ?""", (nomTable, entree))
		elif nomTable == "Fichiers":
			cursor.execute("""SELECT id FROM ? WHERE Nom = ?""", (nomTable, entree))
		elif nomTable == "FichiersExt":
			cursor.execute("""SELECT id FROM ? WHERE Nom = ? AND IP = ?""", (nomTable, entree, entree1))
		elif nomTable == "NoeudsHorsCo":
			cursor.execute("""SELECT id FROM ? WHERE IP = ?""", (nomTable, entree))
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (ajouterEntree()):" + str(e))
	else:
		nbRes = 0
		rows = cursor.fetchall()
		for row in rows:
			nbRes += 1
		if nbRes != 0:
			# L'entrée existe déjà
			if nbRes > 1:
				logs.ajtLogs("ERREUR : Entrée présente plusieurs fois dans la base. (ajouterEntree())")
		else:
			datetimeAct = str(time.time())
			datetimeAct = datetimeAct[:datetimeAct.find(".")]
			# En fonction de la table, il n'y a pas les mêmes champs à remplir
			try:
				if nomTable == "Noeuds":
					cursor.execute("""INSERT INTO ? (IP, DerSync, DateAjout) VALUES (?, ?, ?)""", (nomTable, entree, datetimeAct, datetimeAct))
				elif nomTable == "Fichiers":
					cheminFichier = "HOSTEDFILES/" + entree
					cursor.execute("""INSERT INTO ? (Nom, DateAjout, Taille, Chemin) VALUES (?, ?, ?, ?)""", (nomTable, entree, datetimeAct, os.path.getsize(cheminFichier), cheminFichier))
				elif nomTable == "FichiersExt":
					cursor.execute("""INSERT INTO ? (Nom, IP) VALUES (?, ?)""", (nomTable, entree, entree1))
				elif nomTable == "NoeudsHorsCo":
					cursor.execute("""INSERT INTO ? (IP, NbVerifs) VALUES (?, 0)""", (nomTable, entree))
				conn.commit()
			except Exception as e:
				conn.rollback()
				logs.ajtLogs("ERREUR : Problème avec base de données (ajouterEntree()):" + str(e))
	conn.close()

def envNoeuds(nbreNoeuds):
	# Fonction qui permet de lire un nombre de noeuds et de 
	# ... renvoyer une chaine de type 88.189.108.233:12345
	# Paramètre : Le nomnbre de noeuds à renvoyer
	listeNoeuds = ""
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	datetimeAct24H = str(time.time()-86400)
	datetime24H = datetimeAct24H[:datetimeAct24H.find(".")]
	try:
		cursor.execute("""SELECT IP FROM Noeuds WHERE DerSync > ? LIMIT ?""", (datetimeAct24H, nbreNoeuds))
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (envNoeuds()):" + str(e))
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
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if nomTable == "Noeuds":
			cursor.execute("""DELETE FROM ? WHERE IP =  ?""", (nomTable, entree))
		elif nomTable == "Fichiers":
			cursor.execute("""DELETE FROM ? WHERE Nom = ?""", (nomTable, entree))
		elif nomTable == "FichiersExt":
			cursor.execute("""DELETE FROM ? WHERE Nom = ? AND IP = ?""", (nomTable, entree, entree1))
		elif nomTable == "NoeudsHorsCo":
			cursor.execute("""DELETE FROM ? WHERE IP =  ?""", (nomTable, entree))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (supprEntree()):" + str(e))
	else:
		if nomTable == "Noeuds":
			logs.ajtLogs("INFO : Le noeud " + entree + " a bien été supprimé de la base.")
		elif nomTable == "Fichiers":
			chemin = "HOSTEDFILES/" + entree
			os.remove(chemin)
			logs.ajtLogs("INFO : Le fichier " + entree + " a bien été supprimé")
		elif nomTable == "FichiersExt":
			logs.ajtLogs("INFO : Le fichier Externe " + entree + " a bien été supprimé")
		elif nomTable == "NoeudsHorsCo":
			logs.ajtLogs("INFO : Le noeud HS " + entree + " a bien été supprimé définitivement de la base.")
	conn.close()

def incrNbVerifsHS(ipPort):
	# Vérifie que le noeud existe
	# Si il existe, le noeud est incémenté de 1.
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT ID FROM NoeudsHorsCo WHERE IP = ?""", (ipPort,))
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (incrNbVerifsHS()):" + str(e))
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
			logs.ajtLogs("ERREUR : Problème avec base de données (incrNbVerifsHS()):" + str(e))
		logs.ajtLogs("INFO : Le nombre de verifications de " + ipPort + " a bien été incrémenté de 1.")
	else:
		# Le noeud n'existe pas, juste un warning dans les logs.
		logs.ajtLogs("ERREUR : Le noeud HS " + ipPort + " n'a pas pu etre incrémenté car il n'existe plus.")
	conn.close()

def verifNbVerifsHS(ipPort):
	# Vérifie que le nombre de vérifications déjà effectuées
	# S'il y en a plus que 10, le noeud est définitivement supprimé
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT NbVerifs FROM NoeudsHorsCo WHERE IP = ?""", (ipPort,))
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (verifNbVerifsHS()):" + str(e))
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
			logs.ajtLogs("ERREUR : Problème avec base de données (verifNbVerifsHS()):" + str(e))
		logs.ajtLogs("INFO : Le noeud HS " + ipPort + " a bien été supprimé, il ne répond plus.")
	conn.close()

def verifFichier(nomFichier):
	# Fonction qui vérifie si le fichier existe dans la base de données
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT ID FROM Fichiers WHERE Nom = ?""", (nomFichier,))
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données dans verifFichier() : " + str(e))
	FichierExiste = False
	for row in rows:
		FichierExiste = True
	conn.close()
	return FichierExiste

def majStatsTaillFchsTtl(varAMaj):
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""UPDATE Statistiques SET PoidsFichiers = ? WHERE 1""", (varAMaj,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (majStatsTaillFchsTtl()):" + str(e))
	conn.close()

def majStatsNbFchs(varAMaj):
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""UPDATE Statistiques SET NbFichiers = ? WHERE 1""", (varAMaj,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (majStatsNbFchs()):" + str(e))
	conn.close()

def majStatsNbFchsExt(varAMaj):
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""UPDATE Statistiques SET NbFichiersExt = ? WHERE 1""", (varAMaj,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (majStatsNbFchsExt()):" + str(e))
	conn.close()

def majStatsNbNoeuds(varAMaj):
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""UPDATE Statistiques SET NbNoeuds = ? WHERE 1""", (varAMaj,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (majStatsNbNoeuds()):" + str(e))
	conn.close()

def searchFileBDD(nomFichier):
	# Fonction qui a pour but de chercher dans la Base de données le noeud qui possède le fichier recherché
	# Elle retourne l'IP du noeud qui a le fichier, sinon elle retourne une chaine vide
	IPPortNoeud = "" # L'adresse du noeud sera ici
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	# On va chercher dans les fichiers hébergés
	try:
		cursor.execute("""SELECT id FROM Fichiers WHERE Nom = ?""", (nomFichier,))
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (searchFile()):" + str(e))
	rows = cursor.fetchall()
	for row in rows:
		# Le fichier est hébergé par le noeud qui le cherche
		IPPortNoeud = "127.0.0.1"
	if IPPortNoeud != "127.0.0.1":
		# Si le fichier n'a pas été trouvé
		# Il faut chercher dans les fichiers connus externes
		try:
			cursor.execute("""SELECT IP FROM FichiersExt WHERE Nom = ?""", (nomFichier,))
		except Exception as e:
			logs.ajtLogs("ERREUR : Problème avec base de données (searchFile()):" + str(e))
		rows = cursor.fetchall()
		for row in rows:
			# Le fichier est hébergé par un noeud connu
			IPPortNoeud = str(row)
	return IPPortNoeud

def nbEntrees(nomTable):
	# Fonction qui a pour seul but de compter toutes les entrées de la table
	# Dont le nom a été passé en paramètres
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT COUNT(*) FROM ?""", (nomTable,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (nbEntrees()):" + str(e))
	for row in cursor.fetchall():
		conn.close()
		return row

def aleatoire(nomTable, entree, nbEntrees):
	# Fonction qui a pour but de renvoyer sour forme d'un tableau nbEntrees lignes
	# contenues dans nomTable de façon aléatoire.
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT ? FROM ? ORDER BY RANDOM() LIMIT ?""", (entree, nomTable, nbEntrees))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (aleatoire()):" + str(e))
	rows = cursor.fetchall()
	tableau = []
	for row in rows:
		tableau.append(row)
		# On remplit le tableau avant de le retourner
	conn.close()
	return tableau

def chercherInfo(nomTable, info, retour):
	# Fonction qui retourne une information demandée dans la table demandée dans une entrée demandé
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT ? FROM ? WHERE ?""", (retour, nomTable, info))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (chercherInfo()):" + str(e))
	for row in cursor.fetchall():
		conn.close()
		return row
