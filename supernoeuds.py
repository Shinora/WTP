#! /usr/bin/python
# -*- coding:utf-8 -*-

import logs
import clientCMD
import BDD

# Ici sont regroupées toutes les fonctions liées uniquement aux super-noeuds

def parseAll():
	# Fonction qui permet de connaitre l'intégralité du réseau
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT IP FROM Noeuds WHERE 1""")
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.ajtLogs("ERREUR : Problème avec base de données dans parseAll() : " + str(e))
	for row in rows:
		hote = row[:row.find(":")]
		port = row[row.find(":")+1:]
		# Pour chaque noeud on demande la liste de :
		# tous les fichiers qu'il héberge (=cmd DemandeListeFichiers)
		clientCMD.CmdDemandeListeFichiers(hote, port)
		# tous les fichiers externes qu'il connait (=cmd DemandeListeFichiersExt)
		clientCMD.CmdDemandeListeFichiers(hote, port, 1)
		# tous les noeuds qu'il connait (=cmd DemandeListeNoeuds)
		clientCMD.CmdDemandeListeNoeuds(hote, port)
	conn.close()
