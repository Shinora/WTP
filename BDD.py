#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import math
import time
import logs
import sqlite3
from Crypto import Random

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
			CREATE TABLE IF NOT EXISTS SuperNoeuds(
				id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
				IP TEXT,
				NbFichiers INTEGER,
				DerSync TEXT,
				DateAjout TEXT
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

def ajtNoeud(ipPort):
	# Fonction qui permet d'ajouter un noeud à la base de données
	# Paramètre : IP et port du nœud, de type 88.189.108.233:12345
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	# Vérifier si le noeud existe déjà dans la BDD.
	# Si il existe on ne fait rien
	# Si il n'existe pas, on l'ajoute
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT id FROM Noeuds WHERE IP = ?""", (ipPort,))
		rows = cursor.fetchall()
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (ajtNoeud()):" + str(e))
	nbRes = 0
	for row in rows:
		nbRes += 1
	if nbRes != 0:
		# Le noeud existe déjà
		if nbRes > 1:
			logs.ajtLogs("ERREUR : Noeud présent plusieurs fois dans la base. ajtNoeud --> BDD.py")
	else:
		# C'est bon, on va créer le noeud dans la liste
		# Nous avons l'Ip+Port (IP)
		# La date actuelle servira de DerSync et Date
		datetimeAct = str(time.time())
		datetimeAct = datetimeAct[:datetimeAct.find(".")]
		try:
			cursor.execute("""INSERT INTO Noeuds (IP, DerSync, DateAjout) VALUES (?, ?, ?)""", (ipPort, datetimeAct, datetimeAct))
			conn.commit()
		except Exception as e:
			conn.rollback()
			logs.ajtLogs("ERREUR : Problème avec base de données (ajtNoeud()):" + str(e))
	conn.close()

def envNoeuds(nbreNoeuds):
	# Fonction qui permet de lire un nombre de noeuds et de 
	# ... renvoyer une chaine de type 88.189.108.233:12345
	# Paramètre : Le nomnbre de noeuds à renvoyer
	listeNoeuds = ""
	try:
		with open('WTP.db'): pass
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

def ajtFichier(nomFichier):
	# Fonction qui permet d'ajouter un fichier à la base de données
	# Paramètre : nom du fichier de type SHA256.extension
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	# Vérifier si le fichier existe déjà dans la BDD.
	# Si il existe on ne fait rien
	# Si il n'existe pas, on l'ajoute
	try:
		cursor.execute("""SELECT id FROM Fichiers WHERE Nom = ?""", (nomFichier,))
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (ajtFichier()):" + str(e))
	rows = cursor.fetchall()
	nbRes = 0
	for row in rows:
		nbRes += 1
	if nbRes != 0:
		# Le fichier existe déjà
		if nbRes > 1:
			logs.ajtLogs("ERREUR : Fichier présent plusieurs fois dans la base. ajtFichier --> BDD.py")
	else:
		# C'est bon, on va créer le fichier dans la liste
		datetimeAct = str(time.time())
		datetimeAct = datetimeAct[:datetimeAct.find(".")]
		cheminFichier = "HOSTEDFILES/" + nomFichier
		try:
			cursor.execute("""INSERT INTO Fichiers (Nom, DateAjout, Taille, Chemin) VALUES (?, ?, ?, ?)""", (nomFichier, datetimeAct, os.path.getsize(cheminFichier), cheminFichier))
			conn.commit()
		except Exception as e:
			conn.rollback()
			logs.ajtLogs("ERREUR : Problème avec base de données (ajtFichier()):" + str(e))
	conn.close()

def ajtFichierExt(nomFichier, IpPort):
	# Fonction qui permet d'ajouter un fichier à la base de données
	# Paramètre : nom du fichier de type SHA256.extension
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	# Vérifier si le fichier existe déjà dans la BDD.
	# Si il existe on ne fait rien
	# Si il n'existe pas, on l'ajoute
	try:
		cursor.execute("""SELECT id FROM FichiersExt WHERE Nom = ? AND IP = ?""", (nomFichier, IpPort))
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (ajtFichierExt()):" + str(e))
	rows = cursor.fetchall()
	nbRes = 0
	for row in rows:
		nbRes += 1
	if nbRes != 0:
		# Le fichier existe déjà
		if nbRes > 1:
			logs.ajtLogs("ERREUR : Fichier présent plusieurs fois dans la base. ajtFichierExt --> BDD.py")
	else:
		# C'est bon, on va créer le fichier dans la liste
		datetimeAct = str(time.time())
		datetimeAct = datetimeAct[:datetimeAct.find(".")]
		cheminFichier = "HOSTEDFILES/" + nomFichier
		try:
			cursor.execute("""INSERT INTO FichiersExt (Nom, IP) VALUES (?, ?)""", (nomFichier, IpPort))
			conn.commit()
		except Exception as e:
			conn.rollback()
			logs.ajtLogs("ERREUR : Problème avec base de données (ajtFichierExt()):" + str(e))
	conn.close()

def supprNoeud(ipPort):
	# Vérifie que le noeud existe
	# Si il existe, le noeud est supprimé.
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	# Vérification de l'existance du noeud supprimée
	try:
		cursor.execute("""DELETE FROM Noeuds WHERE IP =  ?""", (ipPort,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (supprNoeud()):" + str(e))
	else:
		logs.ajtLogs("INFO : Le noeud " + ipPort + " a bien été supprimé de la base.")
	conn.close()

def supprFichier(nomFichier):
	# Vérifie que le fichier existe
	# Si il existe, le fichier est supprimé.
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()

	# On supprime le fichier du disque dur
	chemin = "HOSTEDFILES/" + nomFichier
	os.remove(chemin)
	try:
		cursor.execute("""DELETE FROM Fichiers WHERE Nom = ?""", (nomFichier,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (supprFichier()):" + str(e))
	logs.ajtLogs("INFO : Le fichier " + nomFichier + " a bien été supprimé")
	conn.close()

def supprFichierExt(nomFichier, IpPort):
	# Vérifie que le fichier existe
	# Si il existe, le fichier est supprimé.
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""DELETE FROM FichiersExt WHERE Nom = ? AND IP = ?""", (nomFichier, IpPort))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données (supprFichierExt()):" + str(e))
	logs.ajtLogs("INFO : Le fichier Externe " + nomFichier + " a bien été supprimé")
	conn.close()

def ajtNoeudHS(ipPort):
	# Vérifier si le noeud existe déjà dans la BDD.
	# Si il existe on ne fait rien
	# Si il n'existe pas, on l'ajoute
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT ID FROM NoeudsHorsCo WHERE IP = ?""", (ipPort,))
		rows = cursor.fetchall()
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (ajtNoeudHS()):" + str(e))
	nbRes = 0
	for row in rows:
		nbRes += 1
	if nbRes != 0:
		# Le noeud existe déjà
		if nbRes > 1:
			logs.ajtLogs("ERREUR : Noeud HS présent plusieurs fois dans la base. ajtNoeudHS --> BDD.py")
	else:
		# C'est bon, on va créer le noeud dans la liste
		# Nous avons l'Ip+Port (IP)
		try:
			cursor.execute("""INSERT INTO NoeudsHorsCo (IP, NbVerifs) VALUES (?, 0)""", (ipPort,))
			conn.commit()
		except Exception as e:
			conn.rollback()
			logs.ajtLogs("ERREUR : Problème avec base de données (ajtNoeudHS()):" + str(e))
	conn.close()

def supprNoeudHS(ipPort):
	# Vérifie que le noeud existe
	# Si il existe, le noeud est supprimé.
	try:
		with open('WTP.db'): pass
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
		logs.ajtLogs("ERREUR : Problème avec base de données (supprNoeudHS()):" + str(e))
	nbRes = 0
	for row in rows:
		nbRes += 1
	if nbRes != 0:
		# Le noeud existe, on peut le supprimer
		try:
			cursor.execute("""DELETE FROM NoeudsHorsCo WHERE IP =  ?""", (ipPort,))
			conn.commit()
		except Exception as e:
			conn.rollback()
			logs.ajtLogs("ERREUR : Problème avec base de données (supprNoeudHS()):" + str(e))
		logs.ajtLogs("INFO : Le noeud HS " + ipPort + " a bien été supprimé définitivement de la base.")
	else:
		# Le noeud n'existe pas, juste unwarning dans les logs.
		logs.ajtLogs("WARNING : Le noeud HS " + ipPort + " n'a pas pu etre supprimé car il n'existe plus.")
	conn.close()

def incrNbVerifsHS(ipPort):
	# Vérifie que le noeud existe
	# Si il existe, le noeud est incémenté de 1.
	try:
		with open('WTP.db'): pass
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
		with open('WTP.db'): pass
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
		with open('WTP.db'): pass
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
		with open('WTP.db'): pass
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
		with open('WTP.db'): pass
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
		with open('WTP.db'): pass
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
		with open('WTP.db'): pass
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