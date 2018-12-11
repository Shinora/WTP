#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import sys
import os
import math
import hashlib
import logs
import BDD
import autresFonctions
from Crypto import Random

 ####################################################
#                          #
# Sont ici les fonctions qui permettent d'envoyer    #
# et recevoir des fichiers  présents sur le réseau   #
# Fonctions présetes ici :                           #
# UploadFichier(nomFichier, IpPortNoeud)             #
# DownloadFichier(IpPortReceveur)                    #
#                                                    #
 ####################################################

 # Fonction pour envoyer (upload) un fichier au receveur
# A besoin en paramètre :
# Du nom du fichier
# De l'ip suivie du port du Noeud à contacter sous la forme 000.000.000.000:00000

def UploadFichier(nomFichier, IpPortNoeud):
    cheminFichier = "HOSTEDFILES/" + nomFichier
    #Départager l'IP et le port
    pos1 = IpPortNoeud.find(":")
    pos1 = pos1+1
    pos2 = len(IpPortNoeud)
    PortNoeud = int(IpPortNoeud[pos1:pos2])
    pos1 = pos1-1
    IPNoeud = IpPortNoeud[0:pos1]
    # Liaison tcp/ip
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connection au receveur
    try:
        c.connect((IPNoeud, PortNoeud))
    except socket.error as erreur:
        logs.ajtLogs("ERREUR : Connection au receveur impossible. UploadFichier() --> echangeFichiers.py")
        print(erreur)
        print("IP : " + str(IPNoeud))
        print("Port : " + str(PortNoeud))
        sys.exit()
    # Connaitre la taille du fichier en octet
    tailleFichier = os.path.getsize(cheminFichier)
    # Envoyer au receveur les informations concernant le fichier (nom et taille)
    cmdAEnvoyer = b""
    cmdAEnvoyer = "=cmd NomFichierUpload " + str(nomFichier) + " Taille " + str(tailleFichier)
    cmdAEnvoyer = cmdAEnvoyer.encode()
    # On envoie le message
    c.send(cmdAEnvoyer)
    dataRecu = c.recv(1024)
    dataRecu = dataRecu.decode()
    if dataRecu == '=cmd GoTransfererFichier':
        #Tout se passe bien, on continue...
        #Maintenant, on vérifie si le fichier peut être envoyé n une seule foie, ou si il faut le "découper"
        if tailleFichier > 1024:
            #Le fichier doit être découpé avant d'être envoyé
            fich = open(cheminFichier, "rb")
            num = 0
            nbPaquets = math.ceil(tailleFichier/1024)
            deplacementFichier = 0
            while num < nbPaquets:
                fich.seek(deplacementFichier, 0) # on se deplace par rapport au numero de caractere (de 1024 a 1024 octets)
                donnees = fich.read(1024) # Lecture du fichier en 1024 octets   
                c.send(donnees) # Envoi du fichier par paquet de 1024 octets
                num = num + 1
                deplacementFichier = deplacementFichier+1024   
        else:
            #Le fichier peut être envoyé en une seule fois
            fich = open(cheminFichier, "rb")
            donnees = fich.read() # Lecture du fichier
            c.send(donnees) # Envoi du fichier
    else:
        logs.ajtLogs("ERREUR : Receveur a quitté l'upload avant le commencement. UploadFichier() --> echangeFichiers.py")
        # Vérifier que le fichier a été correctement uploadé
    c.close()


# Fonction qui permet au noeud d'enregistrer le fichier qu'un noeud lui envoi
# A besoin en paramètre :
# De l'ip suivie du port du receveur sous la forme 000.000.000.000:00000 (localhost = 127.0.0.1)

def DownloadFichier(IpPortReceveur):
    # Vérifier si le dossier HOSTEDFILES existe, sinon le créer
    try: 
        os.makedirs("HOSTEDFILES")
    except OSError:
        if not os.path.isdir("HOSTEDFILES"):
            raise
    #Départager l'IP et le port
    pos1 = IpPortReceveur.find(":")
    pos1 = pos1+1
    pos2 = len(IpPortReceveur)
    PortServ = int(IpPortReceveur[pos1:pos2])
    pos1 = pos1-1
    IPServ = IpPortReceveur[0:pos1]
    # Liaison tcp/ip
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Liaison adresse/port
    try:
        s.bind((IPServ, PortServ))
    except(socket.error):
        logs.ajtLogs("ERREUR : Port déjà utilisé. DownloadFichier --> echangeFichiers.py")
        sys.exit()
    # Receveur en écoute
    s.listen(5)
    conn, addr = s.accept()
    logs.ajtLogs("Noeud connecté. DownloadFichier --> echangeFichiers.py")
    cmdRecu = conn.recv(1024) # On récupère les informations que le noeud a envoyé
    cmdRecu = cmdRecu.decode()
    # Il faut maintenant "découper" la commande, pour pouvoir prendre les informations utiles
    cmdDemande = cmdRecu[:21]
    if cmdDemande == '=cmd NomFichierUpload':
        # C'est bon, on continue
        cmdRecu = cmdRecu.replace("=cmd NomFichierUpload ", "")
        cmd = cmdRecu.split(' Taille ')
        cmdFSize = int(cmd[1])
        # Et voilà, on a : 
        # Le nom du fichier : cmd[0]
        # La taille du fichier : cmdFSize
        # On envoi un paquet pour prévenir le noeud que l'on est pret
        cmdAEnvoyer = b""
        cmdAEnvoyer = "=cmd GoTransfererFichier"
        cmdAEnvoyer = cmdAEnvoyer.encode()
        conn.send(cmdAEnvoyer)
        #On vide le fichier (on ne sait jamais)
        nomFichier = cmd[0]
        cheminFichier = "HOSTEDFILES/" + nomFichier
        f = open(cheminFichier, "w")
        f.write("")
        f.close()
        # On ouvre le fichier vide en mode append et binaire 
        # (donc les données n'ont pas besoin d'êtres converties et elles seront ajoutées à la fin du fichier)
        f = open(cheminFichier, "ab")
        if cmdFSize > 1024:
            # Le fichier va arriver en morceaux
            nbPaquetsCalcule = math.ceil(cmdFSize/1024)
            nbPaquetsRecu = 0
            while nbPaquetsCalcule > nbPaquetsRecu:
                recu = ""
                recu = conn.recv(1024)
                if not recu : break
                f.write(recu)
                nbPaquetsRecu = nbPaquetsRecu+1
        else:
            # Le fichier va arriver d'un seul coup
            recu = ""
            recu = conn.recv(1024)
            f.write(recu)
        f.close()
        # Maintenant, il faut vérifier que le ficher a le meme SHA256
        fichier = open(cheminFichier, "r")
        contenu = fichier.read()
        fichier.close()
        hashFichier = hashlib.sha256(contenu.encode('utf-8')).hexdigest()
        if hashFichier == nomFichier[:nomFichier.find('.')]:
            # Le transfert s'est bien passé
            # On envoi un message positif au noeud
            cmdAEnvoyer = b""
            cmdAEnvoyer = "=cmd Upload succes"
            cmdAEnvoyer = cmdAEnvoyer.encode()
            conn.send(cmdAEnvoyer)
            # Ajouter le fichier à la BDD
            BDD.ajouterEntree("Fichiers", nomFichier)
        else:
            # Ah, il y a un problème
            logs.ajtLogs("ERREUR : Le Hash du fichier différent. DownloadFichier --> echangeFichiers.py")
            #Supprimer le fichier
            os.remove(cheminFichier)
    else:
        # Ah... La demande ne peut être gérée par cette fonction...
        logs.ajtLogs("ERREUR : Commande non gérée : " + str(cmdDemande) + ". DownloadFichier --> echangeFichiers.py")
        cmdAEnvoyer = b""
        cmdAEnvoyer = "=cmd TransfertRefuse"
        cmdAEnvoyer = cmdAEnvoyer.encode()
        conn.send(cmdAEnvoyer)
    conn.close()
    s.close()

def demandeFichier(nomFichier, IpPort):
    # Fonction qui demande au noeud s'il connait un fichier,
    # Et retourne l'IPPORT du noeud qui a le fichier (retourne le deuxième argument si c'est lui)
    ipPortNoeud = autresFonctions.connaitreIP()
    print("EN COURS...")
    return ipPortNoeud
