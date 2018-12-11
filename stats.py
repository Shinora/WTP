#! /usr/bin/python
# -*- coding:utf-8 -*-

import logs
import BDD
import sqlite3

def comptTaillFchsTtl():
	# Fonction qui compte la taille totale de tous les fichiers hébergés sur le noeud,
	# Puis qui met à jour la base de données avec la fonction adéquate
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT Taille FROM Fichiers WHERE 1""")
		rows = cursor.fetchall()
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (comptTaillFchsTtl()):" + str(e))
	tailleTotale = 0
	for row in rows:
		tailleTotale += row[0]
	# On met à jour directement dans la BDD
	BDD.majStatsTaillFchsTtl(tailleTotale)

def comptNbFichiers():
	# Fonction qui compte le nombre total de fichiers hébergés par le noeud,
	# Puis qui met à jour la base de données avec la fonction adéquate
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT id FROM Fichiers WHERE 1""")
		rows = cursor.fetchall()
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (comptNbFichiers()):" + str(e))
	nbTotal = 0
	for row in rows:
		nbTotal += 1
	# On met à jour directement dans la BDD
	BDD.majStatsNbFchs(nbTotal)

def comptNbFichiersExt():
	# Fonction qui compte le nombre total de fichiers connus par le noeud,
	# Puis qui met à jour la base de données avec la fonction adéquate
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT id FROM FichiersExt WHERE 1""")
		rows = cursor.fetchall()
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (comptNbFichiersExt()):" + str(e))
	nbTotal = 0
	for row in rows:
		nbTotal += 1
	# On met à jour directement dans la BDD
	BDD.majStatsNbFchsExt(nbTotal)

def comptNbNoeuds():
	# Fonction qui compte le nombre total de neouds connus par le noeud,
	# Puis qui met à jour la base de données avec la fonction adéquate
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT id FROM Noeuds WHERE 1""")
		rows = cursor.fetchall()
	except Exception as e:
		logs.ajtLogs("ERREUR : Problème avec base de données (comptNbNoeuds()):" + str(e))
	nbTotal = 0
	for row in rows:
		nbTotal += 1
	# On met à jour directement dans la BDD
	BDD.majStatsNbNoeuds(nbTotal)
