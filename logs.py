#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
from datetime import datetime
import requests

 ####################################################
#                                                    #
# Sont ici les fonctions qui ont un rapport avec les #
# logs, qui se situent dans le fichier logs.txt qui  #
# est dans le même dossier que ce fichier.           #
#                                                    #
 ####################################################

# Fonction pour ajouter une ligne dans les logs.
# Elle n'a qu'un paramètre, le texte à ajouter aux logs.
# Il doit contenir à la fin le nom de la fonction.
def ajtLogs(texte):
	# [DATETIME] : TEXTE dans la fonction fonction()
	dateHeure = str(datetime.now()) # Ex : 2018-07-03 18:05:37.441483
	chaineFinale = "[{0}] : {1}\n".format(dateHeure[:19], texte)
	f = open("logs.txt", "a")
	f.write(chaineFinale)
	f.close()

# Fonction pour supprimer les logs
# Elle n'a aucun paramètre.
def supprLogs():
	f = open("logs.txt", "w")
	f.write("")
	f.close()

def rapportErreur(selection = " "):
	# Sélectionne les lignes ayant le mot clef de la selection ou les mots clefs plus graves
	# Envoie le tout à un serveur
	# INFO < WARNING < ERREUR
	megaStr = ""
	with open("logs.txt") as f :
		for line in f :
			if line.find(selection) != -1:
				megaStr += line
	f.close()
	data = {"text":megaStr}
	r = requests.post("https://myrasp.fr/WTPStatic/rapport.php", data = data)
	supprLogs()