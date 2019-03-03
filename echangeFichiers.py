#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import os
import math
import hashlib
import logs
import BDD
import re

 ####################################################
#													#
# Sont ici les fonctions qui permettent d'envoyer	#
# et recevoir des files  présents sur le réseau		#
# Fonctions présetes ici :							#
# UploadFichier(fileName, IppeerPort)				#
# DownloadFichier(IpPortReceveur)					#
#													#
 ####################################################

 # Fonction pour envoyer (upload) un file au receveur
# A besoin en paramètre :
# Du nom du file
# De l'ip suivie du port du Noeud à contacter sous la forme 000.000.000.000:00000

def UploadFichier(fileName, IppeerPort):
	error = 0
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
	if reg.match(IppeerPort): # Si ipport est un ip:port
		pathFichier = "HOSTEDFILES/" + fileName
		#Départager l'IP et le port
		peerIP = IppeerPort[:IppeerPort.find(":")]
		peerPort = int(IppeerPort[IppeerPort.find(":")+1:])
		# Liaison tcp/ip
		c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Connection au receveur
		try:
			c.connect((peerIP, peerPort))
		except socket.error as erreur:
			error += 1
			logs.addLogs("ERROR: Can not connect to the receiver. (UploadFichier()) " + str(erreur))
		else:
			# Connaitre la taille du file en octet
			tailleFichier = os.path.getsize(pathFichier)
			# Envoyer au receveur les informations concernant le file (nom et taille)
			sendCmd = b""
			sendCmd = "=cmd NomFichierUpload " + str(fileName) + " Taille " + str(tailleFichier)
			sendCmd = sendCmd.encode()
			# On envoie le message
			c.send(sendCmd)
			rcvData = c.recv(1024)
			rcvData = rcvData.decode()
			if rcvData == '=cmd GoTransfererFichier':
				#Tout se passe bien, on continue...
				#Maintenant, on vérifie si le file peut être envoyé n une seule foie, ou si il faut le "découper"
				if tailleFichier > 1024:
					#Le file doit être découpé avant d'être envoyé
					fich = open(pathFichier, "rb")
					num = 0
					nbPaquets = math.ceil(tailleFichier/1024)
					deplacementFichier = 0
					while num < nbPaquets:
						fich.seek(deplacementFichier, 0) # on se deplace par rapport au numero de caractere (de 1024 a 1024 octets)
						donnees = fich.read(1024) # Lecture du file en 1024 octets
						c.send(donnees) # Envoi du file par paquet de 1024 octets
						num = num + 1
						deplacementFichier = deplacementFichier + 1024
				else:
					#Le file peut être envoyé en une seule fois
					fich = open(pathFichier, "rb")
					donnees = fich.read() # Lecture du file
					c.send(donnees) # Envoi du file
			else:
				logs.addLogs("ERROR: Receiver left upload before start. (UploadFichier())")
				# Vérifier que le file a été correctement uploadé
				error += 1
			c.close()
	else:
		error += 1
	return error


# Fonction qui permet au noeud d'enregistrer le file qu'un noeud lui envoi
# A besoin en paramètre :
# De l'ip suivie du port du receveur sous la forme 000.000.000.000:00000 (localhost = 127.0.0.1)

def DownloadFichier(IpPortReceveur):
	# Vérifier si le dossier HOSTEDFILES existe, sinon le créer
	error = 0
	reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})$")
	if reg.match(IpPortReceveur): # Si ipport est un ip:port
		try:
			os.makedirs("HOSTEDFILES")
		except OSError:
			if not os.path.isdir("HOSTEDFILES"):
				raise
		#Départager l'IP et le port
		IPServ = IpPortReceveur[:IpPortReceveur.find(":")]
		PortServ = int(IpPortReceveur[IpPortReceveur.find(":")+1:])
		# Liaison tcp/ip
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Liaison adresse/port
		try:
			s.bind((IPServ, PortServ))
		except(socket.error):
			logs.addLogs("ERROR : Port already used. (DownloadFichier())")
			error += 1
		else:
			# Receveur en écoute
			s.listen(5)
			conn, addr = s.accept()
			logs.addLogs("Connected peer. (DownloadFichier())")
			cmdRecu = conn.recv(1024) # On récupère les informations que le noeud a envoyé
			cmdRecu = cmdRecu.decode()
			# Il faut maintenant "découper" la request, pour pouvoir prendre les informations utiles
			cmdDemande = cmdRecu[:21]
			if cmdDemande == '=cmd NomFichierUpload':
				# C'est bon, on continue
				cmdRecu = cmdRecu.replace("=cmd NomFichierUpload ", "")
				cmd = cmdRecu.split(' Taille ')
				cmdFSize = int(cmd[1])
				# Et voilà, on a :
				# Le nom du file : cmd[0]
				# La taille du file : cmdFSize
				# On envoi un paquet pour prévenir le noeud que l'on est pret
				sendCmd = b""
				sendCmd = "=cmd GoTransfererFichier"
				sendCmd = sendCmd.encode()
				conn.send(sendCmd)
				#On vide le file (on ne sait jamais)
				fileName = cmd[0]
				pathFichier = "HOSTEDFILES/" + fileName
				f = open(pathFichier, "w")
				f.write("")
				f.close()
				# On ouvre le file vide en mode append et binaire
				# (donc les données n'ont pas besoin d'êtres converties et elles seront ajoutées à la fin du file)
				f = open(pathFichier, "ab")
				if cmdFSize > 1024:
					# Le file va arriver en morceaux
					nbPaquetsCalcule = math.ceil(cmdFSize/1024)
					nbPaquetsRecu = 0
					while nbPaquetsCalcule > nbPaquetsRecu:
						recu = ""
						recu = conn.recv(1024)
						if not recu :
							break
						f.write(recu)
						nbPaquetsRecu = nbPaquetsRecu+1
				else:
					# Le file va arriver d'un seul coup
					recu = ""
					recu = conn.recv(1024)
					f.write(recu)
				f.close()
				# Maintenant, il faut vérifier que le ficher a le meme SHA256
				file = open(pathFichier, "r")
				contenu = file.read()
				file.close()
				hashFichier = hashlib.sha256(contenu.encode('utf-8')).hexdigest()
				if hashFichier == fileName[:fileName.find('.')]:
					# Le transfert s'est bien passé
					# On envoi un message positif au noeud
					sendCmd = b""
					sendCmd = "=cmd Upload succes"
					sendCmd = sendCmd.encode()
					conn.send(sendCmd)
					# Ajouter le file à la BDD
					BDD.ajouterEntree("Fichiers", fileName)
				else:
					# Ah, il y a un problème
					logs.addLogs("ERROR: The Hash of the file is different. (DownloadFichier())")
					#Supprimer le file
					os.remove(pathFichier)
					error += 1
			else:
				# Ah... La demande ne peut être gérée par cette fonction...
				logs.addLogs("ERROR: Unmanaged command : " + str(cmdDemande) + ". (DownloadFichier())")
				sendCmd = b""
				sendCmd = "=cmd TransfertRefuse"
				sendCmd = sendCmd.encode()
				conn.send(sendCmd)
				error += 1
			conn.close()
			s.close()
	else:
		error += 1
	return error
