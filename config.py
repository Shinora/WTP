#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import autresFonctions

def fillConfFile():
	# On vide le file avant de le remplir de nouveau
	supprContenu = open("wtp.conf", "w")
	supprContenu.write("")
	supprContenu.close()
	def_port = input("Enter your main port (default:5555) : ")
	if def_port == "":
		# L'utilisateur veut laisser la valeur par défaut
		def_port = 5555
	else:
		def_port = int(def_port)
	portVPN = input("Enter your VPN port (default:5556) : ")
	if portVPN == "":
		# L'utilisateur veut laisser la valeur par défaut
		portVPN = 5556
	else:
		portVPN = int(portVPN)
	portDNS = input("Enter your DNS port (default:5557) : ")
	if portDNS == "":
		# L'utilisateur veut laisser la valeur par défaut
		portDNS = 5557
	else:
		portDNS = int(portDNS)
	min_port = 1
	max_port = 0
	while min_port > max_port:
		print("The minimum port must be smaller than the maximum port")
		min_port = input("Enter the minimum usable port (default:5550): ")
		if min_port == "":
			# L'utilisateur veut laisser la valeur par défaut
			min_port = 5550
		else:
			min_port = int(min_port)
		max_port = input("Enter the maximum usable port (default:5600): ")
		if max_port == "":
			# L'utilisateur veut laisser la valeur par défaut
			max_port = 5600
		else:
			max_port = int(max_port)
	blacklist = str(input("Enter your trust node for the blacklist (IP:PORT) : "))
	if blacklist == "":
		blacklist = "88.189.108.233:5555"
	autostart = input("Do you want to enable autostart ? ( 0 = Yes / 1 = No ) : ")
	parser = input("Do you want to enable parser mode ? ( 0 = Yes / 1 = No ) : ") # Parser = SuperNoeud
	vpn = input("Do you want to enable VPN ? ( 0 = Yes / 1 = No ) : ")
	dns = input("Do you want to enable DNS ? ( 0 = Yes / 1 = No ) : ")
	conf_file = open("wtp.conf", "a")
	conf_file.write("defaultPort : "+str(def_port)+"\n")
	conf_file.write("VPNPort : "+str(portVPN)+"\n")
	conf_file.write("DNSPort : "+str(portDNS)+"\n")
	conf_file.write("miniPort : "+str(min_port)+"\n")
	conf_file.write("MaxPort : "+str(max_port)+"\n")
	conf_file.write("AESKey : aeosiekrjeklkrjb\n")
	conf_file.write("MyIP : "+str(autresFonctions.connaitreIP())+"\n")
	conf_file.write("Version : 0.0.9-4 Beta\n")
	conf_file.write("Path : "+str(os.getcwd())+"\n")
	if autostart == "0":
		conf_file.write("Autostart : Oui\n")
	else:
		conf_file.write("Autostart : Non\n")
	if parser == "0":
		conf_file.write("Parser : True\n")
	else:
		conf_file.write("Parser : False\n")
	if vpn == "0":
		conf_file.write("VPN : True\n")
	else:
		conf_file.write("VPN : False\n")
	if dns == "0":
		conf_file.write("DNS : True\n")
	else:
		conf_file.write("DNS : False\n")
	conf_file.write("Blacklist : "+str(blacklist)+"\n")
	conf_file.close()

def readConfFile(parametre): # Fonctionne pour tout sauf Blacklist
	# Fonction qui lit le file de configuration et qui retourne l'information demandée en paramètres
	try:
		with open('wtp.conf'):
			pass
	except IOError:
		# Le file n'existe pas
		fillConfFile()
	if os.path.getsize("wtp.conf") < 80:
		# Le file est très léger, il ne peut contenir les informations
		# Il faut donc le recréer
		fillConfFile()
	f = open("wtp.conf",'r')
	lignes  = f.readlines()
	f.close()
	for ligne in lignes:
		# On lit le file ligne par ligne et si on trouve le paramètre dans la ligne,
		# on renvoie ce qui se trouva après
		if ligne[:len(parametre)] == parametre and ligne[len(parametre)+1:len(parametre)+2] == ":":
			# On a trouvé ce que l'on cherchait
			# Maintenant on enlève " : "
			return ligne[len(parametre)+3:-1]

def modifConfigFile(parametre, value):
	# Fonction qui a pour but de remplacer la valeur actuelle du fichier de config
	# Par la valeur passée en paramètres
	try:
		with open('wtp.conf'):
			pass
	except IOError:
		# Le file n'existe pas
		fillConfFile()
	if os.path.getsize("wtp.conf") < 80:
		# Le file est très léger, il ne peut contenir les informations
		# Il faut donc le recréer
		fillConfFile()
	f = open("wtp.conf",'r')
	lignes  = f.readlines()
	f.close()
	fichierFinal = ""
	for ligne in lignes:
		if ligne[:len(parametre)] == parametre and ligne[len(parametre)+1:len(parametre)+2] == ":":
			# On a trouvé ce que l'on cherchait
			fichierFinal += parametre + " : " + value + "\n"
		else:
			fichierFinal += ligne
	f = open("wtp.conf", "w")
	f.write(fichierFinal)
	f.close()

def modifConfig():
	# Fonction qui a pour but de modifier le fichier de configuration.
	print("Configuration file path : " + str(os.getcwd()) + "/wtp.conf")
	print("This is the actual configuration file :\n")
	f = open("wtp.conf", "r")
	print(f.read()+"\n")
	f.close()
	print("Enter exit to exit this wizard")
	while 1:
		param = input("What would you want to change ? (exit for quit)\n")
		if param == "exit":
			break
		current = str(readConfFile(param))
		if current == "None":
			print("This parameter is unknown.")
		else:
			print("The current setting is : " + current)
			value = str(input("By what do you want to replace him ?\n"))
			modifConfigFile(param, value)
			print("Done !")
		print("\n")
	print("For the changes to take effect, please restart WTP")
