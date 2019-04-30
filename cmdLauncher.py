import os
import os.path
import BDD
#import maj
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
import clientBlacklist
import stats
import documentation
from color import c


def cmdLauncher(userCmd):
	error = 0
	if userCmd == "help":
		# Afficher toutes les options
		documentation.mini()
	elif userCmd == "update":
		# Vérifier les MAJ
		status = loader("Work in progress")
		status.start()
		#maj.verifMAJ()
		#maj.verifSources()
		status.stop()
		status.join()
		print(c("green")+"Done."+c(""))
	elif userCmd == "stats":
		# Affiche les statistiques
		print("Number of peers in the database : " + str(stats.compterStats("NbNoeuds")))
		print("Number of special peers in the database : " + str(stats.compterStats("NbSN")))
		print("Number of external files in the database : " + str(stats.compterStats("NbFichiersExt")))
		print("Number of files on this hard drive : " + str(stats.compterStats("NbFichiers")))
		print("Size of all files : " + str(stats.compterStats("PoidsFichiers")))
		print("Number of peers lists sent : " + str(stats.compterStats("NbEnvsLstNoeuds")))
		print("Number of file lists sent : " + str(stats.compterStats("NbEnvsLstFichiers")))
		print("Number of external file lists sent : " + str(stats.compterStats("NbEnvsLstFichiersExt")))
		print("Number of files sent : " + str(stats.compterStats("NbEnvsFichiers")))
		print("Number of presence requests received : " + str(stats.compterStats("NbPresence")))
		print("Number of files received : " + str(stats.compterStats("NbReceptFichiers")))
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
		documentation.maxi()
	elif userCmd == "checkFiles":
		# On vérifie immédiatement dans ADDFILES, HOSTEDFILES et .TEMP
		status = loader("Work in progress")
		status.start()
		fctsMntc.checkIntruders()
		fctsMntc.creerFichier()
		fctsMntc.supprTemp()
		status.stop()
		status.join()
		print(c("green")+"Done."+c(""))
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
		ipport = str(input("With which DNS do you want to update ? (IP:Port)\n>> "))
		# Vérifier le noeud
		if autresFonctions.verifIPPORT(ipport):
			# C'est un IPPort
			co = autresFonctions.connectionClient(ipport)
			if co != "=cmd ERROR":
				sendCmd = "=cmd status"
				co.send(sendCmd.encode())
				rcvCmd = co.recv(1024).decode()
				co.close()
				if rcvCmd == "=cmd DNS":
					e = dns.majDNS(ipport)
					if int(e) > 0:
						print(c("red")+"An error occured."+c(""))
					else:
						print(c("green")+"Done."+c(""))
				else:
					print(c("red")+"This peer isn't DNS."+c(""))
			print(c("red")+"Unable to connect to this peer."+c(""))
		elif ipport == "crazy":
			print("DISCLAMER : Some peers can be controlled by malicious people who can perform phishing attacks")
			rep = str(input("Are you sure ? (y/N)\n>>"))
			if rep == "y" or rep == "Y":
				e = dns.majDNS()
				if int(e) > 0:
					print(c("red")+"An error occured."+c(""))
				else:
					print(c("green")+"Done."+c(""))
			else:
				print("You scared us!\nFortunately, you have not passed the dark side of the force!")
		else:
			print(c("red")+"It's not an ip:port"+c(""))
	elif userCmd == "client":
		# Possibilité de faire des demandes en console
		error = 0
		sendCmd = ""
		print("You can now write requests and send them to the peers you want.")
		print("Exit this wizard and enter doc for more information.")
		while sendCmd != "exit":
			sendCmd = str(input("What is your request ? (exit for quit this wizard)\n>> "))
			if sendCmd == "doc":
				documentation.maxi()
			elif sendCmd != "exit":
				host = str(input("What is the IP of the peer that you want to contact ? > "))
				try:
					port = int(input("What is the Port of the peer that you want to contact ? > "))
				except ValueError:
					print(c("red")+"It isn't a port (between 1024 and 65535)"+c(""))
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
						if autresFonctions.verifIPPORT(ipport):
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
						print(c("green")+"Done."+c(""))
					else:
						print(c("red")+"An error occured. ("+str(error)+")"+c(""))
			else:
				break
	elif userCmd == "add":
		# L'utilisateur veut ajouter quelque chose
		categorie = str(input("What do you want to add ?\n>>> "))
		if categorie == "peer":
			ipport = str(input("What is the IP:Port of the peer ?\n>>> "))
			error = BDD.ajouterEntree("Noeud", ipport)
			if error == 0:
				print(c("green")+"Done."+c(""))
			else:
				print(c("red")+"An error occured ("+str(error)+").")
		else:
			print(c("red")+"Your input is unknown."+c(""))
			print(c("cian")+"You can enter help for more information."+c(""))
	elif userCmd == "blacklist":
		blckLst = clientBlacklist.configBlckLst()
		blckLst.start()
		blckLst.join()
	else:
		print(c("red")+"Unknown request."+c(""))
	return 0
