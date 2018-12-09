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

# On vérifie que les sources sont correctes et pas modifiées
# maj.verifSources()
# Ligne commentée pour le dev, trop pénible
autresFonctions.fillConfFile()
# Créer un fichier qui va lancer les différentes
# instances en fonction de la configuration
cmd = os.popen('python3 maintenance.py', 'r')
print("Bonjour")
fExtW = open(".extinctionWTP", "w")
fExtW.write("ALLUMER")
fExtW.close()

hote = '127.0.0.1'
port = int(input("Port : "))

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(5)
logs.ajtLogs("INFO : WTP a démarré, il ecoute à présent sur le port " + str(port))

serveur_lance = True
clients_connectes = []
while serveur_lance:
    # On va vérifier que de nouveaux clients ne demandent pas à se connecter
    # Pour cela, on écoute la connexion_principale en lecture
    # On attend maximum 50ms
    connexions_demandees, wlist, xlist = select.select([connexion_principale],
        [], [], 0.05)
    
    for connexion in connexions_demandees:
        connexion_avec_client, infos_connexion = connexion.accept()
        # On ajoute le socket connecté à la liste des clients
        clients_connectes.append(connexion_avec_client)
    
    # Maintenant, on écoute la liste des clients connectés
    # Les clients renvoyés par select sont ceux devant être lus (recv)
    # On attend là encore 50ms maximum
    # On enferme l'appel à select.select dans un bloc try
    # En effet, si la liste de clients connectés est vide, une exception
    # Peut être levée
    clients_a_lire = []
    try:
        clients_a_lire, wlist, xlist = select.select(clients_connectes,
                [], [], 0.05)
    except select.error:
        pass
    else:
        # On parcourt la liste des clients à lire
        for client in clients_a_lire:
            # Client est de type socket
            msg_recu = client.recv(1024)
            msg_recu = msg_recu.decode()
            # Maintenant, vérifions la demande du client.
            if msg_recu[:19] == "=cmd DemandeFichier": # Fonction Client OPPÉRATIONNEL
                # =cmd DemandeFichier  nom sha256.ext  ipPort IP:PORT
                # Dirriger vers la fonction UploadFichier()
                # Le noeud distant demande le fichier, donc on lui envoi, Up !
                # On va chercher les deux informations qu'il nous faut :
                # Le nom du fichier (sous forme sha256.ext)
                # L'IP et le port du noeud qui a fait la demande (sous forme IP:PORT)
                pos1 = msg_recu.find(" nom ")
                pos1 = pos1+5
                pos2 = msg_recu.find(" ipPort ")
                nomFichier = msg_recu[pos1:pos2]
                pos2 = pos2+8
                pos3 = len(msg_recu)
                IpPortNoeud = msg_recu[pos2:pos3]
                if BDD.verifFichier(nomFichier):
                    # Le fichier est présent dans la BDD, on peut l'envoyer
                    client.send("=cmd OK".encode())
                    time.sleep(0.5) # Le temps que le noeud distant mette en place son serveur
                    echangeFichiers.UploadFichier(nomFichier, IpPortNoeud)
                else:
                    client.send("=cmd ERROR".encode())
            elif msg_recu[:17] == "=cmd DemandeNoeud": # Fonction Serveur
                # Dirriger vers la fonction EnvoiNoeuds()
                # Le noeud distant a demandé les noeuds, on lui envoi !
                # On trouve le premier port qui peut être attribué
                IpPortNoeud = "127.0.0.1:" + str(autresFonctions.portLibre(5555))
                cmdAEnvoyer = IpPortNoeud # On envoie au demandeur l'adresse à contacter
                cmdAEnvoyer = cmdAEnvoyer.encode()
                client.send(cmdAEnvoyer)
                print("OK !!")
                echangeNoeuds.EnvoiNoeuds(IpPortNoeud)
            elif msg_recu[:25] == "=cmd DemandeListeFichiers":
                # On va récuperer le nom du fichier qui contient la liste
                # Ensuite, on la transmet au noeud distant pour qu'il puisse
                # faire la demande de réception du fichier pour qu'il puisse l'analyser
                fichier = autresFonctions.lsteFichiers()
                client.send(fichier.encode())
                print("Fait.")
            elif msg_recu[:23] == "=cmd DemandeListeNoeuds":
                # On va récuperer le nom du fichier qui contient la liste
                # Ensuite, on la transmet au noeud distant pour qu'il puisse
                # faire la demande de réception du fichier pour qu'il puisse l'analyser
                fichier = autresFonctions.lsteNoeuds()
                client.send(fichier.encode())
                print("Fait.")
            elif msg_recu[:20] == "=cmd DemandePresence": # OPPÉRATIONNEL
                # C'est tout bête, pas besoin de fonction
                # Il suffit de renvoyer la commande informant que l'on est connecté au réseau.
                cmdAEnvoyer = "=cmd Present"
                cmdAEnvoyer = cmdAEnvoyer.encode()
                client.send(cmdAEnvoyer)
                print("Fait.")
            elif msg_recu[:22] == "=cmd rechercherFichier": 
                # =cmd rechercherFichier nom SHA256.ext
                # Renvoie le retour de la fonction, qui elle même retourne une IP+Port ou 0
                # Chercher le nom du fichier
                nomFichier = msg_recu[27:]
                cmdAEnvoyer = str(search.chercherFichier(nomFichier))
                cmdAEnvoyer = cmdAEnvoyer.encode()
                client.send(cmdAEnvoyer)
                print("Fait.")
            else:
                # Oups... Demande non-reconnue...
                if msg_recu != '':
                    print("ERROR : " + msg_recu)
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


print("Fermeture des connexions")
for client in clients_connectes:
    client.close()

connexion_principale.close()
logs.ajtLogs("INFO : WTP s'est correctement arrèté.")