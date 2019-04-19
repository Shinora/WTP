import os
import os.path
import logs
import zipfile
import hashlib
from urllib.request import *

def verifMAJ(force = 0):
	# Fonction qui a pour but de vérifier si il y a des mises à jour à faire
	# Elle va regarder sur une page de myrasp.fr la dernière version du protocol
	# Et si elle a une version différente, on télécharge le file zip contenant les nouvelles sources
	# Si force = 1, il indique une version obsolète pour forcer la MAJ
	if force == 1:
		versionActuelle = "0.0.1"
	else:
		versionActuelle = "0.0.9"
	class AppURLopener(FancyURLopener):
			version = "Mozilla/5.0"
	opener = AppURLopener()
	page = opener.open("https://static.myrasp.fr/WTP/latestWTP.html")
	latest = page.read().decode("utf-8")
	if versionActuelle != latest:
		# Il faut mettre à jour
		logs.addLogs("INFO : Démmarage de la mise à jour de V" + str(versionActuelle) + " à V" + latest)
		# Le file zip a un nom de forme WTPversion.zip Ex : WTP0.0.1.zip
		fileName = "WTP"+latest+".zip"
		url = 'https://myrasp.fr/WTP/Maj/'+fileName
		try:
			os.makedirs(".MAJ")
		except OSError:
			if not os.path.isdir(".MAJ"):
				raise
		with open('.MAJ/'+fileName, 'wb') as archive:
			archive.write(opener.open(url).read())
		# Le téléchargement des nouvelles sources est terminé
		# Extraction dans .MAJ/version Ex : .MAJ/0.0.1/
		# Vérifier si le dossier .MAJ/version existe, sinon le créer
		try:
			os.makedirs(".MAJ/"+latest)
		except OSError:
			if not os.path.isdir(".MAJ/"+latest):
				logs.addLogs("ERROR : The zip file isn't present in verifMAJ()")
		with zipfile.ZipFile(".MAJ/"+fileName,"r") as zip_ref:
			zip_ref.extractall(".MAJ/"+latest+"/")
		# Extraction terminée
		# Maintenant il faut remplacer les anciens files par les nouveaux
		liste = os.listdir(".MAJ/"+latest+"/")
		nbFichiers = len(liste)
		for x in range(nbFichiers):
			newFichier = ".MAJ/"+latest+"/"+liste[x]
			oldFichier = liste[x]
			# On copie le contenu du nouveau file
			file = open(newFichier, "rb")
			contenuNewFichier = file.read()
			file.close()
			# On remplace l'ancien par la copie
			file = open(oldFichier, "wb")
			file.write(contenuNewFichier)
			file.close()
			logs.addLogs("INFO : The file " + oldFichier + " has been updated")
		logs.addLogs("INFO : The update is complete")
		# Il faut redemarrer le protocol
		print("\033[36mThe update is complete. Please restart WTP.\033[0m")
	else:
		logs.addLogs("INFO : Pas de mise à jour disponible")

def verifSources():
	files = [ f for f in os.listdir('.') if os.path.isfile(os.path.join('.',f)) ]
	for en_cours in files:
		class AppURLopener(FancyURLopener):
			version = "Mozilla/5.0"
		if en_cours[0] != "." and en_cours != "logs.txt" and en_cours != "wtp.conf" and en_cours != "WTP.db":
			opener = AppURLopener()
			page = opener.open("https://myrasp.fr/WTP/Maj/"+en_cours)
			online_sha = page.read().decode("utf-8")
			acces_file = open(en_cours, "r")
			contenu = acces_file.read()
			acces_file.close()
			sha_file = hashlib.sha256(str(contenu).encode()).hexdigest()
			if online_sha != sha_file:
				# On lance la MAJ en mode forcé
				logs.addLogs("ERROR : When checking sources, the file " + en_cours + " was found to be incorrect. New sources will be downloaded.")
				verifMAJ(1)
