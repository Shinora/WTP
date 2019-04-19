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
import config
#import ssl
from random import randint

def portLibre(premierPort):
	# Fonction qui cherche les ports de la machine qui sont libres
	# Et renvoie le premier trouvé, en partant du port initial, donné.
	port = True
	while port:
		clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			clientsocket.connect(('127.0.0.1' , int(premierPort)))
		except ConnectionRefusedError:
			# Le port est occupé !
			clientsocket.close()
			premierPort += 1
		else:
			# Le port est libre !
			clientsocket.close()
			premierPort += 1
			if premierPort < int(config.readConfFile("MaxPort")):
				return premierPort
			logs.addLogs("ERROR: All ports already in use")

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
	fileDir = "HOSTEDFILES/TEMP"+str(time.time())
	# On vide le file au cas où
	vidage = open(fileDir, "wb")
	vidage.write("")
	vidage.close()
	# On cherche notre IP
	monIP = connaitreIP()
	# Puis on commence l'importation
	fluxEcriture = open(fileDir, "ab")
	for row in rows:
		if filesExternes == 0:
			fluxEcriture.write(row[0]+" @ "+monIP+":"+str(config.readConfFile("defaultPort"))+"\n")
		else:
			fluxEcriture.write(row[0]+" @ "+row[1]+"\n")
	fluxEcriture.close()
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
	fileDir = "HOSTEDFILES/TEMP"+str(time.time())
	# On vide le file au cas où
	vidage = open(fileDir, "wb")
	vidage.write("")
	vidage.close()
	# Puis on commence l'importation
	fluxEcriture = open(fileDir, "ab")
	for row in rows:
		fluxEcriture.write(row[0]+"\n")
	fluxEcriture.close()
	return fileName

def connaitreIP():
	# Fonction qui retourne l'IP externe du noeud qui lance cette fonction
	class AppURLopener(FancyURLopener):
			version = "Mozilla/5.0"
	opener = AppURLopener()
	try:
		page = opener.open("https://myrasp.fr/Accueil/monip.php")
	except Exception as e:
		addLogs("ERROR : We could not know the IP to the developers in connaitreIP() : " + str(e))
		print("\033[93mCheck your Internet connection.\033[0m")
	sortie = page.read().decode("utf-8")
	return sortie

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

def connectionClient(ip, port = "", verify = 1):
	if port == "":
		port = ip[ip.find(":")+1:]
		ip = ip[:ip.find(":")]
	if verifIPPORT(str(ip) + ":" + str(port)):
		try:
			conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			conn.settimeout(15)
			#conn = ssl.wrap_socket(conn, ssl_version=ssl.PROTOCOL_TLSv1, ciphers="ADH-AES256-SHA")
			conn.connect((ip, int(port)))
		except Exception as e:
			logs.addLogs("INFO : Unable to connect to " + str(ip) + ":" + str(port) + " Reason : " + str(e))
		else:
			return conn
	if verify == 1:
		# On ajoute le noeud dans la liste des noeuds Hors Connection s'il n'y est pas déjà
		# (Mais on ne l'incrémente pas s'il l'est déjà)
		IppeerPort = ip+":"+str(port)
		BDD.ajouterEntree("NoeudsHorsCo", IppeerPort)
		BDD.supprEntree("Noeuds", IppeerPort)
	return "=cmd ERROR"

def verifFiles():
	try:
		os.makedirs("HOSTEDFILES")
	except OSError:
		if not os.path.isdir("HOSTEDFILES"):
			raise
	try:
		os.makedirs("ADDFILES")
	except OSError:
		if not os.path.isdir("ADDFILES"):
			raise
	try:
		os.makedirs(".TEMP")
	except OSError:
		if not os.path.isdir(".TEMP"):
			raise

def verifIPPORT(ipport):
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(str(ipport)): # Si ipport est un ip:port
		return 1
	return 0

def ask(question):
	while 1:
		try:
			result = str(input(str(question) + "\n>>> "))
		except ValueError as e:
			print("\033[91mYour input isn't correct. Error : " + str(e)+"\033[0m")
		else:
			return result

def protip():
	# Fonction qui affiche une ligne au hazard du fichier protip.txt
	try:
		f = open("protip.txt", 'r')
		lines = f.readlines()
		f.close()
	except Exception as e:
		logs.addLogs("ERROR : Unable de read the file protip.txt : "+str(e))
	else:
		hazard = randint(0,len(lines))
		nbre = 0
		for line in lines:
			if hazard == nbre:
				print(line)
				break
			nbre += 1
