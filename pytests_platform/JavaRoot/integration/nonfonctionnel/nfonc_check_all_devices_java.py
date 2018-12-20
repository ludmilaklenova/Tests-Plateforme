#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# Synchrotron Soleil
#
# Nom: nfonc_check_all_devices_java.py
#
#Start tous les devices de la base de données Tango via les Starters
#
########################################################################
"""
Created on 14/11/2017
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""

import argparse
import os
import time
import datetime
import glob
import pytest
import sys
import itertools 
import requests
import PyTango
from test_generic_common import TestGeneric


class TestStartALLDevicesJava(TestGeneric):
    """Configuration class for check if all DServers are started in the database"""
    prog_version              = '1.0' #version de l'application
    rc                        = 0 # code de retour de l'application
    ns                        = None #parser
    device_proxy              = None #device proxy
    starter                   = None #device Starter
    database                  = None #device Database
    logger                    = None #device Logger
    start_stop_devices        = None #device StartStopDevices
    fonc_message              = "process has normally finished" #dernier message de l'application
    var_env                   = 'PYTESTS_PLATFORM_ROOT' #le nom de la variable d'environnement
    starters_proxy            = [] #list of dservers Starters
    stop_devices_period       = 2 # period d'attente d'arret de tous les devices (minutes)
    tango_db                  = None #objet Database, connexion avec la base de données
    all_devices_file_name     = "all_devices_java_database.txt" #format du nom du fichier de sauvegarde de tous les devices présentes dans les Starters
    devices_without_property  = "devices_java_without_propertys.txt" #nom du fichier de sauvegarde des devices sans les proprietes
    backup_file               = None #le nom absolu du fichier de sauvegarde des devices sans les proprietes
    all_devices_file          = None #le nom absolu du fichier de sauvegarde  de tous les devices decrites dans les Starters
    
        # define command line parser
    parser = argparse.ArgumentParser(prog='nfonc_check_all_devices_java', description="Start devices options")
    parser.add_argument('--version', action='version', version='%(prog)s  version ' + prog_version, help ="nfonc_check_all_devices_java version")
    parser.add_argument('--log_file',default='/tmp/Root_JAVA/StartAllDevices/logs/start_devices_java.log',type=str,help="Logs file. Default : /tmp/DeviceRoot_JAVA/StartAllDevices/logs/start_devices_java.log")
    parser.add_argument('--output_dir',default='/tmp/Root_JAVA/StartAllDevices/output',type=str,help="Backup devices tests results directory. Default : /tmp/DeviceRoot_JAVA/StartAllDevices/output")
    parser.add_argument('--tango_host',required=True,help="Tango database host and port. Format : host:port")
    parser.add_argument('--wait_time',default=20.0,type=float,help='wait time for start all dservers (minutes). Default = 20 minutes') 
          
        
    def setEnv(self,**kwargs): 
        """Initialize the environment that the application can turn.
                   :: return :
                         0  if the environment is set up,
                         1 otherwise.
        """
        #----------analyse syntaxique et sémantique de la ligne de commande 
        try :
            self.ns = self.parser.parse_args() #Les options de la ligne de commande
        except Exception, details :
            self.fonc_message = "Error : %s "%str(details)
            return 1

        #-------------on doit travailler avec le tango host donnés en argument
        #----mise en place de l'environnement des tests    
        #------si l'erreur, fin de tests
        if TestGeneric.setEnv(self, tango_host=self.ns.tango_host,log_file=self.ns.log_file)== 1 :
                print(self.fonc_message)
                return 1

#--------------importation des modules
        try:
            from devices.database import Database 
            from devices.starter import Starter 
            from utils.startstop import StartStopDevices 
            #-------initialisation de l'attribut starter
            self.starter      = Starter
#-------initialisation de l'attribut database
            self.database     = Database
#-------initialisation de l'attribut 
            self.start_stop_devices = StartStopDevices 
        except Exception, details :
            self.fonc_message = "Import error : '%s'"%str(details)
            return 1

#----------------si le répertoire du resultat de test n'existe pas, 
#----------------création

        if not os.path.isdir(self.ns.output_dir):
            try:
                os.makedirs(self.ns.output_dir)
            except Exception, details :
                self.fonc_message = "Error : %s "%str(details)
                return 1    
            
#----------------si le fichier de sauvegarde de la liste des devices sans les proprietes existe
#----------------suppression
        self.backup_file = "%s/%s"%(self.ns.output_dir, self.devices_without_property)
        self.logger.info("")
        self.logger.info(unicode('devices without property file : %s'%self.backup_file))
        if os.path.isfile(self.backup_file):
            try:
                os.remove(self.backup_file)
            except Exception, details :
                self.fonc_message = "Error : %s "%str(details)
                return 1 
            
#----------------si les fichiers de sauvegarde de tous les devices de la base de données existes
#---------------- suppression 
        all_devices_files = glob.glob('%s/%s*'%(self.ns.output_dir,self.all_devices_file_name))
        
        for device_file in all_devices_files :
            try:
                os.remove(device_file)
            except Exception, details :
                self.fonc_message = "Error : %s "%str(details)
                return 1 
#-------------création du nom absolu du fichier de sauvegarde de tous les devices de la base de données
        self.all_devices_file = '%s/%s'%(self.ns.output_dir,self.all_devices_file_name)
        self.logger.info(unicode('all dservers file : %s'%self.all_devices_file))
        self.logger.info(unicode('log file : %s '%self.ns.log_file))
        
        return 0
    
    def check_dserver_name(self,dserver_name):
        """Check if dserver name is Starter or Database.
           ::parameter: dserver_name - dserver name. Format <dserver_name>/<instance>.
           ::return: True, if Starter or Database not in the dserver name,
					 False, otherwise.
        """
        if ('starter/' not in dserver_name and 'database/' not in dserver_name and 'compactpcicrate' not in dserver_name):
            return False
        else:
            return True  
         
    def backup_data(self,backup_file_name, all_devices_file):
        """Save full names of the devices without property and all devices States Status in the files.
           ::parameter: backup_file_name - file name of the backup devices without property,
           ::parameter: all_devices_file - file name of the backup of list dservers.
        """
        
#----------------recuperation de la liste des dservers dans la base de données
        servers_list = self.tango_db.get_server_list()
        
        
#-------------initialisation de la liste des devices sans les proprietes
        devices_without_property = []
        
#-------------initialisation du dictionnaire de tous les devices de la bdd avec les tuple <nom_du_device> : <state> 
        devices_states           = {}
        
#-------------remplissage de la liste de tous les dservers de la base de données 
        all_dservers      = [server for server in servers_list if not self.check_dserver_name(server.lower())]
        all_dservers.sort()
        
#-----------------pour chaque dserver
        for server in all_dservers :
#------------------recuperation de la liste des class
            server_class_list= self.tango_db.get_server_class_list(server) 
#------------------recuperation de la liste des noms des devices pour chaque class de dserver
            for server_class in server_class_list :
                devices_names_list = self.tango_db.get_device_name(server,server_class)
#-----------------si un device n'a pas des proptietes, ajoute dans la liste 
#-----------------des devices sans les proprietes
                for device_name in devices_names_list :
                    try:
#-----------------connextion avec le device
                        device = PyTango.DeviceProxy(device_name)
#-----------------si le device n'as pas de propriete, ajoute dans la liste le nom de ca class
                        if not device.get_property_list('*'):
                            devices_without_property.append(unicode('%s\n'%server_class.lower()))
                        try :
                            devices_states[device_name] = device.state()
                        except Exception :
                            devices_states[device_name] = 'NON_EXPORTED'
                            pass
                    except Exception,details:
                        self.fonc_message = "Error : %s "%str(details)
                        self.logger.error(self.fonc_message)
                        pass  
                                              
#------------si la liste des classes des devices sans les proprietes n'est pas vide
        if devices_without_property : 
#-----------élimination des doublons dans la liste
            devices_without_property = set(devices_without_property)
            
            #-----------sauvegarde dans le fichier temporaire
            
            with open(backup_file_name, "w") as fname:   
                    fname.write("#Devices without propertys - %s \n"%datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S"))
                    for class_name in devices_without_property:
                        fname.write("%s"%class_name)                            
#----------sauvegarde de la liste de tous les dservers de la base de données avec leur etat
#-----------avec le format: <device_name>;<etat>
        with open(all_devices_file, "w") as devices_fname:  
            devices_fname.write('#LIST DEVICES WITH STATES - %s \n'%datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S"))
            for device, state in devices_states.iteritems() :
                    devices_fname.write(unicode('%s;%s\n'%(device,state)))
       
        
    def setUp(self, *args, **kwargs):
        """Stop all dservers before a test. Ping database and starters dservers.
            ::return : 0,if all actions ok,
                       1, if execution error.
        """ 
        self.logger.debug(unicode("test set up"))
        
#---------------initiation de la base de données Tango
        try:
            self.tango_db = self.database(self.ns.tango_host,self.logger)
        except Exception,details:
            self.fonc_message = "Error : %s "%str(details)
            return 1
        
#-------initialisation de l'attribut start_stop
        try:
            self.start_stop   = self.start_stop_devices(self.tango_db, self.starter, self.logger)
        except Exception, details :
            self.fonc_message = 'Error : %s'%str(details)
            return 1
        
        if self.start_stop.get_state() == 'UNVALID':
            self.fonc_message = self.start_stop.get_message()
            return 1 

        return 0
         
    def check_stopped_dservers(self):
        """Check if all DServers are stopped in the database.
        ::return : 0, if test is passed,
                   1, if test is failed.
        """
        self.rc             = 1 # code de retour de l'application 
        
#-----------récuperation de la liste des dservers non démarrés
        stopped_servers = self.start_stop.get_all_dservers_stopped()
        #--------si tous les servers sont démarrés, test OK
        if not stopped_servers :
            self.rc = 0
        else :
            self.rc = 1
            self.fonc_message   = "stopped devices are detected in the database." #dernier message de l'application
#----------------logs la liste de ces dservers
            for starter_name,list_stopped_servers in stopped_servers.iteritems():
                    self.logger.debug(unicode("Starter device '%s' : printing stopped servers..."%starter_name))
                    self.logger.debug(unicode('\n'.join(str(p) for p in list_stopped_servers))) 

#------------sauvegarde des données de la fin du test
        self.backup_data(self.backup_file,self.all_devices_file)  
        return self.rc
    
    def run(self,args,test=None,test_argument=None, start_time=-1):
        """Execute a fonctionnel test.
             ::parameter: test - executed fonctionnel test,
             ::parameter: test_argument - fonctionnel test argument,
             ::parameter: start_time - test start time
             ::return : 0, if test is passed,
                        1, if test is failed.
        """
        
        self.logger.debug(u"test start")
        
        
        #----------éxécution du test fonctionnel
        #--------avec un argument, si existe
        #--------récuperation du code de retour du test
        if test_argument :
            result = test(test_argument) 
        else :
            result = test() 
        
        self.logger.debug(u"test stop")
        return  result
    
       
    def test_start_all_dservers(self):  
        """Launch test
        """
        #----mise en place de l'environnement des tests    
        #------si l'erreur, fin de tests
        
        if self.setEnv()== 1 :
            assert 1==0,self.get_fonc_message()
            
        #----------appel du test et vérification du resultat du test
       
        assert self.execute(None,test=self.check_stopped_dservers,
                            start_time =time.time()) == 0,self.get_fonc_message()    

    
if __name__ == '__main__':   
#------------on cherche le chemin absolu du script qu'on lance
    script_name = os.path.abspath(__file__)
#--------------pytest ne doit pas écrire dans le cache
    os.environ['PYTEST_ADDOPTS'] = '-p no:cacheprovider' 

#---appel du module pytest 
    return_code = pytest.main([script_name,"-vv","--capture=no","--tb=no","--no-print-logs"], plugins=[TestStartALLDevicesJava()])
#--fin des tests avec le code de retour du pytest           
    sys.exit(return_code) 
    