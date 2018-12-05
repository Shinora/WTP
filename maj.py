#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import select
import sys
import os
import os.path
import logs
import zipfile
import urllib
import time

def verifMAJ():
	# Fonction qui a pour but de vérifier si il y a des mises à jour à faire
	# Elle va regarder sur une page de myrasp.fr la dernière version du protocol
	# Et si elle a une version différente, on télécharge le fichier zip contenant les nouvelles sources
	versionActuelle = "0.0.1"
	page=urllib.request.urlopen('https://static.myrasp.fr/WTP/latestWTP.php')
	latest = str(page.read())
	if versionActuelle != latest:
		# Il faut mettre à jour
		logs.ajtLogs("INFO : Démmarage de la mise à jour de V" + versionActuelle + " à V" + latest)
		# Le fichier zip a un nom de forme WTPversion.zip Ex : WTP0.0.1.zip
		nomFichier = "WTP"+latest+".zip"
		url = 'https://static.myrasp.fr/WTP/'+nomFichier
		# Vérifier si le dossier .MAJ existe, sinon le créer
		try: 
			os.makedirs(".MAJ")
		except OSError:
			if not os.path.isdir(".MAJ"):
				raise
		with open('.MAJ/'+nomFichier, 'wb') as archive:
			archive.write(urllib.request.urlopen(url).read())
		# Le téléchargement des nouvelles sources est terminé
		# Extraction dans .MAJ/version Ex : .MAJ/0.0.1/
		# Vérifier si le dossier .MAJ/version existe, sinon le créer
		try: 
			os.makedirs(".MAJ/"+latest)
		except OSError:
			if not os.path.isdir(".MAJ/"+latest):
				raise
		with zipfile.ZipFile(".MAJ/"+nomFichier,"r") as zip_ref:
			zip_ref.extractall(".MAJ/"+latest+"/")
		# Extraction terminée
		# Maintenant il faut remplacer les anciens fichiers par les nouveaux
		liste = os.listdir(".MAJ/"+latest+"/")
		nbFichiers = len(liste)
		for x in range(nbFichiers):
			newFichier = ".MAJ/"+latest+"/"+liste[x]
			oldFichier = liste[x]
			# On copie le contenu du nouveau fichier
			fichier = open(newFichier, "r")
			contenuNewFichier = fichier.read()
			fichier.close()
			# On remplace l'ancien par la copie
			fichier = open(oldFichier, "w")
			fichier.write(contenuNewFichier)
			fichier.close()
			logs.ajtLogs("INFO : Le fichier " + oldFichier + " a été mis à jour")
		logs.ajtLogs("INFO : La mise à jour est terminée")
		# Il faut redemarrer le protocol
		cmd = os.popen("python3 reload.py", 'r')
	else:
		logs.ajtLogs("INFO : Pas de mise à jour disponible")