#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import autresFonctions
import echangeNoeuds
import echangeFichiers
import re
import search
import fctsClient

hostName = ""
hostPort = 8888

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		requete = self.path
		requete = requete[1:]
		while requete.find("%20") != -1:
			requete = requete[:requete.find("%20")] + " " + requete[requete.find("%20")+3:]
		resultat = ""
		# Maintenant, requete est egal à la requete passée en paramètres, avec les espaces
		if requete[:19] == "=cmd rechercher nom":
			# =cmd rechercher nom SHA256.ext
			sortie = search.rechercheFichierEntiere(requete[20:])
			ipport = sortie[:sortie.find(";")]
			sha = sortie[sortie.find(";")+1:]
			if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', ipport):
				# C'est un IPPort
				# On envoi vers la fonction qui télécharge le fichier
				ip = ipport[:ipport.find(":")]
				port = int(ipport[ipport.find(":")+1:])
				error = fctsClient.CmdDemandeFichier(ip, port, sha)
				if error == 0:
					resultat = "=cmd SUCCESS : " + sha
				elif error == 5:
					resultat = "=cmd ERROR NO FILE"
				else:
					resultat = "=cmd ERROR"
			else:
				# C'est une erreur
				print("AHH")
				print(sortie)
				print(ipport)
				resultat = sortie
		else:
			resultat = "=cmd CommandeInconnue :"+requete+":"
		print(resultat)
		resultat = "HTTP/1.0 200 OK\r\nContent-Length: 11\r\nAccess-Control-Allow-Origin: *\r\nCache-Control: no-store\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n"+resultat+"\r\n"
		self.wfile.write(bytes(resultat, "utf-8"))
myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))
autresFonctions.afficherLogo()
try:
	myServer.serve_forever()
except KeyboardInterrupt:
	pass
myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
