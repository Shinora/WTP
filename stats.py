import logs
import BDD
import sqlite3

def comptTaillFchsTtl():
	# Fonction qui compte la taille totale de tous les files hébergés sur le noeud,
	# Puis qui met à jour la base de données avec la fonction adéquate
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT Taille FROM Fichiers WHERE 1""")
		rows = cursor.fetchall()
	except Exception as e:
		logs.addLogs("ERROR : Problem with the database (comptTaillFchsTtl()):" + str(e))
	tailleTotale = 0
	for row in rows:
		tailleTotale += row[0]
	# On met à jour directement dans la BDD
	modifStats("PoidsFichiers", tailleTotale)

def comptNbFichiers():
	# Fonction qui compte le nombre total de files hébergés par le noeud,
	# Puis qui met à jour la base de données avec la fonction adéquate
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT id FROM Fichiers WHERE 1""")
		rows = cursor.fetchall()
	except Exception as e:
		logs.addLogs("ERROR : Problem with the database (comptNbFichiers()):" + str(e))
	nbTotal = 0
	for row in rows:
		nbTotal += 1
	# On met à jour directement dans la BDD
	modifStats("NbFichiers", nbTotal)

def comptNbFichiersExt():
	# Fonction qui compte le nombre total de files connus par le noeud,
	# Puis qui met à jour la base de données avec la fonction adéquate
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT id FROM FichiersExt WHERE 1""")
		rows = cursor.fetchall()
	except Exception as e:
		logs.addLogs("ERROR : Problem with the database (comptNbFichiersExt()):" + str(e))
	nbTotal = 0
	for row in rows:
		nbTotal += 1
	# On met à jour directement dans la BDD
	modifStats("NbFichiersExt", nbTotal)

def comptNbNoeuds():
	# Fonction qui compte le nombre total de neouds connus par le noeud,
	# Puis qui met à jour la base de données avec la fonction adéquate
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT id FROM Noeuds WHERE 1""")
		rows = cursor.fetchall()
	except Exception as e:
		logs.addLogs("ERROR : Problem with the database (comptNbNoeuds()):" + str(e))
	nbTotal = 0
	for row in rows:
		nbTotal += 1
	# On met à jour directement dans la BDD
	modifStats("NbNoeuds", nbTotal)

def modifStats(colonne, valeur=-1):
	# Si valeur = -1, on incrémente, sinon on assigne la valeur en paramètres
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if valeur == -1:
			if colonne == "NbNoeuds":
				cursor.execute("""UPDATE Statistiques SET NbNoeuds = 1 WHERE 1""")
			elif colonne == "NbFichiersExt":
				cursor.execute("""UPDATE Statistiques SET NbFichiersExt = 1 WHERE 1""")
			elif colonne == "NbSN":
				cursor.execute("""UPDATE Statistiques SET NbSN = 1 WHERE 1""")
			elif colonne == "NbFichiers":
				cursor.execute("""UPDATE Statistiques SET NbFichiers = 1 WHERE 1""")
			elif colonne == "PoidsFichiers":
				cursor.execute("""UPDATE Statistiques SET PoidsFichiers = 1 WHERE 1""")
			elif colonne == "NbEnvsLstNoeuds":
				cursor.execute("""UPDATE Statistiques SET NbEnvsLstNoeuds = 1 WHERE 1""")
			elif colonne == "NbEnvsLstFichiers":
				cursor.execute("""UPDATE Statistiques SET NbEnvsLstFichiers = 1 WHERE 1""")
			elif colonne == "NbEnvsLstFichiersExt":
				cursor.execute("""UPDATE Statistiques SET NbEnvsLstFichiersExt = 1 WHERE 1""")
			elif colonne == "NbEnvsFichiers":
				cursor.execute("""UPDATE Statistiques SET NbEnvsFichiers = 1 WHERE 1""")
			elif colonne == "NbPresence":
				cursor.execute("""UPDATE Statistiques SET NbPresence = 1 WHERE 1""")
			elif colonne == "NbReceptFichiers":
				cursor.execute("""UPDATE Statistiques SET NbReceptFichiers = 1 WHERE 1""")
			else:
				logs.addLogs("ERROR : This statistic is unknown : "+str(colonne))
		else:
			if colonne == "NbNoeuds":
				cursor.execute("""UPDATE Statistiques SET NbNoeuds = ? WHERE 1""", (str(valeur),))
			elif colonne == "NbFichiersExt":
				cursor.execute("""UPDATE Statistiques SET NbFichiersExt = ? WHERE 1""", (str(valeur),))
			elif colonne == "NbSN":
				cursor.execute("""UPDATE Statistiques SET NbSN = ? WHERE 1""", (str(valeur),))
			elif colonne == "NbFichiers":
				cursor.execute("""UPDATE Statistiques SET NbFichiers = ? WHERE 1""", (str(valeur),))
			elif colonne == "PoidsFichiers":
				cursor.execute("""UPDATE Statistiques SET PoidsFichiers = ? WHERE 1""", (str(valeur),))
			elif colonne == "NbEnvsLstNoeuds":
				cursor.execute("""UPDATE Statistiques SET NbEnvsLstNoeuds = ? WHERE 1""", (str(valeur),))
			elif colonne == "NbEnvsLstFichiers":
				cursor.execute("""UPDATE Statistiques SET NbEnvsLstFichiers = ? WHERE 1""", (str(valeur),))
			elif colonne == "NbEnvsLstFichiersExt":
				cursor.execute("""UPDATE Statistiques SET NbEnvsLstFichiersExt = ? WHERE 1""", (str(valeur),))
			elif colonne == "NbEnvsFichiers":
				cursor.execute("""UPDATE Statistiques SET NbEnvsFichiers = ? WHERE 1""", (str(valeur),))
			elif colonne == "NbPresence":
				cursor.execute("""UPDATE Statistiques SET NbPresence = ? WHERE 1""", (str(valeur),))
			elif colonne == "NbReceptFichiers":
				cursor.execute("""UPDATE Statistiques SET NbReceptFichiers = ? WHERE 1""", (str(valeur),))
			else:
				logs.addLogs("ERROR : This statistic is unknown : "+str(colonne))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.addLogs("ERROR : Problem with database (modifStats()):" + str(e))
		logs.addLogs(str(valeur) + colonne)
	conn.close()

def compterStats(colonne):
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if colonne == "NbNoeuds":
			cursor.execute("""SELECT NbNoeuds FROM Statistiques""")
		elif colonne == "NbFichiersExt":
			cursor.execute("""SELECT NbFichiersExt FROM Statistiques""")
		elif colonne == "NbSN":
			cursor.execute("""SELECT NbSN FROM Statistiques""")
		elif colonne == "NbFichiers":
			cursor.execute("""SELECT NbFichiers FROM Statistiques""")
		elif colonne == "PoidsFichiers":
			cursor.execute("""SELECT PoidsFichiers FROM Statistiques""")
		elif colonne == "NbEnvsLstNoeuds":
			cursor.execute("""SELECT NbEnvsLstNoeuds FROM Statistiques""")
		elif colonne == "NbEnvsLstFichiers":
			cursor.execute("""SELECT NbEnvsLstFichiers FROM Statistiques""")
		elif colonne == "NbEnvsLstFichiersExt":
			cursor.execute("""SELECT NbEnvsLstFichiersExt FROM Statistiques""")
		elif colonne == "NbEnvsFichiers":
			cursor.execute("""SELECT NbEnvsFichiers FROM Statistiques""")
		elif colonne == "NbPresence":
			cursor.execute("""SELECT NbPresence FROM Statistiques""")
		elif colonne == "NbReceptFichiers":
			cursor.execute("""SELECT NbReceptFichiers FROM Statistiques""")
		else:
			logs.addLogs("ERROR : This statistic is unknown : "+str(colonne))
		conn.close()
	except Exception as e:
		logs.addLogs("ERROR : Problem with database (compterStats()):" + str(e))
	conn.close()
	return str(cursor.fetchone())[1:-2]
