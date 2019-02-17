#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import logs
import time

# Ce fichier doit simplement redémarrer le protocol entier
fExtW = open(".extinctionWTP", "w")
fExtW.write("ETEINDRE")
fExtW.close()
# Et voilà, c'est tout éteint !
os.popen("python3 launcher.py", 'r')
logs.addLogs("INFO : WTP has been restart after the update.")

lance = True
while lance:
	time.sleep(15)
	fExtW = open(".extinctionWTP", "r")
	contenu = fExtW.read()
	fExtW.close()
	if contenu == "ETEINDRE":
		lance = False