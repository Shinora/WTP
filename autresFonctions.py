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
import time
from  urllib.request import *

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
		if premierPort < int(autresFonctions.readConfFile("Port par defaut")):
			return premierPort
		logs.ajtLogs("ERROR : Tous les ports sont déjà utilisés")
		time.sleep(1)

def lsteFichiers(fichiersExternes = 0): 
	# ATTENTION !! IL FAUT CONNAITRE SON IP EXTERNE POUR POUVOIR L'AJOUTER EN FIN DE LIGNE
	# CAR CHAQUE LIGNE EST DE TYPE SHA256fichier.ext @ IP:Port
	# Fonction qui retourne un fichier qui contient tous les
	# noms des fichers hébergés par le noeud,
	# et qui sont dans la BDD, un par ligne
	# Si fichiersExternes = 1, on doit faire la liste des focihers externes connus et non des fichiers hébergés
	BDD.verifExistBDD()
	try: 
		os.makedirs("HOSTEDFILES")
	except OSError:
		if not os.path.isdir("HOSTEDFILES"):
			raise
	conn = sqlite3.connect('WTP.db')
	cursor = conn.cursor()
	if fichiersExternes == 0:
		cursor.execute("""SELECT Nom FROM Fichiers WHERE 1""")
	else:
		cursor.execute("""SELECT Nom FROM FichiersExt WHERE 1""")
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
		if fichiersExternes == 0:
			fluxEcriture.write(row[0]+" @ "+monIP+":"+str(autresFonctions.readConfFile("Port par defaut"))+"\n")
		else:
			fluxEcriture.write(row[0]+" @ "+row[1]+"\n")
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
	class AppURLopener(FancyURLopener):
			version = "Mozilla/5.0"
	opener = AppURLopener()
	page = opener.open("https://myrasp.fr/Accueil/monip.php")
	return page.read().decode("utf-8")

def fillConfFile():
	# On vide le fichier avant de le remplir de nouveau
	supprContenu = open("wtp.conf", "w")
	supprContenu.write("")
	supprContenu.close()
	def_port = input("Entrez votre port principal (defaut:5555) : ")
	if def_port == "":
		# L'utilisateur veut laisser la valeur par défaut
		def_port = 5555
	else:
		def_port = int(def_port)
	portVPN = input("Entrez votre port VPN (defaut:5556) : ")
	if portVPN == "":
		# L'utilisateur veut laisser la valeur par défaut
		portVPN = 5556
	else:
		portVPN = int(portVPN)
	portDNS = input("Entrez votre port DNS (defaut:5557) : ")
	if portDNS == "":
		# L'utilisateur veut laisser la valeur par défaut
		portDNS = 5557
	else:
		portDNS = int(portDNS)
	min_port = 1
	max_port = 0
	while min_port > max_port:
		print("Le port minimal doit être plus petit que le port maximal")
		min_port = input("Entrez le port minimal utilisable (defaut:5550): ")
		if min_port == "":
			# L'utilisateur veut laisser la valeur par défaut
			min_port = 5550
		else:
			min_port = int(min_port)
		max_port = input("Entrez le port maximal utilisable (defaut:5600): ")
		if max_port == "":
			# L'utilisateur veut laisser la valeur par défaut
			max_port = 5600
		else:
			max_port = int(max_port)
	blacklist = []
	loop_blacklist = 1
	while loop_blacklist ==1:
		black_ip = str(input("Entrez une ip que vous souhaitez blacklister : "))
		blacklist.append(black_ip)
		loop_request = int(input("Voulez vous blacklister une autre ip ? (1 = Oui / O = Non) "))
		if loop_request != 0:
			loop_blacklist = 1
		else:
			loop_blacklist = 0
	autostart = input("Voulez vous activer le démarrage automatique ? ( 0 = Non / 1 = Oui ) : ")
	conf_file = open("wtp.conf", "a")
	conf_file.write("Port par defaut : "+str(def_port)+"\n")
	conf_file.write("Port VPN : "+str(portVPN)+"\n")
	conf_file.write("Port DNS : "+str(portDNS)+"\n")
	conf_file.write("Port Min : "+str(min_port)+"\n")
	conf_file.write("Port Max : "+str(max_port)+"\n")
	if autostart == "1":
		conf_file.write("Autostart : Oui\n")
	else:
		conf_file.write("Autostart : Non\n")
	conf_file.write("SuperNoeud : Non\n")
	conf_file.write("Blacklist [\n")
	for ip in blacklist:
		conf_file.write(ip + " ; \n")
	conf_file.write("]")
	conf_file.close()

def readConfFile(parametre): # Fonctionne pour tout sauf Blacklist
	# Fonction qui lit le fichier de configuration et qui retourne l'information demandée en paramètres
	try:
		with open('wtp.conf'): pass
	except IOError:
		# Le fichier n'existe pas
		fillConfFile()
	if os.path.getsize("wtp.conf") < 80:
		# Le fichier est très léger, il ne peut contenir les informations
		# Il faut donc le recréer
		fillConfFile()
	f = open("wtp.conf",'r')
	lignes  = f.readlines()
	f.close()
	for ligne in lignes:
		# On lit le fichier ligne par ligne et si on trouve le paramètre dans la ligne,
		# on renvoie ce qui se trouva après
		if ligne[:len(parametre)] == parametre:
			# On a trouvé ce que l'on cherchait
			# Maintenant on enlève " : "
			return ligne[len(parametre)+3:]

def afficherLogo():
	print("")
	print("                        ██╗    ██╗████████╗██████╗ ")
	print("                        ██║    ██║╚══██╔══╝██╔══██╗")
	print("                        ██║ █╗ ██║   ██║   ██████╔╝")
	print("                        ██║███╗██║   ██║   ██╔═══╝ ")
	print("                        ╚███╔███╔╝   ██║   ██║     ")
	print("                         ╚══╝╚══╝    ╚═╝   ╚═╝     ")
	print("")
	print("")

