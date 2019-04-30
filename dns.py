import logs
import hashlib
import sqlite3
import autresFonctions
import config
import BDD
import echangeListes
import fctsClient
from color import c

def addNDD(ipport, sha, ndd, password):
	error = 0
	if autresFonctions.verifIPPORT(ipport): # Si ipport est un ip:port
		connexion_avec_serveur = autresFonctions.connectionClient(ipport)
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			logs.addLogs("Connection established with the DNS")
			# =cmd DNS AddDNS sha ******* ndd ******* pass *******
			request = "=cmd DNS AddDNS sha " + str(sha) + " ndd " + str(ndd) + " pass " + str(password)
			request = request.encode()
			connexion_avec_serveur.send(request)
			message = connexion_avec_serveur.recv(1024)
			connexion_avec_serveur.close()
			if message == "=cmd NDDDejaUtilise":
				error = 5
				print(str(c("red"))+"The domain name is already used."+str(c(""))+" If it belongs to you, you can modify it provided you know the password.")
			elif message == "=cmd SUCCESS":
				print(str(c("green"))+"The domain name and address SHA256 have been associated."+str(c("")))
			else:
				print(str(c("red"))+"An undetermined error occurred. Please try again later or change DNS peer."+str(c("")))
				error = 1
	else:
		error += 1
	return error

def addNoeudDNS(ipport, ipportNoeud):
	error = 0
	if autresFonctions.verifIPPORT(ipport):
		connexion_avec_serveur = autresFonctions.connectionClient(ipport)
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			logs.addLogs("Connection established with the DNS")
			# =cmd DNS AddDNSExt ipport ******
			request = "=cmd DNS AddDNSExt ipport " + ipportNoeud
			request = request.encode()
			connexion_avec_serveur.send(request)
			message = connexion_avec_serveur.recv(1024)
			connexion_avec_serveur.close()
			if message == "=cmd IPPORTDejaUtilise":
				error = 5
				print(str(c("red"))+"The peer DNS is already known by the receiver."+str(c("")))
			elif message == "=cmd SUCCESS":
				print(str(c("green"))+"The DNS pair has been added to the receiver base."+str(c("")))
			else:
				print(str(c("red"))+"An undetermined error occurred. Please try again later or change DNS peer."+str(c("")))
				error = 1
	else:
		error += 1
	return error

def modifNDD(ipport, ndd, adress, password):
	error = 0
	if autresFonctions.verifIPPORT(ipport):
		connexion_avec_serveur = autresFonctions.connectionClient(ipport)
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			logs.addLogs("Connection established with the DNS")
			# =cmd DNS modifNDD ndd ****** adress ****** pass ******
			request = "=cmd DNS modifNDD ndd " + str(ndd) + " adress " + str(adress) + " pass " + str(password)
			request = request.encode()
			connexion_avec_serveur.send(request)
			message = connexion_avec_serveur.recv(1024)
			connexion_avec_serveur.close()
			error = 0
			if message == "=cmd IPPORTDejaUtilise":
				error = 5
				print(str(c("red"))+"Le noeud DNS est déjà connu par le receveur."+str(c("")))
			elif message == "=cmd SUCCESS":
				print(str(c("green"))+"Le noeud DNS a bien été ajouté à la base du receveur."+str(c("")))
			else:
				print(str(c("red"))+"An undetermined error occurred. Please try again later or change DNS peer."+str(c("")))
				error += 1
	else:
		error += 1
	return error

def supprNDD(ipport, ndd, password):
	error = 0
	if autresFonctions.verifIPPORT(ipport):
		connexion_avec_serveur = autresFonctions.connectionClient(ipport)
		if str(connexion_avec_serveur) == "=cmd ERROR":
			error += 1
		else:
			logs.addLogs("Connection established with the DNS")
			# =cmd DNS supprNDD ndd ****** pass ******
			request = "=cmd DNS supprNDD ndd " + str(ndd) + " pass " + str(password)
			request = request.encode()
			connexion_avec_serveur.send(request)
			message = connexion_avec_serveur.recv(1024)
			if message != "=cmd SUCCESS":
				error += 1
			connexion_avec_serveur.close()
	else:
		error += 1
	return error

def modifEntree(nomTable, entree, entree1 = "", entree2 = ""):
	# Fonction qui permet de supprimer une entrée dans une table
	# Paramètres : Le nom de la table; le nouveau SHA256; le nom de domaine; le mot de passe non hashé
	problem = 0
	BDD.verifExistBDD()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	try:
		if nomTable == "DNS":
			if entree1 != "" and entree2 != "":
				# On vérifie que le mot de passe hashé est égal à celui de la base de données,
				# et si c'est le cas on peut suprimer la ligne
				cursor.execute("""SELECT PASSWORD FROM DNS WHERE NDD = ?""", (entree1,))
				rows = cursor.fetchall()
				nbRes = 0
				for row in rows:
					nbRes += 1
					if row[0] == hashlib.sha256(str(entree2).encode()).hexdigest():
						cursor.execute("""UPDATE DNS SET SHA256 = ? WHERE NDD = ?""", (entree, entree1))
						conn.commit()
					else:
						# Le mot de passe n'est pas valide.
						problem = 5
				if nbRes == 0:
					logs.addLogs("DNS : ERROR: The domain name to modify does not exist (modifEntree())")
					problem = 8
					problem += ajouterEntree("DNS", entree1, entree, entree2)
			else:
				logs.addLogs("DNS : ERROR: There is a missing parameter to perform this action (modifEntree())")
				problem += 1
		else:
			logs.addLogs("DNS : ERROR: The table name was not recognized (modifEntree()) : " + str(nomTable))
			problem += 1
		conn.commit()
	except Exception as e:
		conn.rollback()
		logs.addLogs("DNS : ERROR : Problem with the database (modifEntree()):" + str(e))
		problem += 1
	else:
		logs.addLogs("DNS : INFO : The domain name "+ entree1 +" has been modified.")
	conn.close()
	return problem

def majDNS(ipportNoeud = ""):
	# Fonction pour noeud DNS qui permet de mettre à jour toute sa base avec un autre noeud
	BDD.verifExistBDD()
	problem = 0
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	ipport = ""
	if ipportNoeud == "":
		try:
			cursor.execute("""SELECT IP FROM Noeuds WHERE Fonction = 'DNS' ORDER BY RANDOM() LIMIT 1""")
			rows = cursor.fetchall()
			conn.close()
		except Exception as e:
			conn.rollback()
			logs.addLogs("DNS : ERROR : Problem with the database (majDNS()):" + str(e))
			problem += 1
		else:
			for row in rows:
				ipport = row[0]
	else:
		ipport = ipportNoeud
		if ipport != "":
			# Maintenant on va demander au noeud DNS distant d'envoyer toutes ses entrées DNS pour
			# Que l'on puisse ensuite analyser, et ajouter/mettre à jour notre base
			connexion_avec_serveur = autresFonctions.connectionClient(ipport)
			if str(connexion_avec_serveur) != "=cmd ERROR":
				sendCmd = b""
				sendCmd = "=cmd DNS syncBase"
				connexion_avec_serveur.send(sendCmd.encode())
				rcvCmd = connexion_avec_serveur.recv(1024)
				rcvCmd = rcvCmd.decode()
				connexion_avec_serveur.close()
				# Le noeud renvoie le nom du fichier à télécharger
				# Et son IP:PortPrincipal, sinon =cmd ERROR
				if rcvCmd != "=cmd ERROR":
					# =cmd Filename ****** ipport ******
					filename = rcvCmd[14:rcvCmd.find(" ipport ")]
					ipport = rcvCmd[rcvCmd.find(" ipport ")+8:]
					ip = ipport[:ipport.find(":")]
					port = ipport[ipport.find(":")+1:]
					error += fctsClient.CmdDemandeFichier(ip, port, filename)
					if error == 0:
						echangeListes.filetoTable(filename, "DNS")
					else:
						problem += 1
				else:
					problem += 1
			else:
				problem += 1
		else:
			problem += 1
	return problem
