#! /usr/bin/python
# -*- coding:utf-8 -*-

import re
import search
import fctsClient
import sys
import json
import struct
import logs
import threading
import config

class Bridge(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.allume = True

	def run(self):
		while self.allume:
			requete = self.getMessage()
			print("Youpi : " + requete)
			if requete[:19] == "=cmd rechercher nom":
				# =cmd rechercher nom SHA256.ext
				sortie = search.rechercheFichierEntiere(requete[20:])
				ipport = sortie[:sortie.find(";")]
				sha = sortie[sortie.find(";")+1:]
				if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', ipport):
					# C'est un IPPort
					# On envoi vers le thread qui télécharge le file
					error += fctsClient.CmdDemandeFichier(ipport[:ipport.find(":")], int(ipport[ipport.find(":")+1:]), sha)
					if error == 0:
						resultat = "=cmd SUCCESS : " + str(config.readConfFile("Path")) + "/HOSTEDFILES/" + sha
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
			elif requete[:15] == "=cmd VPN noeud " and requete.find(" request =cmd DemandeFichier") != -1:
				# =cmd VPN noeud 127.0.0.1:5555 request =cmd DemandeFichier
				ipport = requete[requete.find("=cmd VPN noeud ")+15:requete.find(" request ")]
				resultat = requete[requete.find(" request ")+10:]
			else:
				resultat = "=cmd CommandeInconnue :"+requete+":"
			print(resultat)
			logs.addLogs(resultat)
			self.sendMessage(self.encodeMessage(resultat))

	# Read a message from stdin and decode it.
	def getMessage(self):
		rawLength = sys.stdin.read(4)
		if not rawLength:
			sys.exit(0)
		messageLength = struct.unpack('@I', rawLength)[0]
		message = sys.stdin.read(messageLength)
		print(json.loads(message))
		return json.loads(message)

	# Encode a message for transmission, given its content.
	def encodeMessage(self, messageContent):
		encodedContent = json.dumps(messageContent)
		encodedLength = struct.pack('@I', len(encodedContent))
		print({'length': encodedLength, 'content': encodedContent})
		return {'length': encodedLength, 'content': encodedContent}

	# Send an encoded message to stdout.
	def sendMessage(self, encodedMessage):
		sys.stdout.write(encodedMessage['length'])
		sys.stdout.write(encodedMessage['content'])
		sys.stdout.flush()

	def stop(self):
		self.allume = False
