#! /usr/bin/python
# -*- coding:utf-8 -*-

import time
import autresFonctions
import echangeNoeuds
import echangeFichiers
import re
import search
import fctsClient
import sys
import json
import struct
import logs


# Read a message from stdin and decode it.
def getMessage():
	rawLength = sys.stdin.read(4)
	if len(rawLength) == 0:
		sys.exit(0)
	messageLength = struct.unpack('@I', rawLength)[0]
	message = sys.stdin.read(messageLength)
	print(json.loads(message))
	return json.loads(message)

# Encode a message for transmission, given its content.
def encodeMessage(messageContent):
	encodedContent = json.dumps(messageContent)
	encodedLength = struct.pack('@I', len(encodedContent))
	print({'length': encodedLength, 'content': encodedContent})
	return {'length': encodedLength, 'content': encodedContent}

# Send an encoded message to stdout.
def sendMessage(encodedMessage):
	sys.stdout.write(encodedMessage['length'])
	sys.stdout.write(encodedMessage['content'])
	sys.stdout.flush()

while True:
	requete = getMessage()
	print("Youpi : " + requete)
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
				resultat = "=cmd SUCCESS : " + str(autresFonctions.readConfFile("Path"))[:-1] + "/HOSTEDFILES/" + sha
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
	elif requete[:15] == "=cmd VPN noeud " and requete.find(" commande =cmd DemandeFichier") != -1:
		# =cmd VPN noeud 127.0.0.1:5555 commande =cmd DemandeFichier
		ipport = requete[requete.find("=cmd VPN noeud ")+15:requete.find(" commande ")]
		commande = requete[requete.find(" commande ")+10:]
	else:
		resultat = "=cmd CommandeInconnue :"+requete+":"
	print(resultat)
	logs.ajtLogs(resultat)
	sendMessage(encodeMessage(resultat))
