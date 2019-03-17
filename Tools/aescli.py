#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import sys
from Crypto import Random
from Crypto.Cipher import AES

# initialisation Variable
continuer = 'True'
host = 'localhost'
port = 5571
message_envoyer = ''
message_recu = ''

def createCipherAES(key):
    block_size = 16
    mode = AES.MODE_CFB
    iv = Random.new().read(block_size)
    return AES.new(key, mode, iv)

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    c.connect((host, port))
except(socket.error):
    print("l'hote n'est pas disponible")
    sys.exit()

# échange client serveur
cipher = createCipherAES("aeosiekrjeklkrje")

while(continuer == 'True'):
  message_envoyer = input('message: ')
  if(message_envoyer == 'close'):
    message_envoyer = cipher.encrypt(message_envoyer) # Cryptage du message en AES 16 bit
    c.send(message_envoyer) # Envois du message crypter
    print("Bye")
    continuer = 'False'
  message_envoyer = cipher.encrypt(message_envoyer) # Cryptage du message en AES 16 bit
  c.send(message_envoyer) # Envois du message crypter
  message_recu = c.recv(1024) # Réception des données crypter
  message_recu = cipher.decrypt(message_recu) # Décryptage des données recues.
  print(message_recu) # Affichage des données recues.
c.close()
