#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################################
# Synchrotron Soleil
#
# Nom: test_generique_common.py
#
#Décrite le scénario générique des tests.
# 
#
########################################################################
"""
Created on 14/08/2018
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""


from __future__ import print_function
import os
import sys
import time

class TestGeneric(object):
    """Base generic test object"""

    logger       = None
    device_proxy = None
    fonc_message = "process has normally finished" #dernier message du test
    var_env      = 'PYTESTS_PLATFORM_ROOT' #le nom de la variable d'environnement
    rc           = 1 # code de retour du test
    
    def get_fonc_message(self):
        return self.fonc_message
    
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def setUp(self, *args, **kwargs):
        pass

    def setEnv(self, **kwargs):
        """Initialize the environment that the test can turn.
           ::return :
                         0, if the environment is set,
                         1, otherwise.
        """
        log_file = kwargs['log_file']
 #-------------on doit travailler avec la bdd Tango donc le host est donné en argument
        os.environ['TANGO_HOST'] = kwargs['tango_host']
               
#-----------Vérification des variables d'environnement nécessaires pour l'application    
        ROOT_DIR = os.getenv(self.var_env)
        
        if not ROOT_DIR :
            self.fonc_message = "'%s' is not found"%self.var_env
            return 1
        elif not os.path.isdir(ROOT_DIR) :
            self.fonc_message = "Directory '%s' is not found"%ROOT_DIR
            return 1
        else :
            PLATFORM_TESTS_COMMON = os.path.join(ROOT_DIR, 'lib', 'python2.7', 'site-packages','pytests_platform','lib','common')
            if not os.path.isdir(PLATFORM_TESTS_COMMON) :
                self.fonc_message = "Directory '%s' is not found"%PLATFORM_TESTS_COMMON
                return 1
            
#------initialisation des variables d'environnement d’exécution 
        sys.path.append(PLATFORM_TESTS_COMMON)
        
#--------------importation des modules
        try:
            from utils.logger import Logger
            from devices.tango import DeviceProxy
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
        try:
            self.unsafe_execute(*args, **kwargs)
            self.rc = 0
        except BaseException:
                self.rc = 1
        #-------affichage du resultat    
        self.tearDown(**kwargs)
        return self.rc

    def unsafe_execute(self, *args, **kwargs):
        try:
            #---------si l'erreur lors de vérification du prerequis, fin du test
            if self.setUp(*args, **kwargs) > 0 :
                raise Exception('')
        except Exception as err:
            raise
        
        try:
            if self.run(*args, **kwargs) > 0 :
                raise Exception(' ')
        except KeyboardInterrupt:
            self.logger.info('interruption detected')
            raise
        except Exception as err:
            raise
        
    def create_proxy_obj(self,device_name):
        proxy_obj = None
        try:           
            proxy_obj = self.device_proxy(device_name,self.logger)            
        except Exception, details :
           self.fonc_message = "Error device %s : %s "%(device_name,str(details))
        
        return proxy_obj
                    
    def read_prop_and_check_not_empty(self,device_proxy_obj, property_name):        
        properties_dict = []
        if not device_proxy_obj:
            self.fonc_message = "Device proxy object is empty"
            return properties_dict
        
        try:
            # Lecture de la property 
            properties_dict = device_proxy_obj.get_property(property_name)
            properties_dict = properties_dict[property_name]           
            
            #------------vérification que la propriete existe
            #---------sinon sortie en erreur, fin de test
            if not properties_dict :
                self.fonc_message = "Property %s/%s is empty"%(device_proxy_obj.get_device_name(),property_name)

        except Exception, details : 
            self.fonc_message = "Error device  %s : %s "%(device_proxy_obj,str(details))
   
        return properties_dict
    
    def call_command_inout(self,device_proxy_obj,cmd_name,time_sleep=None):
        success = False
        
        if not device_proxy_obj:
            self.fonc_message = "Device proxy object is empty"
            return success        
        try:           
            device_proxy_obj.command_inout(cmd_name)
            time.sleep(time_sleep == None and 0.3 or time_sleep)    
            success = True         
        except Exception, details :
           self.fonc_message = "Error device %s : %s "%(device_proxy_obj.get_device_name(),str(details))            
       
        return success
