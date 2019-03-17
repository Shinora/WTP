#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import os.path
import BDD
import maj
import search
from loader import loader
import config
from clientDNS import DNSConfig
import fctsMntc
import shutil
import logs
import dns
import autresFonctions
import fctsClient
import blacklist


def cmdLauncher(userCmd):
	error = 0
	if userCmd == "help":
		# Afficher toutes les options
		print("Web Transfer Protocol	V"+str(config.readConfFile("Version")))
		print("Here are the main functions:")
		print("update		Check for updates")
		print("stats 		Shows your peer statistics")
		print("config 		Edit the configuration")
		print("exit 		Stop WTP")
		print("dns 		Edit the VPN configuration")
		print("doc 		How to use wtp")
		print("checkFiles 	Check the ADDFILES and HOSTEDFILES")
		print("delAll 		Delete all : Config, DB, Files.")
		print("majDNS		Update the DNS database")
		print("client 		Use WTP in console")
		print("majBlkLst	Update the blacklist database")
	elif userCmd == "update":
		# Vérifier les MAJ
		status = loader("Work in progress")
		status.start()
		#maj.verifMAJ()
		#maj.verifSources()
		status.stop()
		status.join()
		print("Done.")
	elif userCmd == "stats":
		# Affiche les statistiques
		print("Number of peers in the database : " + str(BDD.compterStats("NbNoeuds")))
		print("Number of special peers in the database : " + str(BDD.compterStats("NbSN")))
		print("Number of external files in the database : " + str(BDD.compterStats("NbFichiersExt")))
		print("Number of files on this hard drive : " + str(BDD.compterStats("NbFichiers")))
		print("Size of all files : " + str(BDD.compterStats("PoidsFichiers")))
		print("Number of peers lists sent : " + str(BDD.compterStats("NbEnvsLstNoeuds")))
		print("Number of file lists sent : " + str(BDD.compterStats("NbEnvsLstFichiers")))
		print("Number of external file lists sent : " + str(BDD.compterStats("NbEnvsLstFichiersExt")))
		print("Number of files sent : " + str(BDD.compterStats("NbEnvsFichiers")))
		print("Number of presence requests received : " + str(BDD.compterStats("NbPresence")))
		print("Number of files received : " + str(BDD.compterStats("NbReceptFichiers")))
	elif userCmd == "config":
		# Modifier le fichier de configuration
		config.modifConfig()
	elif userCmd == "dns":
		# Entrer dans le programme de configuration du DNS
		thrdDNS = DNSConfig()
		thrdDNS.start()
		thrdDNS.join()
	elif userCmd == "exit":
		# On arrète WTP
		print("Pro tip : You can also stop WTP at any time by pressing Ctrl + C.")
		return -1
	elif userCmd == "doc":
		# On affiche la documentation
		print("Welcome to the WTP documentation.")
		print("1. Basics")
		print("To be able to use WTP from your browser, you need to install the browser extension. Link : https://github.com/Torzivalds/WTP/tree/master/Extention%20Firefox  A configuration wizard is included.\n")
		print("To add files to the network, you must go to the file named ADDFILES and copy / paste them. Path : "+str(os.getcwd())+"/ADDFILES  WTP will automatically add them. \nPro tip : WTP checks this folder every 5 minutes. If you are in a hurry, you can enter this request : checkFiles. \nDISCLAMER : A file can not be deleted from the network. Be careful when you add some.")
		print("For more information on the possible commands here, enter help.\n")
		print("2. Advenced")
		print("You found a bug or improvement ? Contact us on our website :\nhttps://myrasp.fr/WTP")
		print("Developer ressources are in the Wiki part of our GitHub.\nhttps://github.com/Torzivalds/WTP/wiki")
		print("3. Contribute")
		print("You can contribute by improving the code with us, by talking about Web Transfer Protocol to your friends, your family, your colleagues, and if you can not contribute in these ways, you can donate via PayPal.\nYour contributions make us happy and help us to move forward, thank you!\n")
		print("4. External ressources")
		print("GitHub : https://github.com/Torzivalds/WTP\nPayPal : https://paypal.me/torzivalds\nWebsite : https://myrasp.fr/WTP\nFirefox Extension : https://github.com/Torzivalds/WTP/tree/master/Extention%20Firefox")
	elif userCmd == "checkFiles":
		# On vérifie immédiatement dans ADDFILES, HOSTEDFILES et .TEMP
		status = loader("Work in progress")
		status.start()
		fctsMntc.creerFichier()
		fctsMntc.checkIntruders()
		fctsMntc.supprTemp()
		status.stop()
		status.join()
		print("Done.")
	elif userCmd == "delAll":
		print("Are you sure you want to delete everything ?\nAll configuration, database, hosted files will be lost.")
		print("You will not be able to go back.")
		if str(input("If you are sure, enter DeleteAll\n>> ")) == "DeleteAll":
			print("We are sorry to see you go.\nWe hope to see you very soon !\nIf you have comments to send to you, please contact us via our website :\nhttps://myrasp.fr/WTP")
			status = loader("Work in progress")
			status.start()
			shutil.rmtree(str(os.getcwd())+"/HOSTEDFILES")
			shutil.rmtree(str(os.getcwd())+"/ADDFILES")
			os.remove(str(os.getcwd())+"/.extinctionWTP")
			os.remove(str(os.getcwd())+"/.TempMaintenance24H")
			os.remove(str(os.getcwd())+"/.TempMaintenance5M")
			logs.rapportErreur()
			os.remove(str(os.getcwd())+"/logs.txt")
			os.remove(str(os.getcwd())+"/wtp.conf")
			status.stop()
			status.join()
			return -1
		print("You scared us!\nFortunately, you have not passed the dark side of the force!")
	elif userCmd == "majDNS":
		print("You want to update the DNS database.\nIf you are crazy, you can enter crazy to update with a random peer.")
		ipport = str(input("With which DNS do you want to update ?\n>> "))
		# Vérifier le noeud
		if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', ipport):
			# C'est un IPPort
			ip = ipport[:ipport.find(":")]
			port = int(ipport[ipport.find(":")+1:])
			co = autresFonctions.connectionClient(ip, port)
			if co != "=cmd ERROR":
				connexion_avec_serveur.send(sendCmd.encode())
				rcvCmd = connexion_avec_serveur.recv(1024).decode()
				connexion_avec_serveur.close()
				if rcvCmd == "=cmd DNS":
					e = dns.majDNS()
					if int(e) > 0:
						print("An error occured.")
					else:
						print("Done.")
				else:
					print("This peer isn't DNS.")
			print("Unable to connect to this peer.")
		elif ipport == "crazy":
			print("DISCLAMER : Some peers can be controlled by malicious people who can perform phishing attacks")
			rep = str(input("Are you sure ? (y/N)\n>>"))
			if rep == "y" or rep == "Y":
				e = dns.majDNS()
				if int(e) > 0:
					print("An error occured.")
				else:
					print("Done.")
			else:
				print("You scared us!\nFortunately, you have not passed the dark side of the force!")
		else:
			print("It's not an ip:port")
	elif userCmd == "client":
		# Possibilité de faire des demandes en console
		error = 0
		sendCmd = ""
		print("You can now write requests and send them to the peers you want.")
		print("Exit this wizard and enter doc for more information.")
		while sendCmd != "exit":
			sendCmd = str(input("What is your request ? (exit for quit this wizard)\n>> "))
			if sendCmd != "exit":
				host = str(input("What is the IP of the peer that you want to contact ? > "))
				try:
					port = int(input("What is the Port of the peer that you want to contact ? > "))
				except ValueError:
					print("It isn't a port (between 1024 and 65535)")
				else:
					if sendCmd == "=cmd DemandeNoeud":
						error += fctsClient.CmdDemandeNoeud(host, port)
					elif sendCmd[:19] == "=cmd DemandeFichier":
						# =cmd DemandeFichier nom sha256.ext
						error += fctsClient.CmdDemandeFichier(host, port, sendCmd[24:])
					elif sendCmd == "=cmd DemandeListeNoeuds":
						error += fctsClient.CmdDemandeListeNoeuds(host, port)
					elif sendCmd == "=cmd DemandeListeFichiers":
						error += fctsClient.CmdDemandeListeFichiers(host, port)
					elif sendCmd[:19] == "=cmd rechercher nom":
						# =cmd rechercher nom SHA256.ext
						sortie = search.rechercheFichierEntiere(sendCmd[20:])
						ipport = sortie[:sortie.find(";")]
						sha = sortie[sortie.find(";")+1:]
						if re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', ipport):
							# C'est un IPPort
							# On envoi vers la fonction qui télécharge le file
							ip = ipport[:ipport.find(":")]
							port = int(ipport[ipport.find(":")+1:])
							error += fctsClient.CmdDemandeFichier(ip, int(port), sha)
						else:
							# C'est une erreur
							print(sortie)
							error += 1
					else:
						error = 0
						connexion_avec_serveur = autresFonctions.connectionClient(host, port)
						if str(connexion_avec_serveur) == "=cmd ERROR":
							error += 1
						else:
							connexion_avec_serveur.send(sendCmd.encode())
							rcvCmd = connexion_avec_serveur.recv(1024).decode()
							connexion_avec_serveur.close()
							print(rcvCmd)
					if int(error) == 0:
						print("Done.")
					else:
						print("An error occured. ("+str(error)+")")
	elif userCmd == "add":
		# L'utilisateur veut ajouter quelque chose
		categorie = str(input("What do you want to add ?\n>>> "))
		if categorie == "peer":
			ipport = str(input("What is the IP:Port of the peer ?\n>>> "))
			error = BDD.ajouterEntree("Noeud", ipport)
			if error == 0:
				print("Done.")
			else:
				print("An error occured ("+str(error)+").")
		else:
			print("Your input is unknown.")
			print("You can enter help for more information.")
	elif userCmd == "majBlkLst":
		# L'utilisateur veut mettre à jour sa BlackList
		ipport = str(input("With which peer do you want to update? (Press ENTER to update with the default peer : "+str(config.readConfFile("BlackList"))+")\n>> "))
		if ipport == "enter" or ipport == "ENTER" or ipport == "":
			status = loader("Work in progress")
			status.start()
			blacklist.maj()
			status.stop()
			status.join()
		else:
			if autresFonctions.verifIPPORT(IppeerPort): # Si ipport est un ip:port
				status = loader("Work in progress")
				status.start()
				blacklist.maj(ipport)
				status.stop()
				status.join()
			else:
				print("This is not a IP:PORT")
	else:
		print("Unknown request.")
	return 0
