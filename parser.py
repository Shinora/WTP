#! /usr/bin/python
# -*- coding:utf-8 -*-

import logs
import fctsClient
import BDD
import re

# Fonctionnalité qui permet de connaitre l'intégralité du réseau

fExtW = open(".extinctionWTP", "w")
fExtW.write("ALLUMER")
fExtW.close()

allume = True
while allume:
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT IP FROM Noeuds WHERE 1""")
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.addLogs("ERREUR : Problem with database (parseAll()) : " + str(e))
	for row in rows:
		reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
		if reg.match(row): # Si row est un ip:port
			host = row[:row.find(":")]
			port = row[row.find(":")+1:]
			# Pour chaque noeud on demande la liste de :
			# tous les files qu'il héberge (=cmd DemandeListeFichiers)
			fctsClient.CmdDemandeListeFichiers(host, port)
			# tous les files externes qu'il connait (=cmd DemandeListeFichiersExt)
			fctsClient.CmdDemandeListeFichiers(host, port, 1)
			# tous les noeuds qu'il connait (=cmd DemandeListeNoeuds)
			fctsClient.CmdDemandeListeNoeuds(host, port)
	conn.close()
	# Vérifier si WTP a recu une demande d'extinction
	fExt = open(".extinctionWTP", "r")
	contenu = fExt.read()
	fExt.close()
	if contenu == "ETEINDRE":
		# On doit éteindre WTP.
		allume = False
	elif contenu != "ALLUMER":
		fExtW = open(".extinctionWTP", "w")
		fExtW.write("ALLUMER")
		fExtW.close()
