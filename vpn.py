#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import os
import os.path
import logs
import autresFonctions
import search
import fctsClient
from Crypto import Random
from Crypto.Cipher import AES
from loader import loader
import threading
import config

# Toutes les fonctions ici permettent de créer une sorte de VPN au sein du réseau
# Une requete passe alors par un autre noeud avant d'aller chez le destinataire


class ClientThread(threading.Thread):
	def __init__(self, ip, port, clientsocket):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsocket = clientsocket

	def run(self):
		status = loader("Connection with a peer")
		status.start()
		rcvCmd = self.clientsocket.recv(1024)
		rcvCmd = rcvCmd.decode()
		if rcvCmd[:15] == "=cmd VPN noeud ":
			# =cmd VPN noeud 127.0.0.1:5555 request =cmd DemandeFichier
			ipport = rcvCmd[15:rcvCmd.find(" request ")]
			request = rcvCmd[rcvCmd.find(" request ")+10:]
			ip = ipport[:ipport.find(":")]
			port = ipport[ipport.find(":")+1:]
			if request[:19] == "=cmd DemandeFichier":
				fctsClient.CmdDemandeFichier(ip, port, request[24:])
				# Manque du code pour transmettre les infos au noeud qui les demandait
				sendCmd = "=cmd TravailFini"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
			elif request[:17] == "=cmd DemandeNoeud":
				fctsClient.CmdDemandeNoeud(ip, port)
				# Manque du code pour transmettre les infos au noeud qui les demandait
				sendCmd = "=cmd TravailFini"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
			elif request[:28] == "=cmd DemandeListeFichiersExt":
				fctsClient.CmdDemandeListeFichiers(ip, port, 1)
				# Manque du code pour transmettre les infos au noeud qui les demandait
				sendCmd = "=cmd TravailFini"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
			elif request[:25] == "=cmd DemandeListeFichiers":
				fctsClient.CmdDemandeListeFichiers(ip, port)
				# Manque du code pour transmettre les infos au noeud qui les demandait
				sendCmd = "=cmd TravailFini"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
			elif request[:23] == "=cmd DemandeListeNoeuds":
				fctsClient.CmdDemandeListeNoeuds(ip, port)
				# Manque du code pour transmettre les infos au noeud qui les demandait
				sendCmd = "=cmd TravailFini"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
			elif request[:22] == "=cmd rechercher":
				# =cmd rechercher nom ******
				search.rechercheFichierEntiere(request[20:])
				# Manque du code pour transmettre les infos au noeud qui les demandait
				sendCmd = "=cmd TravailFini"
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
			elif request[:11] == "=cmd status":
				# On demande le statut du noeud (Simple, Parser, DNS, VPN, Main)
				sendCmd = "=cmd VPN"
				self.clientsocket.send(sendCmd.encode())
			else:
				logs.addLogs("ERROR : Unknown request (vpn.py) : " + str(request))
		else:
			# Oups... Demande non-reconnue
			# On envoie le port par défaut du noeud
			if rcvCmd != '':
				logs.addLogs("ERROR : Unknown request (vpn.py) : " + str(rcvCmd))
				sendCmd = "=cmd ERROR DefaultPort "+str(config.readConfFile("defaultPort"))
				sendCmd = sendCmd.encode()
				self.clientsocket.send(sendCmd)
		status.stop()
		status.join()


class ServVPN(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.serveur_lance = True

	def run(self):
		status = loader("The DNS service start")
		status.start()
		host = '127.0.0.1'
		port = int(config.readConfFile("VPNPort"))
		logs.addLogs("INFO : The VPN service has started, he is now listening to the port " + str(port))
		try:
			try:
				tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				tcpsock.bind((host,port))
				tcpsock.settimeout(5)
			except OSError as e:
				logs.addLogs("ERROR : In vpn.py : "+str(e))
				logs.addLogs("INFO : Stop everything and restart after...")
				os.popen("python3 reload.py", 'r')
			else:
				logs.addLogs("INFO : The VPN service has started, he is now listening to the port " + str(port))
				status.stop()
				status.join()
				while self.serveur_lance:
					try:
						tcpsock.listen(10)
						(clientsocket, (ip, port)) = tcpsock.accept()
					except socket.timeout:
						pass
					else:
						newthread = ClientThread(ip, port, clientsocket)
						newthread.start()
		except KeyboardInterrupt:
			print(" pressed: Shutting down ...")
			print("")
		logs.addLogs("INFO : WTP service has been stoped successfully.")

	def stop(self):
		self.serveur_lance = False
