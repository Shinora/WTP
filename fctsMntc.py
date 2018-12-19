#! /usr/bin/python
# -*- coding:utf-8 -*-

import logs
import BDD
import socket
import hashlib
import sqlite3
import os

def verifNoeud():
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		BDD.creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	cursor.execute("""SELECT IP FROM Noeuds WHERE 1""")
	rows = cursor.fetchall()
	for row in rows:
		# Prend un à un chaque noeud de la liste, et lui envoie une commande.
		# Si le noeud répond, on le laisse tranquille, sinon on le met dans une autre table.
		IpPortNoeud = row[0]
		#Départager l'IP et le port
		pos1 = IpPortNoeud.find(":")
		pos1 = pos1+1
		pos2 = len(IpPortNoeud)
		PortNoeud = int(IpPortNoeud[pos1:pos2])
		pos1 = pos1-1
		IPNoeud = IpPortNoeud[0:pos1]
		# Liaison tcp/ip
		c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Connection au receveur
		try:
			c.connect((IPNoeud, PortNoeud))
		except Exception as erreur:
			# Le noeud est injoignable, on le déplace dans une autre table.
			BDD.ajouterEntree("NoeudsHorsCo", IpPortNoeud)
			BDD.supprEntree("Noeuds", IpPortNoeud)
			logs.ajtLogs("ERREUR : Connection au noeud impossible : '" + str(erreur) + "' verifNoeud() --> fctsMntc.py")
		else:
			cmdAEnvoyer = "=cmd DemandePresence"
			cmdAEnvoyer = cmdAEnvoyer.encode()
			# On envoie le message
			c.send(cmdAEnvoyer)
			dataRecu = c.recv(1024)
			dataRecu = dataRecu.decode()
			if dataRecu != '=cmd Present':
				# Le noeud n'est pas connecté au réseau, on le déplace dans une autre table.
				BDD.ajouterEntree("NoeudsHorsCo", IpPortNoeud)
				BDD.supprEntree("Noeuds", IpPortNoeud)

def verifNoeudHS():
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		BDD.creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	cursor.execute("""SELECT IP FROM NoeudsHorsCo WHERE 1""")
	rows = cursor.fetchall()
	for row in rows:
		# Prend un à un chaque noeud de la liste, et lui envoie une commande.
		# Si le noeud répond, on le laisse tranquille, sinon on le met dans une autre table.
		IpPortNoeud = row[0]
		#Départager l'IP et le port
		pos1 = IpPortNoeud.find(':')
		pos1 = pos1+1
		pos2 = len(IpPortNoeud)
		PortNoeud = int(IpPortNoeud[pos1:pos2])
		pos1 = pos1-1
		IPNoeud = IpPortNoeud[0:pos1]
		# Liaison tcp/ip
		c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Connection au receveur
		try:
			c.connect((IPNoeud, PortNoeud))
		except:
			logs.ajtLogs("INFO : Connection au noeud HS impossible. verifNoeudHS() --> fctsMntc.py")
			# Le noeud n'est pas connecté au réseau
			# On incrémente son nombre de vérifs et on le supprime si besoin
			BDD.incrNbVerifsHS(IpPortNoeud)
			BDD.verifNbVerifsHS(IpPortNoeud)
		else:
			cmdAEnvoyer = b""
			cmdAEnvoyer = "=cmd DemandePresence"
			cmdAEnvoyer = cmdAEnvoyer.encode()
			# On envoie le message
			c.send(cmdAEnvoyer)
			dataRecu = c.recv(1024)
			dataRecu = dataRecu.decode()
			if dataRecu == '=cmd Present':
				# C'est bon, le noeud est connecté au reseau, 
				# on l'ajoute à la table normale et on le supprime de la table des noeuds HS
				BDD.ajouterEntree("Noeuds", IpPortNoeud)
				BDD.supprEntree("NoeudsHorsCo", IpPortNoeud)
			else:
				# Le noeud n'est pas connecté au réseau, on incrémente de 1 son nombre de vérifications.
				BDD.incrNbVerifsHS(IpPortNoeud)
				# On vérifie si le noeud a un nombre de vérifications inférieur à 10.
				# Si ce n'est pas le cas, il est supprimé définitivement.
				BDD.verifNbVerifsHS(IpPortNoeud)

def verifFichier():
	# Prend les fichiers un à un dans la BDD, puis les vérifie.
	# Il doit être présent sur le disque.
	# LE SHA256 doit être identique au nom.
	# Sinon on envoie vers la fonction qui supprime le fichier de la BDD et du disque
	try:
		with open('WTP.db'):
			pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		BDD.creerBase()
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	cursor.execute("""SELECT Chemin FROM Fichiers WHERE 1""")
	rows = cursor.fetchall()
	for row in rows:
		nomFichier = row[0]
		chemin = row[0]
		while nomFichier.find('/') != -1:
			nomFichier = nomFichier[nomFichier.find('/')+1:]
		SHAFichier = nomFichier[:nomFichier.find('.')]
		# Et voilà, on a juste le nom du fichier, sans extention,
		# ce qui correspond normalement au SHA256 du contenu de celui-ci
		fichier = open(chemin, "r")
		contenu = fichier.read()
		fichier.close()
		# On vérifie si le SHA256 correspond au contenu du fichier.
		SHAContenuFichier = hashlib.sha256(contenu.encode('utf-8')).hexdigest()
		if SHAFichier == SHAContenuFichier:
			# Le fichier a le même hash que son nom, c'est bon.
			# Si le programme est arrivé jusqu'à là, c'est que le fichier existe egalement.
			logs.ajtLogs("INFO : Le fichier " + nomFichier + " a bien été vérifié, sans erreurs.")
		else:
			#Il y a une erreur. Le fichier doit être supprimé,
			# car il peut nuire au bon fonctionnement du réseau.
			print("Ligne 137 : nomFichier : " + nomFichier)
			BDD.supprEntree("Fichiers", nomFichier)
			logs.ajtLogs("ERREUR : Le fichier " + nomFichier + " contenait des erreurs. Il a été supprimé.")

def creerFichier():
	# Fonction qui va s'executer via la maintenance assez régulièrement
	# Elle regarde dans le dossier ADDFILES si il y a des fichiers
	# Si oui, elle les copie dans le dossier HOSTEDFILES, les renomme de type SHA256.extention
	# Elle envoie vers la fonction contenue dans BDD.py qui va ajouter les fichiers à la base de données
	# Et pour finir, elle supprime les fichiers ajoutés de façon à ce que le dossier ADDFILES soit vide.
	repertoire = "ADDFILES"
	# Vérifier si le dossier ADDFILES existe, sinon le créer
	try:
		os.makedirs("ADDFILES")
	except OSError:
		if not os.path.isdir("ADDFILES"):
			raise
	# Vérifier si le dossier HOSTEDFILES existe, sinon le créer
	try:
		os.makedirs("HOSTEDFILES")
	except OSError:
		if not os.path.isdir("HOSTEDFILES"):
			raise
	dirs = os.listdir(repertoire)
	# This would print all the files and directories
	for file in dirs:
		fichier = repertoire + "/" + file
		if os.path.isfile(fichier):
			# L'élément est un fichier, c'est bon (et pas un dossier)
			with open(fichier, "r", encoding="utf-8") as fluxLecture:
				contenu = fluxLecture.read()
				fluxLecture.close()
			shaFichier = hashlib.sha256(contenu.encode()).hexdigest()
			osef, extention = os.path.splitext(fichier)
			filename = shaFichier + extention
			fileDir = "HOSTEDFILES/" + filename
			fluxEcriture = open(fileDir, "w")
			fluxEcriture.write(contenu)
			fluxEcriture.close()
			os.remove(fichier)
			# L'ajouter à la BDD
			BDD.ajouterEntree("Fichiers", filename)
			logs.ajtLogs("INFO : Un nouveau fichier hébergé a été ajouté avec succès : " + filename)
