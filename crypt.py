#! /usr/bin/python
# -*- coding:utf-8 -*-

import socket
import sys
from Crypto.Cipher import AES
from Crypto import Random

# Toutes les fonctions ici servent à crypter et décrypter le trafic réseau
############################################################
# NE FONCTIONNE PAS POUR LE MOMENT, ON VERRA ÇA PLUS TARD...
############################################################

def encryptAES(chaine):
	# Cryptage AES configuration en 16 bit, vous pouvez choisir en 16, 24 ou 32
	key = 'aeosiekrjeklkrje'
	block_size = 16
	mode = AES.MODE_CFB
	iv = Random.new().read(block_size)
	cipher = AES.new(key, mode, iv)
	return cipher.encrypt(chaine)

def decryptAES(chaine):
	# Cryptage AES configuration en 16 bit, vous pouvez choisir en 16, 24 ou 32
	key = 'aeosiekrjeklkrje'
	block_size = 16
	mode = AES.MODE_CFB
	iv = Random.new().read(block_size)
	cipher = AES.new(key, mode, iv)
	return cipher.decrypt(chaine)

for loop in range(50):
	print(decryptAES(encryptAES("Bonjour"))