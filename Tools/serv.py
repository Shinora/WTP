#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import sys
from Crypto.Cipher import AES
from Crypto import Random

# initialisation Variable
continuer = 'True'
host = 'localhost'
port = 4445
message_envoyer = ''
message_recu = ''

# Cryptage AES configuration en 16 bit, vous pouvez choisir en 16, 24 ou 32

key = 'aeosiekrjeklkrje'
block_size = 16
mode = AES.MODE_CFB
iv = Random.new().read(block_size)
cipher = AES.new(key, mode, iv)

# liaison tcp/ip

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# accepter des clients

try:
  s.bind((host, port))
except(socket.error):
  print "port déja utiliser"
  sys.exit()
  
s.listen(5)
print "en attente de client"
conn, addr = s.accept()
print "\nclient connecter"

# échange serveur client

while(continuer == 'True'):
  message_recu = conn.recv(1024) # données reçues crypter
  message_recu = cipher.decrypt(message_recu) # décryptage des données reçues
  if(message_recu == 'close'): # condition de sortie
    print "bye"
    sys.exit()
  print message_recu # Affichage des données reçues
  message_envoyer = 'Vous êtes connecter au serveur' # Le message à envoyer au client
  message_envoyer = cipher.encrypt(message_envoyer) # On crypte le message en AES 16 bit
  conn.send(message_envoyer) # On envois le message crypter en AES 16 bit

conn.close()
s.close()