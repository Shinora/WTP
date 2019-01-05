#!/usr/bin/python
# -*-coding:Utf-8 -*

import socket
import autresFonctions
import echangeNoeuds
import echangeFichiers
import re
import search
import logs

def CmdDemandeNoeud(ip, port):
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	logs.ajtLogs("Connexion établie avec le serveur sur le port {}".format(port))
	commande = "=cmd DemandeNoeud"
	commande = commande.encode()
	connexion_avec_serveur.send(commande)
	msg_recu = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()
	echangeNoeuds.DemandeNoeuds(str(msg_recu))

def CmdDemandeFichier(ip, port, fichier, special = "non"):
	# =cmd DemandeFichier  nom sha256.ext  ipPort IP:PORT
	# Dirriger vers la fonction DownloadFichier()
	# On va chercher l'info qu'il nous faut :
	# L'IP et le port du noeud qui va envoyer le fichier (sous forme IP:PORT)
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	logs.ajtLogs("Connexion établie avec le serveur sur le port {}".format(port))
	# Il faut trouver un port libre pour que le noeud donneur
	# puisse se connecter à ce noeud sur le bon port
	newIPPort = str(autresFonctions.connaitreIP()) + str(autresFonctions.portLibre(int(autresFonctions.readConfFile("Port Min"))))
	msg_a_envoyer = "=cmd DemandeFichier  nom " + fichier
	msg_a_envoyer += " ipPort " + newIPPort
	msg_a_envoyer = msg_a_envoyer.encode()
	connexion_avec_serveur.send(msg_a_envoyer)
	msg_recu = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()
	if msg_recu.decode() == "=cmd OK":
		# Le noeud distant a le fichier que l'on veut
		echangeFichiers.DownloadFichier(newIPPort)
		if special == "noeuds":
			# C'est un fichier qui contient une liste de noeuds
			# Récuperer le nom du fichier
			nomFichier = msg_a_envoyer[msg_a_envoyer.find(" nom ")+5:msg_a_envoyer.find(" ipPort ")]
			autresFonctions.lireListeNoeuds(nomFichier)
		if special == "fichiers":
			# C'est un fichier qui contient une liste de fichiers
			# Récuperer le nom du fichier
			nomFichier = msg_a_envoyer[msg_a_envoyer.find(" nom ")+5:msg_a_envoyer.find(" ipPort ")]
			autresFonctions.lireListeFichiers(nomFichier)
	else:
		# Le noeud distant n'a pas le fichier que l'on veut
		print("Le noeud n'a pas le fichier recherché")

def CmdDemandeListeNoeuds(ip, port):
	msg_a_envoyer = "=cmd DemandeListeNoeuds"
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	logs.ajtLogs("Connexion établie avec le serveur sur le port {}".format(port))
	msg_a_envoyer = msg_a_envoyer.encode()
	connexion_avec_serveur.send(msg_a_envoyer)
	nomFichier = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()
	CmdDemandeFichier(ip, port, nomFichier.decode(), "noeuds")

def CmdDemandeListeFichiers(ip, port, ext = 0):
	if ext == 1:
		msg_a_envoyer = "=cmd DemandeListeFichiersExt"
	else:
		msg_a_envoyer = "=cmd DemandeListeFichiers"
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	logs.ajtLogs("Connexion établie avec le serveur sur le port {}".format(port))
	msg_a_envoyer = msg_a_envoyer.encode()
	connexion_avec_serveur.send(msg_a_envoyer)
	nomFichier = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()
	CmdDemandeFichier(ip, port, nomFichier.decode(), "fichiers")

def VPN(demande, ipPortVPN, ipPortExt):
	ip = ipPortVPN[:ipPortVPN.find(":")]
	port = ipPortVPN[ipPortVPN.find(":")+1:]
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	logs.ajtLogs("Connexion établie avec le VPN sur le port {}".format(port))
	# =cmd VPN noeud 127.0.0.1:5555 commande =cmd DemandeFichier
	commande = "=cmd VPN noeud " + ipPortExt + " commande " + demande
	commande = commande.encode()
	connexion_avec_serveur.send(commande)
	print(connexion_avec_serveur.recv(1024))
	connexion_avec_serveur.close()
	# Maintenant que l'on a demandé au VPN d'executer la demande, il faut recuperer les donnnées
	# Pour cela, il faut analyser la commande initiale
	if commande[:19] == "=cmd DemandeFichier":
		# =cmd DemandeFichier nom sha256.ext
		CmdDemandeFichier(ip, port, commande[24:])
	elif commande[:17] == "=cmd DemandeNoeud":
		CmdDemandeNoeud(hote, port)
	elif commande[:28] == "=cmd DemandeListeFichiersExt":
		CmdDemandeListeFichiers(ip, port, 1)
	elif commande[:25] == "=cmd DemandeListeFichiers":
		CmdDemandeListeFichiers(ip, port)
	elif commande[:23] == "=cmd DemandeListeNoeuds":
		CmdDemandeListeNoeuds(hote, port)
	elif commande[:22] == "=cmd rechercher":
		# =cmd rechercher nom SHA256.ext
		search.rechercheFichierEntiere(msg_a_envoyer[20:])
	else:
		logs.ajtLogs("ERREUR : Commande inconnue (VPN() in fctsClient.py) : " + str(commande))
