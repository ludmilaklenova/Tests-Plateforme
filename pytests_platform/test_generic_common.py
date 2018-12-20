#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################################
# Synchrotron Soleil
#
# Nom: test_generique_common.py
#
#Décrit le scénario générique des tests.
# 
#
########################################################################
"""
Created on 14/08/2018
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""

import os
import sys
import time

class TestGeneric(object):
    """Generic test object"""

    logger       = None #créateur des fichiers des logs
    device_proxy = None #proxy vers un device
    fonc_message = "process has normally finished" #dernier message du test
    var_env      = 'PYTESTS_PLATFORM_ROOT' #nom de la variable d'environnement
    rc           = 1 # code de retour du test
    
    def get_fonc_message(self):
		"""Get last fonction message.
		"""
        return self.fonc_message
    
    def run(self, *args, **kwargs):
		"""Test run.
		"""
        raise NotImplementedError

    def setUp(self, *args, **kwargs):
		"""Initial state for all test methods.
		"""
        pass

    def setEnv(self, **kwargs):
        """Initialize the environment than the test can turn.
		   ::parameter: log_file of kwargs - log file name,
		   ::parameter: tango_host of kwargs - host tango database,
           ::return :
                         0, if the environment is set,
                         1, otherwise.
        """
#-------------nom du fichier des logs
        log_file = kwargs['log_file']
		
 #-------------on doit travailler avec la bdd Tango donc le host est donné en argument
        os.environ['TANGO_HOST'] = kwargs['tango_host']
               
#-----------vérification des variables d'environnement nécessaires pour les tests  
        ROOT_DIR = os.getenv(self.var_env)
#------------si les variables d'environnement n'existent pas, fin de test
        if not ROOT_DIR :
            self.fonc_message = "'%s' is not found"%self.var_env
            return 1
        elif not os.path.isdir(ROOT_DIR) :
            self.fonc_message = "Directory '%s' is not found"%ROOT_DIR
            return 1
#-----------création du chemin vers la bibliothèque des tests
        else :
            PLATFORM_TESTS_COMMON = os.path.join(ROOT_DIR, 'lib', 'python2.7', 'site-packages','pytests_platform','lib','common')
            if not os.path.isdir(PLATFORM_TESTS_COMMON) :
                self.fonc_message = "Directory '%s' is not found"%PLATFORM_TESTS_COMMON
                return 1
            
#------initialisation des variables d'environnement d’exécution des tests
        sys.path.append(PLATFORM_TESTS_COMMON)
        
#--------------importation des modules 
        try:
            from utils.logger import Logger #classe qui gère des logs 
            from devices.tango import DeviceProxy #classe qui gère les devices
            self.device_proxy = DeviceProxy
        except Exception, details :
            self.fonc_message = "Import error : '%s'"%str(details)
            return 1
        
#----------------si le répertoire du fichier des logs n'existe pas, création
        if not os.path.isdir(os.path.dirname(log_file)):
            try:
                os.makedirs(os.path.dirname(log_file))
            except Exception, details :
                self.fonc_message = "Error : %s "%str(details)
                return 1

#----------------initialisation des logs 
        self.logger = Logger(log_file,'main')
        self.logger.info(unicode('log file : %s '%log_file))
		
#----------------mise à jour du niveau des messages du logger
        self.logger.setVerbose()
        return 0

    def tearDown(self, **kwargs):
        """Show test result.
            ::parameter: start_time of kwargs - start time of action (seconds).
        """
#-------------fin de test
        # l'application est finie 
        self.logger.info(unicode('-'*60))
        self.logger.info(unicode('Ran in %f(s)'%((time.time() - kwargs['start_time']))))
        self.logger.info(unicode(self.fonc_message))
        self.logger.info(unicode('return %s\n'%self.rc))
        self.logger.info(unicode('='*60))

    def execute(self, *args, **kwargs):
		"""Test execution.
			::return :
                         0, if test is properly finished,
                         1, otherwise.
		"""
#-----------exécution du test. 
#-----------si une erreur est survenue lors de l’exécution du test, sortie en erreur
        try:
            self.unsafe_execute(*args, **kwargs)
            self.rc = 0
        except BaseException:
                self.rc = 1
        #-------affichage du resultat du test  
        self.tearDown(**kwargs)
        return self.rc

    def unsafe_execute(self, *args, **kwargs):
		"""Generic test execution template.
		"""
        try:
            #---------si l'erreur lors de vérification du prerequis, fin du test
            if self.setUp(*args, **kwargs) > 0 :
                raise Exception('')
        except Exception as err:
            raise
        #----lancement d'exécution du test
		#----si une erreur est survenue lors de l’exécution du test, une exception est levée
        try:
            if self.run(*args, **kwargs) > 0 :
                raise Exception(' ')
        except KeyboardInterrupt:
            self.logger.info('interruption detected')
            raise
        except Exception as err:
            raise
        
