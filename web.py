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
		if requete[:17] == "=cmd DemandeNoeud":
			# =cmd DemandeNoeud ipport ******
			if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', requete[requete.find(" ipport")+8:]):
				ip = requete[requete.find(" ipport ")+8:requete.find(":")]
				port = int(requete[requete.find(":")+1:])
				fctsClient.CmdDemandeNoeud(ip, port)
				resultat = "=cmd SUCCESS"
			else:
				resultat = "=cmd ERROR MISS IPPort"
		elif requete[:19] == "=cmd DemandeFichier":
			# =cmd DemandeFichier nom sha256.ext ipport ******
			if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', requete[requete.find(" ipport")+8:]):
				ip = requete[requete.find(" ipport ")+8:requete.find(":")]
				port = int(requete[requete.find(":")+1:])
				fctsClient.CmdDemandeFichier(ip, port, requete[24:])
				resultat = "=cmd SUCCESS"
			else:
				resultat = "=cmd ERROR MISS IPPort"
		elif requete[:23] == "=cmd DemandeListeNoeuds":
			# =cmd DemandeListeNoeuds ipport ******
			if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', requete[requete.find(" ipport")+8:]):
				ip = requete[requete.find(" ipport ")+8:requete.find(":")]
				port = int(requete[requete.find(":")+1:])
				fctsClient.CmdDemandeListeNoeuds(ip, port)
				resultat = "=cmd SUCCESS"
			else:
				resultat = "=cmd ERROR MISS IPPort"
		elif requete[:25] == "=cmd DemandeListeFichiers":
			# =cmd DemandeListeFichiers ipport ******
			if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', requete[requete.find(" ipport")+8:]):
				ip = requete[requete.find(" ipport ")+8:requete.find(":")]
				port = int(requete[requete.find(":")+1:])
				fctsClient.CmdDemandeListeFichiers(ip, port)
				resultat = "=cmd SUCCESS"
			else:
				resultat = "=cmd ERROR MISS IPPort"
		elif requete[:19] == "=cmd rechercher nom":
			# =cmd rechercher nom SHA256.ext
			ip = requete[requete.find(" ipport ")+8:requete.find(":")]
			port = int(requete[requete.find(":"):])
			sortie = search.rechercheFichierEntiere(requete[20:])
			ipport = sortie[:sortie.find(";")]
			sha = sortie[sortie.find(";")+1:]
			if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', ipport):
				# C'est un IPPort
				# On envoi vers la fonction qui télécharge le fichier
				ip = ipport[:ipport.find(":")]
				port = int(ipport[ipport.find(":")+1:])
				fctsClient.CmdDemandeFichier(ip, port, sha)
				resultat = "=cmd SUCCESS"
			else:
				# C'est une erreur
				print("AHH")
				print(sortie)
				print(ipport)
				resultat = sortie
		else:
			resultat = "=cmd CommandeInconnue :"+requete+":"
		self.wfile.write(bytes(resultat, "utf-8"))
myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))
try:
	myServer.serve_forever()
except KeyboardInterrupt:
	pass
myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
