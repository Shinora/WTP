#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
from datetime import datetime

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