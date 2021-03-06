from datetime import datetime
import requests
from color import c

 ####################################################
#                                                    #
# Sont ici les fonctions qui ont un rapport avec les #
# logs, qui se situent dans le file logs.txt qui  #
# est dans le même dossier que ce file.           #
#                                                    #
 ####################################################

# Fonction pour ajouter une ligne dans les logs.
# Elle n'a qu'un paramètre, le texte à ajouter aux logs.
# Il doit contenir à la fin le nom de la fonction.
def addLogs(texte):
	dateHeure = str(datetime.now()) # Ex : 2018-07-03 18:05:37.441483
	chaineFinale = "[{0}] : {1}\n".format(dateHeure[:19], texte)
	# Vérifier si ja ligne précédente est la même
	# Si c'est le cas on ecrit pas
	try:
		f = open("logs.txt",'r')
	except IOError:
		f = open("logs.txt", "a")
		f.write(chaineFinale)
		f.close()
	else:
		lines  = f.readlines()
		f.close()
		lastLine = ""
		for line in lines:
			lastLine = line
		lastLine = lastLine[24:-1]
		if lastLine != texte:
			f = open("logs.txt", "a")
			f.write(chaineFinale)
			f.close()

# Fonction pour supprimer les logs
# Elle n'a aucun paramètre.
def supprLogs():
	f = open("logs.txt", "w")
	f.write("")
	f.close()

def rapportErreur(selection = " "):
	# Sélectionne les lignes ayant le mot clef de la selection ou les mots clefs plus graves
	# Envoie le tout à un serveur
	# INFO < WARNING < ERREUR
	megaStr = ""
	with open("logs.txt") as f :
		for line in f :
			if line.find(selection) != -1:
				megaStr += line
	f.close()
	data = {"text":megaStr}
	try:
		requests.post("https://myrasp.fr/WTP/Logs/index.php", data = data)
	except Exception as e:
		addLogs("ERROR : We could not send the logs to the developers in rapportErreur() : " + str(e))
		print(c("yellow")+"We could not send the logs to the developers... \nCheck your Internet connection."+c(""))
	else:
		supprLogs()
		addLogs(c("cian")+"INFO : The logs have been sent to the developers."+c(""))
