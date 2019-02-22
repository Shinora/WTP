#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import select
import sys
import os
import os.path
import logs
import BDD
import autresFonctions
import echangeNoeuds
import echangeFichiers
import time
import maj
import search
import dns
from Crypto import Random
from Crypto.Cipher import AES
import threading
from loader import loader


status = loader("The DNS service start")
status.start()

fExtW = open(".extinctionWTP", "w")
fExtW.write("ALLUMER")
fExtW.close()

host = '127.0.0.1'
port = int(autresFonctions.readConfFile("DNSPort"))

logs.addLogs("INFO : The DNS service has started, he is now listening to the port " + str(port))
cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))

class ClientThread(threading.Thread):
	def __init__(self, ip, port, clientsocket):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsocket = clientsocket

	def run(self): 
		rcvCmd = self.clientsocket.recv(1024)
		rcvCmd = rcvCmd.decode()
		status = loader("Connection with a peer")
		status.start()
		if rcvCmd[:9] == "=cmd DNS ":
			# =cmd DNS ...
			request = rcvCmd[9:]
			if request[:7] == "AddNDD ":
				# =cmd DNS AddNDD sha ******* ndd ******* pass *******
				sha256 = request[11:request.find(" ndd ")]
				ndd = request[request.find(" ndd ")+5:request.find(" pass ")]
				password = request[request.find(" pass ")+6:]
				erreur = dns.ajouterEntree("DNS", ndd, sha256, password)
				if erreur != 0:
					# Une erreur s'est produite et le nom de domaine n'a pas été ajouté
					if erreur == 5:
						# Le nom de domaine ets déjà pris
						sendCmd = "=cmd NDDDejaUtilise"
					else:
						sendCmd = "=cmd ERROR"
				else:
					sendCmd = "=cmd SUCCESS"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
				print(erreur)
			elif request[:9] == "AddDNSExt":
				# =cmd DNS AddDNSExt ipport ******
				erreur = dns.ajouterEntree("DNSExt", request[17:])
				if erreur != 0:
					# Une erreur s'est produite et le noeud DNS n'a pas été ajouté
					if erreur == 5:
						# Le noeud est déjà connu
						sendCmd = "=cmd IPPORTDejaUtilise"
					else:
						sendCmd = "=cmd ERROR"
				else:
					sendCmd = "=cmd SUCCESS"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
				print(erreur)
			elif request[:8] == "modifNDD":
				# =cmd DNS modifNDD ndd ****** adress ****** pass ******
				ndd = request[13:request.find(" adress ")]
				adress = request[request.find(" adress ")+8:request.find(" pass ")]
				password = request[request.find(" pass ")+6:]
				erreur = dns.modifEntree("DNS", adress, ndd, password)
				if erreur > 0:
					if erreur == 5:
						sendCmd = "=cmd MDPInvalide"
					elif erreur == 8:
						sendCmd = "=cmd NDDInconnuCree"
					else:
						sendCmd = "=cmd ERROR"
				else:
					sendCmd = "=cmd SUCCESS"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
				print(erreur)
			elif request[:8] == "supprNDD":
				# =cmd DNS supprNDD ndd ****** pass ******
				ndd = request[22:request.find(" pass ")]
				password = request[request.find(" pass ")+6:]
				erreur = dns.supprEntree("DNS", ndd, password)
				if erreur > 0:
					if erreur == 5:
						sendCmd = "=cmd MDPInvalide"
					else:
						sendCmd = "=cmd ERROR"
				else:
					sendCmd = "=cmd SUCCESS"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
				print(erreur)
			elif request[:9] == "searchSHA":
				# =cmd DNS searchSHA ndd ******
				sortie = str(dns.searchSHA(request[14:]))
				if len(sortie) >= 64:
					sendCmd = sortie
				else:
					if sortie == "INCONNU":
						sendCmd = "=cmd NNDInconnu"
					else:
						sendCmd = "=cmd ERROR"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
			elif request[:11] == "=cmd status":
				# On demande le statut du noeud (Simple, Parser, DNS, VPN, Main)
				sendCmd = "=cmd DNS"
				self.clientsocket.send(sendCmd.encode())
			else:
				sendCmd = "=cmd Inconnu"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
		elif rcvCmd == "=cmd DemandePresence":
			sendCmd = "=cmd Present"
			sendCmd = sendCmd.encode()
			self.clientsocket.send(sendCmd)
		else:
			# Oups... Demande non-reconnue
			# On envoie le port par défaut du noeud
			if rcvCmd != '':
				logs.addLogs("ERROR : Unknown error (serveurDNS.py) : " + str(rcvCmd))
				sendCmd = "=cmd ERROR DefaultPort "+str(autresFonctions.readConfFile("defaultPort"))
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
		status.stop()
		status.join()

try:
	try:
		tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		tcpsock.bind((host,port))
	except OSError as e:
		logs.addLogs("ERROR : In serveurDNS.py : "+str(e))
		logs.addLogs("Stop everything and restart after...")
		fExtW = open(".extinctionWTP", "w")
		fExtW.write("ETEINDRE")
		fExtW.close()
		time.sleep(15)
		logs.addLogs("Try to restart...")
		fExtW = open(".extinctionWTP", "w")
		fExtW.write("ETEINDRE")
		fExtW.close()
	else:
		serveur_lance = True
		status.stop()
		status.join()
		while serveur_lance:
			tcpsock.listen(10)
			(clientsocket, (ip, port)) = tcpsock.accept()
			newthread = ClientThread(ip, port, clientsocket)
			newthread.start()
			# Vérifier si WTP a recu une demande d'extinction
			fExt = open(".extinctionWTP", "r")
			contenu = fExt.read()
			fExt.close()
			if contenu == "ETEINDRE":
				# On doit éteindre WTP.
				serveur_lance = False
			elif contenu != "ALLUMER":
				fExtW = open(".extinctionWTP", "w")
				fExtW.write("ALLUMER")
				fExtW.close()
except KeyboardInterrupt:
	print(" pressed: Shutting down ...")
	print("")
fExtW = open(".extinctionWTP", "w")
fExtW.write("ETEINDRE")
fExtW.close()
logs.addLogs("INFO : The DNS service has been stoped successfully.")
