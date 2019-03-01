#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import sqlite3
import logs
import os
import BDD
import hashlib
import re
import time
from Crypto import Random
from Crypto.Cipher import AES
from urllib.request import *
from os import get_terminal_size

def portLibre(premierPort):
	# Fonction qui cherche les ports de la machine qui sont libres
	# Et renvoie le premier trouvé, en partant du port initial, donné.
	port = True
	while port:
		clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			clientsocket.connect(('127.0.0.1' , int(premierPort)))
		except ConnectionRefusedError:
			# Le port est libre !
			port = False
		else:
			# Le port est déjà utilisé !
			premierPort += 1
		if premierPort < int(readConfFile("MaxPort")):
			return premierPort
		logs.addLogs("ERROR: All ports already in use")
		time.sleep(1)

def lsteFichiers(filesExternes = 0): 
	# ATTENTION !! IL FAUT CONNAITRE SON IP EXTERNE POUR POUVOIR L'AJOUTER EN FIN DE LIGNE
	# CAR CHAQUE LIGNE EST DE TYPE SHA256file.ext @ IP:Port
	# Fonction qui retourne un file qui contient tous les
	# noms des fichers hébergés par le noeud,
	# et qui sont dans la BDD, un par ligne
	# Si filesExternes = 1, on doit faire la liste des focihers externes connus et non des files hébergés
	BDD.verifExistBDD()
	try: 
		os.makedirs("HOSTEDFILES")
	except OSError:
		if not os.path.isdir("HOSTEDFILES"):
			raise
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	if filesExternes == 0:
		cursor.execute("""SELECT Nom FROM Fichiers WHERE 1""")
	else:
		cursor.execute("""SELECT Nom FROM FichiersExt WHERE 1""")
	rows = cursor.fetchall()
	fileDir = "HOSTEDFILES/listeFichiers"
	# On vide le file au cas où
	vidage = open(fileDir, "w")
	vidage.write("")
	vidage.close()
	# On cherche notre IP
	monIP = connaitreIP()
	# Puis on commence l'importation
	fluxEcriture = open(fileDir, "a")
	for row in rows:
		if filesExternes == 0:
			fluxEcriture.write(row[0]+" @ "+monIP+":"+str(readConfFile("defaultPort"))+"\n")
		else:
			fluxEcriture.write(row[0]+" @ "+row[1]+"\n")
	fluxEcriture.close()
	# Maintenant on va trouver le SHA256 du file
	fluxSHA = open(fileDir, "r")
	contenu = fluxSHA.read()
	fluxSHA.close()
	fileName = hashlib.sha256(contenu.encode()).hexdigest() + ".extwtp"
	pathFichier = "HOSTEDFILES/" + fileName
	os.rename(fileDir, pathFichier)
	return fileName

def lsteNoeuds():
	# Fonction qui retourne un file qui contient toutes les
	# IP+PORT des noeuds connus par ce noeud
	# et qui sont dans la BDD, un par ligne
	BDD.verifExistBDD()
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
	# On vide le file au cas où
	vidage = open(fileDir, "w")
	vidage.write("")
	vidage.close()
	# Puis on commence l'importation
	fluxEcriture = open(fileDir, "a")
	for row in rows:
		fluxEcriture.write(row[0]+"\n")
	fluxEcriture.close()
	# Maintenant on va trouver le SHA256 du file
	fluxSHA = open(fileDir, "r")
	contenu = fluxSHA.read()
	fluxSHA.close()
	fileName = hashlib.sha256(contenu.encode()).hexdigest() + ".extwtp"
	pathFichier = "HOSTEDFILES/" + fileName
	os.rename(fileDir, pathFichier)
	return fileName

def lireListeNoeuds(fileName):
	# Fonction qui lit la liste de noeuds ligne par ligne et qui ajoute les noeuds dans la base de données
	pathFichier = "HOSTEDFILES/"+fileName
	f = open(pathFichier,'r')
	lignes  = f.readlines()
	f.close()
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	for ligne in lignes:
		if reg.match(ligne):
			# Si la ligne est une IP
			BDD.ajouterEntree("Noeuds", ligne)
	# Puis on supprime le file car on en n'a plus besoin
	os.remove(pathFichier)
	logs.addLogs("INFO : A file containing a peer list was parsed and deleted.")

def lireListeFichiers(fileName):
	# Fonction qui lit la liste de files ligne par ligne et qui ajoute les noeuds dans la base de données
	# Chaque ligne est de type SHA256file.ext @ IP:Port
	pathFichier = "HOSTEDFILES/"+fileName
	f = open(pathFichier,'r')
	lignes  = f.readlines()
	f.close()
	for ligne in lignes:
		fileName = ligne[:ligne.find(" @ ")]
		ipPort = ligne[ligne.find(" @ ")+3:]
		BDD.ajouterEntree("FichiersExt", fileName, ipPort)
	# Puis on supprime le file car on en n'a plus besoin
	os.remove(pathFichier)
	logs.addLogs("INFO : A file containing a list of files was parsed and deleted.")

def connaitreIP():
	# Fonction qui retourne l'IP externe du noeud qui lance cette fonction
	class AppURLopener(FancyURLopener):
			version = "Mozilla/5.0"
	opener = AppURLopener()
	page = opener.open("https://myrasp.fr/Accueil/monip.php")
	return page.read().decode("utf-8")

def afficherLogo():
	largeur = int(str(get_terminal_size())[25:str(get_terminal_size()).find(",")])
	print("")
	print("██╗    ██╗████████╗██████╗ ".center(largeur))
	print("██║    ██║╚══██╔══╝██╔══██╗".center(largeur))
	print("██║ █╗ ██║   ██║   ██████╔╝".center(largeur))
	print("██║███╗██║   ██║   ██╔═══╝ ".center(largeur))
	print("╚███╔███╔╝   ██║   ██║     ".center(largeur))
	print(" ╚══╝╚══╝    ╚═╝   ╚═╝     ".center(largeur))
	print("")
	print("")

def connectionClient(ip, port, verify = 1):
	ipPort = str(ip) + ":" + str(port)
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(ipPort):
		try:
			connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			connexion_avec_serveur.connect((ip, int(port)))
		except ConnectionRefusedError as e:
			logs.addLogs("INFO : Unable to connect to " + str(ip) + ":" + str(port) + " Reason : " + str(e))
		except ConnectionResetError as e:
			logs.addLogs("INFO : Unable to connect to " + str(ip) + ":" + str(port) + " Reason : " + str(e))
		except OSError as e:
			logs.addLogs("ERROR : Unable to connect to " + str(ip) + ":" + str(port) + " Reason : " + str(e))
		else:
			return connexion_avec_serveur
	if verify == 1:
		# On ajoute le noeud dans la liste des noeuds Hors Connection s'il n'y est pas déjà
		# (Mais on ne l'incrémente pas s'il l'est déjà)
		IppeerPort = ip+":"+port
		BDD.ajouterEntree("NoeudsHorsCo", IppeerPort)
		BDD.supprEntree("Noeuds", IppeerPort)
	return "=cmd ERROR"

def createCipherAES(key):
	block_size = 16
	mode = AES.MODE_CFB
	iv = Random.new().read(block_size)
	return AES.new(key, mode, iv)
