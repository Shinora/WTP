#!/bin/bash

echo Demmarage de l\'installation de WTP

echo Installations de Python3...
sudo apt install python3 -y

echo Téléchargement des dernières sources...
wget https://static.myrasp.fr/WTP/latest.zip

echo Dépaquetage des sources...
unzip latest.zip

echo Instalation terminée !
echo Démmarage...
python3 launcher.py