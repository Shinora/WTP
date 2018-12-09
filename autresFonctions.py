#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import select
import sys
import sqlite3
import logs
import os
import BDD
import hashlib
import re
import urllib

def portLibre(premierPort):
	# Fonction qui cherche les ports de la machine qui sont libres
	# Et renvoie le premier trouvé, en partant du port initial, donné.
	port = True
	while port:
		clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
		    clientsocket.connect(('127.0.0.1' , premierPort))
		except ConnectionRefusedError:
		    # Le port est libre !
		    port = False
		else:
		    # Le port est déjà utilisé !
		    premierPort += 1
	return premierPort

def lsteFichiers(): 
	# ATTENTION !! IL FAUT CONNAITRE SON IP EXTERNE POUR POUVOIR L'AJOUTER EN FIN DE LIGNE
	# CAR CHAQUE LIGNE EST DE TYPE SHA256fichier.ext @ IP:Port
	# Fonction qui retourne un fichier qui contient tous les
	# noms des fichers hébergés par le noeud,
	# et qui sont dans la BDD, un par ligne
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		BDD.creerBase()
	try: 
		os.makedirs("HOSTEDFILES")
	except OSError:
		if not os.path.isdir("HOSTEDFILES"):
			raise
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	cursor.execute("""SELECT Nom FROM Fichiers WHERE 1""")
	rows = cursor.fetchall()
	fileDir = "HOSTEDFILES/listeFichiers"
	# On vide le fichier au cas où
	vidage = open(fileDir, "w")
	vidage.write("")
	vidage.close()
	# On cherche notre IP
	monIP = connaitreIP()
	# Puis on commence l'importation
	fluxEcriture = open(fileDir, "a")
	for row in rows:
		fluxEcriture.write(row[0]+" @ "+monIP+":5555\n")
	fluxEcriture.close()
	# Maintenant on va trouver le SHA256 du fichier
	fluxSHA = open(fileDir, "r")
	contenu = fluxSHA.read()
	fluxSHA.close()
	nomFichier = hashlib.sha256(contenu.encode()).hexdigest() + ".extwtp"
	cheminFichier = "HOSTEDFILES/" + nomFichier
	os.rename(fileDir, cheminFichier)
	return nomFichier

def lsteNoeuds():
	# Fonction qui retourne un fichier qui contient toutes les
	# IP+PORT des noeuds connus par ce noeud
	# et qui sont dans la BDD, un par ligne
	try:
		with open('WTP.db'): pass
	except IOError:
		logs.ajtLogs("ERREUR : Base introuvable... Création d'une nouvelle base.")
		BDD.creerBase()
	try: 
		os.makedirs("HOSTEDFILES")
	except OSError:
		if not os.path.isdir("HOSTEDFILES"):
			raise
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	cursor.execute("""SELECT IP FROM Noeuds WHERE 1""")
	rows = cursor.fetchall()
	fileDir = "HOSTEDFILES/listeNoeuds"
	# On vide le fichier au cas où
	vidage = open(fileDir, "w")
	vidage.write("")
	vidage.close()
	# Puis on commence l'importation
	fluxEcriture = open(fileDir, "a")
	for row in rows:
		fluxEcriture.write(row[0]+"\n")
	fluxEcriture.close()
	# Maintenant on va trouver le SHA256 du fichier
	fluxSHA = open(fileDir, "r")
	contenu = fluxSHA.read()
	fluxSHA.close()
	nomFichier = hashlib.sha256(contenu.encode()).hexdigest() + ".extwtp"
	cheminFichier = "HOSTEDFILES/" + nomFichier
	os.rename(fileDir, cheminFichier)
	return nomFichier

def lireListeNoeuds(nomFichier):
	# Fonction qui lit la liste de noeuds ligne par ligne et qui ajoute les noeuds dans la base de données
	cheminFichier = "HOSTEDFILES/"+nomFichier
	f = open(cheminFichier,'r')
	lignes  = f.readlines()
	f.close()
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	for ligne in lignes:
		if reg.match(ligne):
			# Si la ligne est une IP
			BDD.ajouterEntree("Noeuds", ligne)
	# Puis on supprime le fichier car on en n'a plus besoin
	os.remove(cheminFichier)
	logs.ajtLogs("INFO : Un fichier contenant une liste de noeuds a été parsé puis supprimé.")

def lireListeFichiers(nomFichier):
	# Fonction qui lit la liste de fichiers ligne par ligne et qui ajoute les noeuds dans la base de données
	# Chaque ligne est de type SHA256fichier.ext @ IP:Port
	cheminFichier = "HOSTEDFILES/"+nomFichier
	f = open(cheminFichier,'r')
	lignes  = f.readlines()
	f.close()
	for ligne in lignes:
		nomFichier = ligne[:ligne.find(" @ ")]
		ipPort = ligne[ligne.find(" @ ")+3:]
		BDD.ajouterEntree("FichiersExt", nomFichier, ipPort)
	# Puis on supprime le fichier car on en n'a plus besoin
	os.remove(cheminFichier)
	logs.ajtLogs("INFO : Un fichier contenant une liste de fichiers a été parsé puis supprimé.")

def connaitreIP():
	# Fonction qui retourne l'IP externe du noeud qui lance cette fonction
	page=urllib.request.urlopen('https://myrasp.fr/Accueil/monip.php')
	return page.read()

def fillConfFile():
	def_port = int(input("Entrez votre port par défaut : "))
	min_port = int(input("Entrez le port minimal selectionnable : "))
	max_port = int(input("Entrez le port maximal selectionnable : "))
	blacklist = []
	loop_blacklist = 1
	while loop_blacklist ==1:
		black_ip = str(input("Entrez une ip que vous souhaitez blacklister : "))
		blacklist.append(black_ip)
		loop_request = bool(input("Voulez vous blacklister une autre ip ? (1 = Oui / O = Non) "))
		if loop_request == 0:
			loop_blacklist = 0
		elif loop_request == 1:
			pass
		else:
			loop_request = 0
	autostart = bool(input("Voulez vous activer le démarrage automatique ? ( 0 = Non / 1 = Oui ) : "))
	conf_file = open("wtp.conf", "a")
	conf_file.write("Port par defaut : ", def_port, "\n")
	conf_file.write("Port Min : ", min_port, "\n")
	conf_file.write("Port Max : ", max_port, "\n")
	if autostart == 1:
		conf_file.write("Autostart : Oui \n")
	else:
		conf_file.write("Autostart : Non")
	conf_file.write("Blacklist [ ")
	for ip in blacklist:
		conf_file.write(ip + " ; \n")
	conf_file.write(" ]")
	conf_file.close()