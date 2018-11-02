#! /usr/bin/python
# -*- coding:utf-8 -*-

import time
import logs
import BDD
import fctsMntc


 ####################################################
#
# Boucle infinie qui a pour seul but de lancer des
# fonctions qui effectuent une maintenance du noeud
#
 ####################################################

try:
	with open(".TempMaintenance24H", "r"): pass
except IOError:
	# Le fichier n'existe pas.
	# On va donc le créer, et dans le doute mettre 0 pour le datetime,
	# de sorte à ce que la maintenance soit faite juste après
	f = open(".TempMaintenance24H", "w")
	f.write("0")
	f.close()

f = open(".TempMaintenance24H", "r")
derMtnc = f.read()
f.close()


# Et pareil pour l'importation de fichiers
try:
	with open(".TempMaintenance5M", "r"): pass
except IOError:
	# Le fichier n'existe pas.
	# On va donc le créer, et dans le doute mettre 0 pour le datetime,
	# de sorte à ce que la maintenance soit faite juste après
	f = open(".TempMaintenance5M", "w")
	f.write("0")
	f.close()

f = open(".TempMaintenance5M", "r")
derMtnc5M = f.read()
f.close()


tmpsActuel = str(time.time())
point = tmpsActuel.find('.')
tmpsAct = int(tmpsActuel[0:point])

# En cas de fichier vide, on attribue la valeur 0 pour ne pas avoir de problèmes
if derMtnc == "":
	derMtnc = 0
if derMtnc5M == "":
	derMtnc5M = 0

while 1:
	if int(derMtnc)+86400 < tmpsAct: # 24h = 86 400 sec
		# On peut lancer les fonctions
		# Puis on change le contenu du fichier temporel
		f = open(".TempMaintenance24H", "w")
		f.write(str(tmpsAct))
		f.close()
		derMtnc = tmpsAct
		fctsMntc.verifNoeud()
		fctsMntc.verifNoeudHS()
		fctsMntc.verifFichier()
		logs.ajtLogs("INFO : Maintenance de la base de données effectée avec succès.")
	if int(derMtnc5M)+275 < tmpsAct: # Moins de 5Min
		# On peut lancer les fonctions
		# Puis on change le contenu du fichier temporel
		f = open(".TempMaintenance5M", "w")
		f.write(str(tmpsAct))
		f.close()
		derMtnc5M = tmpsAct
		fctsMntc.creerFichier()
		logs.ajtLogs("INFO : Vérification des nouveaux fichiers effectée avec succès.")
	time.sleep(300) # Se reveille toutes les 5 minutes.
	print(derMtnc)
	print(tmpsAct)
	tmpsActuel = str(time.time())
	point = tmpsActuel.find('.')
	tmpsAct = int(tmpsActuel[0:point])