import BDD
import autresFonctions
import logs
from Crypto import Random
from Crypto.Cipher import AES
import sqlite3
import config

# Les fonctions ici servent à chercher des files sur le réseau

def searchFile(fileName):
	# Fonction qui a pour but de chercher sur le réseau un file
	# Il faut d'abord chercher dans la BDD, et si il n'y est pas on cherche plus spécifiquement
	# IPpeerPort est la variable qui contient l'IP Port du noeud qui possède le file
	BDD.verifExistBDD()
	IPpeerPort = ""
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	# On va chercher dans les files hébergés
	try:
		cursor.execute("""SELECT id FROM Fichiers WHERE Nom = ?""", (fileName,))
	except Exception as e:
		logs.addLogs("ERROR : Problem with database (searchFile()):" + str(e))
	rows = cursor.fetchall()
	for row in rows:
		boucle += 1
		# Le file est hébergé par le noeud qui le cherche
		ipPortIci = "127.0.0.1:"+str(config.readConfFile("defaultPort"))
		IPpeerPort = ipPortIci
	# Si le file n'a pas été trouvé
	# Il faut chercher dans les files connus externes
	try:
		cursor.execute("""SELECT IP FROM FichiersExt WHERE Nom = ?""", (fileName,))
	except Exception as e:
		logs.addLogs("ERROR : Problem with database (searchFile()):" + str(e))
	else:
		rows = cursor.fetchall()
		for row in rows:
			# Le file est hébergé par un noeud connu
			IPpeerPort = str(row)
	if IPpeerPort == "":
		# Il faut demander aux noeuds que l'on connait
		tblNoeuds = BDD.aleatoire("Noeuds", "IP", 10)
		# On a 10 noeuds dans le tableau
		# Maintenant, il faut vérifier que au moins la moitiée des noeuds choisis aléatoirement
		# sont des noeuds "simple", puis mettre les noeuds "simple" au début du tableau
		tableauNoeudsSimple = []
		tableauSuperNoeuds = []
		for noeud in tblNoeuds:
			# On verifie chaque noeud
			fonctionNoeud = chercherInfo("Noeuds", noeud)
			if fonctionNoeud == "simple":
				tableauNoeudsSimple.append(noeud)
			if fonctionNoeud == "supernoeud" or fonctionNoeud == "DNS":
				tableauSuperNoeuds.append(noeud)
		if len(tableauNoeudsSimple) < 6:
			# Il n'y a pas assez de noeuds simples dans la liste,
			# Il faut aller en rechercher
			logs.addLogs("WARNING : Not enough simple peers")
		# On ajoute les super noeuds après les noeuds simples
		tblNoeuds = tableauNoeudsSimple + tableauSuperNoeuds
		for noeudActuel in tblNoeuds:
			# À chaque noeud on demande si il a le file ou s'il connait un noeud qui l'a
			# Maintenant on se connecte au noeud
			error = 0
			connexion_avec_serveur = autresFonctions.connectionClient(noeudActuel)
			if str(connexion_avec_serveur) == "=cmd ERROR":
				error += 1
			else:
				sendCmd = b""
				sendCmd = "=cmd rechercherFichier nom " + fileName
				sendCmd = sendCmd.encode()
				connexion_avec_serveur.send(sendCmd)
				rcvCmd = connexion_avec_serveur.recv(1024)
				rcvCmd = rcvCmd.decode()
				connexion_avec_serveur.close()
				if rcvCmd != "0":
					IPpeerPort = rcvCmd
					break
	return IPpeerPort # Peut retourner "" si il ne trouve pas d'hébergeur

def chercherFichier(fileName):
	# Fonction qui regarde dans sa BDD si il y a le file en question
	retour = 0
	retour = chercherInfo("Fichiers", fileName)
	if retour != 0 and str(retour) != "None":
		# Le noeud héberge le file demandé
		# Donc on retourne son IP
		return autresFonctions.connaitreIP()+":"+str(config.readConfFile("defaultPort"))
	retour = chercherInfo("FichiersExt", fileName)
	# ATTENTION ! Si le file n'est pas connu, 0 est retourné
	return retour

def searchNDD(url):
	# Fonction qui vérifie si le nom de file envoyé est plus petit qu'un SHA256
	# Si c'est le cas, il va chercher chez les noeuds de DNS si ils connaissent ce nom de domaine
	# Renvoie un SHA256
	sha = ""
	if len(url) <= 64:
		# Ce n'est pas un nom de file, car il est plus petit qu'un SHA256
		tableau = searchNoeud("DNS", 25)
		for noeud in tableau:
			noeud = str(noeud[0])
			error = 0
			connexion_avec_serveur = autresFonctions.connectionClient(noeud)
			if str(connexion_avec_serveur) == "=cmd ERROR":
				error += 1
			else:
				sendCmd = b""
				sendCmd = "=cmd DNS searchSHA ndd " + url
				sendCmd = sendCmd.encode()
				connexion_avec_serveur.send(sendCmd)
				rcvCmd = connexion_avec_serveur.recv(1024)
				rcvCmd = rcvCmd.decode()
				connexion_avec_serveur.close()
				if rcvCmd != "=cmd NNDInconnu" and rcvCmd != "=cmd ERROR":
					# On a trouvé !!
					sha = rcvCmd
					break
	return sha

def rechercheFichierEntiere(donnee):
	# Fonction qui cherche jusqu'à trouver l'IpPort d'un noeud qui héberge le file
	# La donnée passée en paramètres peut etre un nom de domaine, ou un sha256
	# Renvoi une erreur ou IP:Port;sha256
	retour = donnee
	if len(str(donnee)) <= 63:
		# C'est un nom de domaine
		retour = ""
		nbre = 0
		while retour == "":
			nbre += 1
			retour = searchNDD(donnee)
			if retour == "" and nbre > 9:
				# La fonction n'a pas trouvé le sha256 associé à ce nom de domaine
				# Elle a pu demander jusqu'à 250 DNS différents
				return "=cmd BADDNS"
	# Si on arrive là c'est que l'on connait le sha256 du file (c'est retour)
	retour2 = str(chercherFichier(retour))
	if retour2 != "0" and str(retour2) != "None":
		# Le noeud héberge déjà le file ou le connait
		return str(retour2 + ";" + retour)
	# Le noeud ne connait pas le file
	retour3 = searchFile(retour)
	if retour3 != "":
		return str(retour3 + ";" + retour)
	return "=cmd NOHOST"

def searchNoeud(role, nbre = 10):
	# Fonction qui  pour but de chercher 'nbre' noeuds ayant pour role 'role'
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT IP FROM Noeuds WHERE Fonction = ? ORDER BY RANDOM() LIMIT ?""", (role, nbre))
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.addLogs("ERROR : Problem with database (aleatoire()):" + str(e))
	rows = cursor.fetchall()
	tableau = []
	for row in rows:
		tableau.append(row)
		# On remplit le tableau avant de le retourner
	conn.close()
	return tableau

def chercherInfo(nomTable, info):
	# Fonction qui retourne une information demandée dans la table demandée dans une entrée demandé
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if nomTable == "Noeuds":
			cursor.execute("""SELECT Fonction FROM Noeuds WHERE IP = ?""", (info,))
		elif nomTable == "Fichiers":
			cursor.execute("""SELECT id FROM Fichiers WHERE Nom = ?""", (info,))
		elif nomTable == "FichiersExt":
			cursor.execute("""SELECT IP FROM FichiersExt WHERE Nom = ?""", (info,))
		elif nomTable == "BlackList":
			cursor.execute("""SELECT Rank FROM BlackList WHERE Name = ?""", (info,))
		else:
			logs.addLogs("ERROR : The table is unknown in chercherInfo : "+str(nomTable))
			return 0
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.addLogs("ERROR : Problem with database (chercherInfo()):" + str(e))
	for row in cursor.fetchall():
		conn.close()
		return row[0]
	return 0

def searchSHA(ndd):
	# Fonction qui a pour but de chercher le sha256 correspondant
	# au nom de domaine passé en paramètres s'il existe
	BDD.verifExistBDD()
	problem = 0
	sha256 = "0"
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		cursor.execute("""SELECT SHA256 FROM DNS WHERE NDD = ?""", (ndd,))
		rows = cursor.fetchall()
	except Exception as e:
		conn.rollback()
		logs.addLogs("DNS : ERROR : Problem with the database (searchSHA()):" + str(e))
		problem += 1
	else:
		nbRes = 0
		for row in rows:
			nbRes += 1
			if nbRes > 1:
				# On trouve plusieurs fois le même nom de domaine dans la base
				problem = 5
				logs.addLogs("DNS : ERROR: The domain name "+ ndd +" is present several times in the database")
			sha256 = row[0]
	conn.close()
	if problem > 1:
		return problem
	if sha256 == "0":
		return "INCONNU"
	return sha256
