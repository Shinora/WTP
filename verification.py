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
import maj


def verifSources():
	i = 0
	fichiers= ["autresFonctions", "BDD", "clientCMD", "echangeFichiers", "echangeListes", "echangeNoeuds", "fctsMntc", "launcher", "logs", "maintenance", "reload", "search", "stats"]
	for i in range(1, len(fichiers):
		en_cours = fichiers[i]
		page = urllib.request.urlopen("https://myrasp.fr/WTPStatic/", en_cours)
		online_sha = str(page.read())
		acces_file = open(en_cours + ".py", "r")
		contenu = acces_file.read()
		acces_file.close()
		sha_fichier = hashlib.sha256(contenu.encode()).hexdigest() + ".extwtp"
		if online_sha != sha_fichier:
			maj.forec = 1
			maj.verifMAJ()
		i+=1

		
	

