#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import logs

# Ce fichier doit simplement redémarrer le protocol entier
cmd = os.popen("ps aux | grep maintenance.py | grep -v grep |  kill `awk -F " " '{ print $2 }'`", 'r')
cmd = os.popen("ps aux | grep launcher.py | grep -v grep |  kill `awk -F " " '{ print $2 }'`", 'r')
# Et voilà, c'est tout éteint !
cmd = os.popen("python3 launcher.py", 'r')
logs.ajtLogs("INFO : WTP a été redémmaré correctement après la mise à jour")