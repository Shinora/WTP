#!/usr/bin/python
# -*-coding:Utf-8 -*

import logs
import time
import sqlite3

def tableToFile(nomTable):
	# cette fonction a pour but de lire une table et de l'écrire dans un fichier
	error = 0
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if nomTable == "Noeuds":
			cursor.execute("SELECT IP FROM Noeuds WHERE 1")
			conn.commit()
		elif nomTable == "Fichiers":
			cursor.execute("SELECT Nom FROM Fichiers WHERE 1")
			conn.commit()
		elif nomTable == "FichiersExt":
			cursor.execute("SELECT Nom FROM FichiersExt WHERE 1")
			conn.commit()
		elif nomTable == "DNS":
			cursor.execute("SELECT SHA256, NDD, PASSWORD FROM DNS WHERE 1")
			conn.commit()
		else:
			logs.addLogs("ERROR: The table name was not recognized (tableToFile()) : " + str(nomTable))
			problem += 1
	except Exception as e:
		conn.rollback()
		logs.addLogs("ERROR : Problem with database (aleatoire()):" + str(e))
		error += 1
	rows = cursor.fetchall()
	conn.close()
	fileName = "TEMP"+str(time.time())
	if error != 0:
		return error
	f = open("HOSTEDFILES/"+fileName, "a")
	for row in rows:
		if nomTable != "DNS":
			f.write(str(row[0])+"\n")
		else:
			f.write(str(row[0]) + "," + str(row[1]) + ", " + str(row[2]) + "\n")
			# La virgule sans espace en premier est normal
	f.close()
	return fileName

def filetoTable(fileName, nomTable):
	# cette fonction a pour but de lire un fichier et de l'écrire dans une table
	f = open("HOSTEDFILES/"+fileName, "rb")
	lines = f.readlines()
	f.close()
	for line in lines:
		if nomTable == "Noeuds":
			BDD.ajouterEntree("Noeud", line)
		elif nomTable[:8] == "Fichiers":
			BDD.ajouterEntree("FichierExt", line)
		elif nomTable == "DNS":
			# La virgule sans espace en premier est normal
			SHA256 = line[:line.find(",")]
			NDD = line[line.find(",")+1:line.find(", ")]
			PASS = line[line.find(", ")+2:-1]
			BDD.ajouterEntree("DNS", NDD, SHA256, PASS)
		else:
			logs.addLogs("ERROR: The table name was not recognized (filetoTable()) : " + str(nomTable))
			problem += 1
