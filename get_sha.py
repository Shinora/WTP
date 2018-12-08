import os
import hashlib
new_fich = open("sha.txt", "w")
new_fich.close()
fichList = [ f for f in os.listdir('.') if os.path.isfile(os.path.join('.',f)) ]
print (fichList)
for fichier in fichList:
	acces_file = open(fichier, "r")
	contenu = acces_file.read()
	acces_file.close()
	sha_fichier = hashlib.sha256(contenu.encode()).hexdigest()
	new_fich = open("sha.txt", "a")
	new_fich.write(fichier + " : " + sha_fichier+ " \n" )
	new_fich.close()


