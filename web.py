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
hote = "127.0.0.1"
port = 5555

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		requete = self.path
		requete = requete[1:]
		while requete.find("%20") != -1:
			requete = requete[:requete.find("%20")] + " " + requete[requete.find("%20")+3:]
		resultat = ""
		# Maintenant, requete est egal à la requete passée en paramètres, avec les espaces
		if requete == "=cmd DemandeNoeud":
			fctsClient.CmdDemandeNoeud(hote, port)
			resultat = "=cmd SUCCESS"
		elif requete[:19] == "=cmd DemandeFichier":
			# =cmd DemandeFichier nom sha256.ext
			fctsClient.CmdDemandeFichier(hote, port, requete[24:])
			resultat = "=cmd SUCCESS"
		elif requete == "=cmd DemandeListeNoeuds":
			fctsClient.CmdDemandeListeNoeuds(hote, port)
			resultat = "=cmd SUCCESS"
		elif requete == "=cmd DemandeListeFichiers":
			fctsClient.CmdDemandeListeFichiers(hote, port)
			resultat = "=cmd SUCCESS"
		elif requete[:19] == "=cmd rechercher nom":
			# =cmd rechercher nom SHA256.ext
			sortie = search.rechercheFichierEntiere(requete[20:])
			ipport = sortie[:sortie.find(";")]
			sha = sortie[sortie.find(";")+1:]
			if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', ipport):
				# C'est un IPPort
				# On envoi vers la fonction qui télécharge le fichier
				ip = ipport[:ipport.find(":")]
				port = int(ipport[ipport.find(":")+1:])
				fctsClient.CmdDemandeFichier(hote, port, sha)
				resultat = "=cmd SUCCESS"
			else:
				# C'est une erreur
				print("AHH")
				print(sortie)
				print(ipport)
				resultat = sortie
		else:
			resultat = "=cmd CommandeInconnue"
		self.wfile.write(bytes(resultat, "utf-8"))
myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))
try:
	myServer.serve_forever()
except KeyboardInterrupt:
	pass
myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
