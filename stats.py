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
	BDD.modifStats("PoidsFichiers", tailleTotale)

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
	BDD.modifStats("NbFichiers", nbTotal)

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
	BDD.modifStats("NbFichiersExt", nbTotal)

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
	BDD.modifStats("NbNoeuds", nbTotal)
