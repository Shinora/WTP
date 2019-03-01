#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import logs
import time
import platform

# Ce fichier doit simplement redémarrer le protocol entier
fExtW = open(".extinctionWTP", "w")
fExtW.write("ETEINDRE")
fExtW.close()
time.sleep(10)
# Et voilà, c'est tout éteint !

# On l'allume en fonction de l'OS
if platform.system() == "Linux":
	os.popen("python3 launcher.py", 'r')
	logs.addLogs("INFO : WTP has been restart after the update.")
elif platform.system() == "Windows":
	# PAS TESTÉ (Ne fonctionne probablement pas)
	os.popen("python3 launcher.py", 'r')
	logs.addLogs("INFO : WTP has been restart after the update.")
elif platform.system() == "Darwin":
	# PAS TESTÉ (Ne fonctionne probablement pas)
	os.popen("python3 launcher.py", 'r')
	logs.addLogs("INFO : WTP has been restart after the update.")
else:
	logs.addLogs("ERROR : Can't' restart WTP because the operating system is unknown")

lance = True
while lance:
	time.sleep(15)
	fExtW = open(".extinctionWTP", "r")
	contenu = fExtW.read()
	fExtW.close()
	if contenu != "ETEINDRE":
		lance = False
