#!/usr/bin/python
# -*-coding:Utf-8 -*

import socket
import select
import logs
import BDD

def demandeListeFichiers(IpPortNoeud):
	# Fonction qui demande l'intégralité de la liste de fichiers que contient le noeud.
	# Le noeud va chercher dans sa BDD, et faire un fichier temporel qui contiendra le nom des fichiers.
	# Il va l'envoyer, puis cette fonction va le rencevoir, l'avaniser puis l'envoyer dans la BDD
	ip = IpPortNoeud[:IpPortNoeud.find(":")]
	port = IpPortNoeud[IpPortNoeud.find(":")+1:]
	error = 0
	connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
	if str(connexion_avec_serveur) == "=cmd ERROR":
		error += 1
	else:
		logs.ajtLogs("Connection avec le noeud établie. demandeListeFichiers() --> echangeListes.py")
		msg_a_envoyer = b""
		msg_a_envoyer = "=cmd ListeIntegraleFichiers"
		msg_a_envoyer = msg_a_envoyer.encode()
		# On envoie le message
		ConnectionDemande.send(msg_a_envoyer)
		ListeNoeudsEnc = ConnectionDemande.recv(1024)
		ListeNoeuds = ListeNoeudsEnc.decode()
	return error
