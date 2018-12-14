#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import logs

# Ce fichier doit simplement redémarrer le protocol entier
os.popen("ps aux | grep maintenance.py | grep -v grep |  kill `awk -F \" \" '{ print $2 }'`", 'r')
os.popen("ps aux | grep launcher.py | grep -v grep |  kill `awk -F \" \" '{ print $2 }'`", 'r')
# Et voilà, c'est tout éteint !
os.popen("python3 launcher.py", 'r')
logs.ajtLogs("INFO : WTP a été redémmaré correctement après la mise à jour")
