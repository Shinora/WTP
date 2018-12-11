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
	pos1 = IpPortNoeud.find(":")
    pos1 = pos1+1
    pos2 = len(IpPortNoeud)
    PortNoeud = IpPortNoeud[pos1:pos2]
    pos1 = pos1-1
    IPNoeud = IpPortNoeud[0:pos1]

    ConnectionDemande = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ConnectionDemande.connect((IPNoeud, int(PortNoeud)))
    logs.ajtLogs("Connection avec le noeud établie. demandeListeFichiers() --> echangeListes.py")
    
    msg_a_envoyer = b""
    msg_a_envoyer = "=cmd ListeIntegraleFichiers"
    msg_a_envoyer = msg_a_envoyer.encode()
    # On envoie le message
    ConnectionDemande.send(msg_a_envoyer)
    ListeNoeudsEnc = ConnectionDemande.recv(1024)
    ListeNoeuds = ListeNoeudsEnc.decode()
