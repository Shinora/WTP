#!/usr/bin/python
# -*-coding:Utf-8 -*

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
import fctsMntc
import search

hote = "127.0.0.1"
port = int(input("Port : "))


msg_a_envoyer = b""
importantCMD = ""
while msg_a_envoyer != b"fin":
	if importantCMD == "":
		msg_a_envoyer = input(">>> ")
	else:
		msg_a_envoyer = importantCMD
		importantCMD = ""
	if msg_a_envoyer == "=cmd DemandeNoeud":
		CmdDemandeNoeud(hote, port)
	elif msg_a_envoyer[:19] == "=cmd DemandeFichier":
		# =cmd DemandeFichier  nom sha256.ext
		CmdDemandeFichier(hote, port, msg_a_envoyer[25:])
	elif msg_a_envoyer == "=cmd DemandeListeNoeuds":
		CmdDemandeListeNoeuds(hote, port)
	elif msg_a_envoyer == "=cmd DemandeListeFichiers":
		CmdDemandeListeFichiers(hote, port)
	elif msg_a_envoyer[:18] == "=cmd chercher nom ":
		# =cmd chercher nom SHA256.ext
		CmdRechercherNom(hote, port, msg_a_envoyer[18:])

def CmdDemandeNoeud(ip, port):
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	print("Connexion établie avec le serveur sur le port {}".format(port))
	commande = "=cmd DemandeNoeud"
	commande = commande.encode()
	connexion_avec_serveur.send(commande)
	msg_recu = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()
	print(msg_recu.decode())
	echangeNoeuds.DemandeNoeuds(str(msg_recu))
	print("Fait.")

def CmdDemandeFichier(ip, port, fichier, special = "non"):
	# =cmd DemandeFichier  nom sha256.ext  ipPort IP:PORT
	# Dirriger vers la fonction DownloadFichier()
	# On va chercher l'info qu'il nous faut :
	# L'IP et le port du noeud qui va envoyer le fichier (sous forme IP:PORT)
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	print("Connexion établie avec le serveur sur le port {}".format(port))
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
	print("Connexion établie avec le serveur sur le port {}".format(port))
	msg_a_envoyer = msg_a_envoyer.encode()
	connexion_avec_serveur.send(msg_a_envoyer)
	nomFichier = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()
	CmdDemandeFichier(ip, port, nomFichier.decode(), "noeuds")
	print("Fait.")

def CmdDemandeListeFichiers(ip, port, ext = 0):
	if ext == 1:
		msg_a_envoyer = "=cmd DemandeListeFichiersExt"
	else:
		msg_a_envoyer = "=cmd DemandeListeFichiers"
	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((ip, port))
	print("Connexion établie avec le serveur sur le port {}".format(port))
	msg_a_envoyer = msg_a_envoyer.encode()
	connexion_avec_serveur.send(msg_a_envoyer)
	nomFichier = connexion_avec_serveur.recv(1024)
	connexion_avec_serveur.close()
	CmdDemandeFichier(ip, port, nomFichier.decode(), "fichiers")
	print("Fait.")

def CmdRechercherNom(ip, port, nomFichier): # En cours...
	# Chercher le nom du fichier
	print("Go chercher")
	search.searchFile(nomFichier)
	print("Fait.")
