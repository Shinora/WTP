#!/usr/bin/python
# -*-coding:Utf-8 -*

import socket
import select
import logs
import BDD
import re
from Crypto import Random
from Crypto.Cipher import AES

 ####################################################
#                                                    #
# Sont ici les fonctions qui permettent de s'envoyer #
# des listes de noeuds présents sur le réseau        #
# Fonctions présetes ici :                           #
# DemandeNoeuds(IpPortNoeud)                         #
# EnvoiNoeuds(hote, port)                            #
#                                                    #
 ####################################################


########################
#
# Ce code va permettre au noeud de demander de nouveaux 
# noeuds à un autre Noeud (Super-Noeud (SN) ou Noeud "simple")
# Il va envoyer une requete qui demande 48 noeuds. 
# (Le minimum d'IP+Ports qui peuvent tenir dans 1024 octets)
# Puis il va analiser la réponse du SN
# Et pour terminer, il va mettre le tout dans sa BDD
#
#########################

def DemandeNoeuds(IpPortNoeud):
    #Le paramètre à donner est l'ip suivie du port du Noeud à contacter sous la forme 000.000.000.000:00000
    #Départager l'IP et le port
    error = 0
    reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
    if reg.match(IpPortNoeud): # Si ipport est un ip:port
        ip = IpPortNoeud[:IpPortNoeud.find(":")]
        port = IpPortNoeud[IpPortNoeud.find(":")+1:]
        connexion_avec_serveur = autresFonctions.connectionClient(ip, port)
        cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
        if str(connexion_avec_serveur) == "=cmd ERROR":
            error += 1
        else:
            logs.ajtLogs("INFO : Connection with peer etablished (DemandeNoeuds())")
            msg_a_envoyer = b""
            msg_a_envoyer = "=cmd DonListeNoeuds 48"
            msg_a_envoyer = msg_a_envoyer.encode()
            # On envoie le message
            ConnectionDemande.send(msg_a_envoyer)
            ListeNoeudsEnc = ConnectionDemande.recv(1024)
            ListeNoeuds = ListeNoeudsEnc.decode()
            #Les 48 IP+port sont sous la forme 000.000.000.000:00000 et sont séparés par une virgule
            ##################################################
            ##  IL FAUT VERIFIER SI CE SONT BIEN DES IP ET  ##
            ##        PAS UNE ERREUR QUI EST RECUE          ##
            ##################################################
            #Départager les IP et les ports et envoi à la BDD par l'intermédiaire 
            # de la fonction spécifique
            for loop in range(ListeNoeuds.count(',')+1):
                lsteTemp = ListeNoeuds[:ListeNoeuds.find(',')]
                ListeNoeuds = ListeNoeuds[ListeNoeuds.find(',')+1:]
                BDD.ajouterEntree("Noeuds", lsteTemp)
            logs.ajtLogs("INFO : Connection closed. (DemandeNoeuds())")
            ConnectionDemande.close()
    else:
        error += 1
    return error

########################
#
# Ce code va permettre au noeud d'envoyer de nouveaux
# noeuds au demandeur
# Il va envoyer une requete qui contient 48 noeuds.
# (Le minimum d'IP+Ports qui peuvent tenir dans 1024 octets)
#
#########################

def EnvoiNoeuds(IpPortNoeud):
    #Départager l'IP et le port
    error = 0
    reg = re.compile("^([0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{1,5})?$")
    if reg.match(ipport): # Si ipport est un ip:port
        pos1 = IpPortNoeud.find(":")
        pos1 = pos1+1
        pos2 = len(IpPortNoeud)
        port = IpPortNoeud[pos1:pos2]
        pos1 = pos1-1
        hote = IpPortNoeud[0:pos1]
        connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion_principale.bind((hote, int(port)))
        connexion_principale.listen(5)
        logs.ajtLogs("INFO : Listen on port " + str(port) + ". (EnvoiNoeuds())")
        cipher = autresFonctions.createCipherAES(autresFonctions.readConfFile("AESKey"))
        serveur_lance = True
        clients_connectes = []
        while serveur_lance:
            # On va vérifier que de nouveaux clients ne demandent pas à se connecter
            # Pour cela, on écoute la connexion_principale en lecture
            # On attend maximum 50ms
            connexions_demandees, wlist, xlist = select.select([connexion_principale], [], [], 0.05)
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
                    # Peut planter si le message contient des caractères spéciaux
                    msg_recu = msg_recu.decode()
                    if msg_recu == "=cmd DonListeNoeuds 48":
                        #Oh, un noeud demande une liste de 48 noeuds sous la forme 000.000.000.000:00000 et séparés par une virgule
                        # On va chercher dans la BDD une liste de noeuds
                        msg_a_envoyer = b""
                        msg_a_envoyer = BDD.envNoeuds(48)
                        msg_a_envoyer = msg_a_envoyer.encode()
                        client.send(msg_a_envoyer)
        logs.ajtLogs("INFO : Connections closed. (EnvoiNoeuds())")
        for client in clients_connectes:
            client.close()
        connexion_principale.close()
    else:
        error += 1
    return error
