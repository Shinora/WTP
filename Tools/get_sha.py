import os
import hashlib
import requests

new_fich = open("sha.txt", "w")
new_fich.close()
fichList = [ f for f in os.listdir('.') if os.path.isfile(os.path.join('.',f)) ]
for fichier in fichList:
	if fichier[0] != "." and fichier != "logs.txt" and fichier != "wtp.conf" and fichier != "WTP.db":
		acces_file = open(fichier, "r")
		contenu = acces_file.read()
		acces_file.close()
		sha_fichier = hashlib.sha256(contenu.encode()).hexdigest()
		new_fich = open("sha.txt", "a")
		new_fich.write(fichier + " : " + sha_fichier+ " \n" )
		new_fich.close()
		# En parallèle on envoi sur le site pour que les autres noeuds puissent se mettre à jour
		data = {"nom":fichier, "contenu":sha_fichier}
		r = requests.post("https://myrasp.fr/WTPStatic/index.php", data = data)
		print("Le SHA256 de " + fichier + " a bien été actualisé sur le site.")
print("La mise a jour est terminée !")
