#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# Synchrotron Soleil
#
# Nom: logger.py
#
#Affiche les messages dans la sortie choisie 
#en tenant compte du flag "verbose".  
########################################################################

"""
Created on 11/08/2017
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""

import sys
import os
#-------------------importation de module de log
import logging 

#-------------------importation du module qui gere les copies des fichiers
import shutil

class Logger() :
	def __init__(self,file_log,name="") :
		"""Show the messages in the chosen output.
		   Initialize the types of messages, their formats and 
                   their destinations were used by the application.
		   ::parameter : name : name of logger, use to create specific  logger. 
		"""
		
		#initialisation du logger
		self.logger = logging.getLogger(name) 
		self.logger.handlers = []
		#niveau des messages du logger par defaut
		self.level  = logging.INFO       

#----------initialisation du niveau de message du logger
		self.logger.setLevel(self.level)
#--------initialisation de la sortie stdout
		formatter_out = logging.Formatter('[%(asctime)s] %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
		self.message_output = logging.StreamHandler(sys.stdout)
		self.message_output.setLevel(logging.INFO)
		self.message_output.setFormatter(formatter_out)
		
#--------si le fichier de logs existe, faire une copie
		
		if os.path.isfile(file_log) :
			shutil.copyfile(file_log, '%s.backup'%file_log)
#--------initialisation de la sortie fichier logs
		log_handler = logging.FileHandler(file_log,mode='w')
		formatter_log = logging.Formatter('[%(asctime)s] %(levelname)-8s  : %(message)s','%Y-%m-%d %H:%M:%S')
		log_handler.setFormatter(formatter_log)
		log_handler.setLevel( logging.DEBUG )

#-------ajout des sortie dans le logger
		self.logger.addHandler(self.message_output)
		self.logger.addHandler(log_handler)
			
		
#-----------Méthodes d’interrogation et de modification de l'état de l'objet
	def getLevel(self) :
		return logging.getLevelName(self.level)

	def setVerbose(self):
		self.level  = logging.DEBUG
		self.logger.setLevel(self.level) 
		

	def setInfo(self):
		self.level  = logging.INFO
		self.logger.setLevel(self.level)

	def debug(self, message) :
		self.logger.debug(message)

	def info(self, message) :
		self.logger.info(message)

	def warning(self, message) :
		self.logger.warning(message)

	def error(self, message) :
		self.logger.error(message)

	def critical(self, message) :
		self.logger.critical(message)
	
	



