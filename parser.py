import logs
import fctsClient
import BDD
import threading
import sqlite3
import autresFonctions

# Fonctionnalité qui permet de connaitre l'intégralité du réseau


class Parser(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.allume = True

	def run(self):
		while self.allume:
			BDD.verifExistBDD()
			conn = sqlite3.connect('WTP.db')
			cursor = conn.cursor()
			try:
				cursor.execute("""SELECT IP FROM Noeuds WHERE 1""")
				rows = cursor.fetchall()
			except Exception as e:
				conn.rollback()
				logs.addLogs("ERREUR : Problem with database (parseAll()) : " + str(e))
			for row in rows:
				if autresFonctions.verifIPPORT(row): # Si row est un ip:port
					host = row[:row.find(":")]
					port = row[row.find(":")+1:]
					# Pour chaque noeud on demande la liste de :
					# tous les files qu'il héberge (=cmd DemandeListeFichiers)
					fctsClient.CmdDemandeListeFichiers(host, port)
					# tous les files externes qu'il connait (=cmd DemandeListeFichiersExt)
					fctsClient.CmdDemandeListeFichiers(host, port, 1)
					# tous les noeuds qu'il connait (=cmd DemandeListeNoeuds)
					fctsClient.CmdDemandeListeNoeuds(host, port)
			conn.close()

	def stop(self):
		self.allume = False
