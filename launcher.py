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

# On vérifie que le fichier de config existe
try:
	with open('wtp.conf'):
		pass
except IOError:
	# Le fichier n'existe pas, on lance le créateur
	autresFonctions.fillConfFile()
BDD.ajouterEntree("Noeuds", "127.0.0.1:5557", "DNS")

# Créer un fichier qui va lancer les différentes
# instances en fonction de la configuration
os.popen('python3 maintenance.py', 'r')
os.popen('python3 vpn.py', 'r')
autresFonctions.afficherLogo()
fExtW = open(".extinctionWTP", "w")
fExtW.write("ALLUMER")
fExtW.close()

hote = '127.0.0.1'
port = int(autresFonctions.readConfFile("Port par defaut"))

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(5)
logs.ajtLogs("INFO : WTP a démarré, il ecoute à présent sur le port " + str(port))

serveur_lance = True
clients_connectes = []
while serveur_lance:
	connexions_demandees, wlist, xlist = select.select([connexion_principale], [], [], 0.05)
	for connexion in connexions_demandees:
		connexion_avec_client, infos_connexion = connexion.accept()
		clients_connectes.append(connexion_avec_client)
	clients_a_lire = []
	try:
		clients_a_lire, wlist, xlist = select.select(clients_connectes, [], [], 0.05)
	except select.error:
		pass
	else:
		for client in clients_a_lire:
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
				print(msg_recu)
				IpPortNoeud = msg_recu[pos2:pos3]
				if BDD.verifFichier(nomFichier):
					# Le fichier est présent dans la BDD, on peut l'envoyer
					client.send("=cmd OK".encode())
					time.sleep(0.5) # Le temps que le noeud distant mette en place son serveur
					if echangeFichiers.UploadFichier(nomFichier, IpPortNoeud) != 0:
						client.send("=cmd ERROR".encode())
					else:
						client.send("=cmd SUCCESS".encode())
					BDD.modifStats("NbEnvsFichiers")
				else:
					client.send("=cmd ERROR".encode())
			elif msg_recu[:17] == "=cmd DemandeNoeud": # Fonction Serveur
				# Dirriger vers la fonction EnvoiNoeuds()
				# Le noeud distant a demandé les noeuds, on lui envoi !
				# On trouve le premier port qui peut être attribué
				IpPortNoeud = "127.0.0.1:" + str(autresFonctions.portLibre(int(autresFonctions.readConfFile("Port Min"))))
				cmdAEnvoyer = IpPortNoeud # On envoie au demandeur l'adresse à contacter
				cmdAEnvoyer = cmdAEnvoyer.encode()
				client.send(cmdAEnvoyer)
				echangeNoeuds.EnvoiNoeuds(IpPortNoeud)
				BDD.modifStats("NbEnvsLstNoeuds")
			elif msg_recu[:25] == "=cmd DemandeListeFichiers":
				# On va récuperer le nom du fichier qui contient la liste
				# Ensuite, on la transmet au noeud distant pour qu'il puisse
				# faire la demande de réception du fichier pour qu'il puisse l'analyser
				if msg_recu[:28] == "=cmd DemandeListeFichiersExt":
					fichier = autresFonctions.lsteFichiers(1)
					BDD.modifStats("NbEnvsLstFichiers")
				else:
					fichier = autresFonctions.lsteFichiers()
					BDD.modifStats("NbEnvsLstFichiersExt")
				client.send(fichier.encode())
			elif msg_recu[:23] == "=cmd DemandeListeNoeuds":
				# On va récuperer le nom du fichier qui contient la liste
				# Ensuite, on la transmet au noeud distant pour qu'il puisse
				# faire la demande de réception du fichier pour qu'il puisse l'analyser
				fichier = autresFonctions.lsteNoeuds()
				client.send(fichier.encode())
				BDD.modifStats("NbEnvsLstNoeuds")
			elif msg_recu[:20] == "=cmd DemandePresence": # OPPÉRATIONNEL
				# C'est tout bête, pas besoin de fonction
				# Il suffit de renvoyer la commande informant que l'on est connecté au réseau.
				cmdAEnvoyer = "=cmd Present"
				cmdAEnvoyer = cmdAEnvoyer.encode()
				client.send(cmdAEnvoyer)
				BDD.modifStats("NbPresence")
			elif msg_recu[:15] == "=cmd rechercher": 
				# =cmd rechercher nom SHA256.ext
				# Renvoie le retour de la fonction, qui elle même retourne une IP+Port ou 0
				# Chercher le nom du fichier
				donnee = msg_recu[20:]
				cmdAEnvoyer = str(search.rechercheFichierEntiere(donnee))
				cmdAEnvoyer = cmdAEnvoyer.encode()
				client.send(cmdAEnvoyer)
			else:
				# Oups... Demande non-reconnue...
				if msg_recu != '':
					logs.ajtLogs("ERREUR : Commande non reconnue : " + msg_recu)
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
for client in clients_connectes:
	client.close()
connexion_principale.close()
logs.ajtLogs("INFO : WTP s'est correctement arrèté.")
