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

hote = "127.0.0.1"
port = int(input("Port : "))


msg_a_envoyer = b""
while msg_a_envoyer != b"fin":
	msg_a_envoyer = input(">>> ")
	if msg_a_envoyer == "=cmd DemandeNoeud":
		connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connexion_avec_serveur.connect((hote, port))
		print("Connexion établie avec le serveur sur le port {}".format(port))
		msg_a_envoyer = msg_a_envoyer.encode()
		connexion_avec_serveur.send(msg_a_envoyer)
		msg_recu = connexion_avec_serveur.recv(1024)
		connexion_avec_serveur.close()
		print(msg_recu.decode())
		echangeNoeuds.DemandeNoeuds(str(msg_recu))
		print("Fait.")
	elif msg_a_envoyer[:19] == "=cmd DemandeFichier": # OPÉRATIONNEL
		# =cmd DemandeFichier  nom sha256.ext  ipPort IP:PORT
		# Dirriger vers la fonction DownloadFichier()
		# On va chercher l'info qu'il nous faut :
		# L'IP et le port du noeud qui va envoyer le fichier (sous forme IP:PORT)
		connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connexion_avec_serveur.connect((hote, port))
		print("Connexion établie avec le serveur sur le port {}".format(port))
		# Il faut trouver un port libre pour que le noeud donneur
		# puisse se connecter à ce noeud sur le bon port
		newIPPort = "127.0.0.1:" + str(autresFonctions.portLibre(5555))
		msg_a_envoyer += " ipPort " + newIPPort
		msg_a_envoyer = msg_a_envoyer.encode()
		connexion_avec_serveur.send(msg_a_envoyer)
		msg_recu = connexion_avec_serveur.recv(1024)
		connexion_avec_serveur.close()
		if msg_recu.decode() == "=cmd OK":
			# Le noeud distant a le fichier que l'on veut
			echangeFichiers.DownloadFichier(newIPPort)
		else:
			# Le noeud distant n'a pas le fichier que l'on veut
			print("Le noeud n'a pas le fichier recherché")
	elif msg_a_envoyer == "=cmd DemandeListeNoeuds":
		connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connexion_avec_serveur.connect((hote, port))
		print("Connexion établie avec le serveur sur le port {}".format(port))
		msg_a_envoyer = msg_a_envoyer.encode()
		connexion_avec_serveur.send(msg_a_envoyer)
		nomFichier = connexion_avec_serveur.recv(1024)
		connexion_avec_serveur.close()
		print(nomFichier.decode())
		print("Fait.")
	elif msg_a_envoyer == "=cmd DemandeListeFichiers":
		connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connexion_avec_serveur.connect((hote, port))
		print("Connexion établie avec le serveur sur le port {}".format(port))
		msg_a_envoyer = msg_a_envoyer.encode()
		connexion_avec_serveur.send(msg_a_envoyer)
		nomFichier = connexion_avec_serveur.recv(1024)
		connexion_avec_serveur.close()
		print(nomFichier.decode())
		print("Fait.")
	print(msg_a_envoyer)