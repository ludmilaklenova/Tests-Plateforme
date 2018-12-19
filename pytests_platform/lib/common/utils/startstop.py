#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# Synchrotron Soleil
#
# Nom: start_stop.py
#
#La classe StartStop permet de lancer ou arreter tous les devices de la base de données.
########################################################################
"""
Created on 02/04/2018
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""

#import tools
import time
import datetime
import sys
import os
import itertools 


class StartStopDevices(object):
    '''start or stop all devices of the database.
    '''
    
    def __init__(self, database_object, starter_class, logger_object) :
        """Initialization of the class.
            ::parameter : database_object - database device of tango,
            ::parameter : starter_class - class of starter,
            ::parameter : logger_object - logger of the logs files.
        """
        self.tango_db = database_object
        self.logger = logger_object
        #self.logger.setVerbose()
        self.starter = starter_class
        self.starters_proxy = None  
        self.message        = "process has normally finished" #dernier message de la class
        self.execution_time = 0.0 #temps d'execution de start ou stop méthodes
        self.state          = 'UNVALID' #état de la classe, valid si la liste des starters self.starters_proxy n'est pas vide
#-------------------recuperation de tous les Starters de la base de données  
        self.starters_proxy = self.get_all_starters()
#----------mise à jours de l'état de la classe par rapport a la liste des starters proxy (vide ou non)    
        self._update_state()
        
    def get_all_starters(self):
        """Get list of Starters.
            ::return: list of devices Starters, if Starters exists in the database,
                      empty list otherwise.
        """
        
        #---------------get all starters
        starters = []
        starter_instances = self.tango_db.get_instances_names('Starter')
        
        for instance in starter_instances:
            self.logger.debug(unicode('found Starter instance : Starter/%s'%instance))
            instance_dservers = self.tango_db.get_devices_list(['Starter/' + instance, 'Starter'])
            for dserver in instance_dservers:
                try:
#-------------------initiation de device Starter
#-------------------ajoute de cette instance de Starter dans la liste des devices Starters                  
                    starters.append(self.starter(dserver, self.logger))
                except Exception,details:
                    self.message = "Error : %s "%str(details)
                    starters = []
                    return starters
        return starters
    
    def _update_state(self):
        """Update class state.
        """
        self.get_state()
        
    def get_state(self):
        """Get class state.
           ::return : class state.
        """
        if self.starters_proxy :
            self.state = 'VALID'
        else :
            self.state = 'UNVALID'
        return self.state
    
    def get_execution_time(self):
        """Get execution time of action.
           ::return : execution time of action.
        """
        return self.execution_time
    
    def get_message(self):
        """get last object message
        """
        return self.message
    
    def get_all_dservers_stopped(self):
        """Get all dservers stopped in the database.
        ::return: dictionary of all stopped dservers in the database, format : {starter_name: list_stopped_dservers}
                  empty dictionary, otherwise
        """
#-------------------si Starter n'est pas en état On, 
#-------------------il y a des dservers arrétés dans la base de données
        all_dservers = {} #par défaut tous les dservers sont en marche
        for starter in self.starters_proxy:
            if starter.get_stopped_dservers():
                all_dservers[starter.get_device_name()] = starter.get_stopped_dservers()
        return all_dservers
    
    def get_all_dservers_running(self):
        """Get all dservers started in the database.
            ::return: dictionary of all started dservers in the database, format : {starter_name: list_started_dservers}
                      empty dictionary, otherwise
        """
#-------------------si Starter n'est pas en état OFF, 
#-------------------il y a des dservers non arrétés dans la base de données
        all_dservers = {} #par défaut tous les dservers sont arretés
        for starter in self.starters_proxy:
            if starter.get_running_dservers():
                all_dservers[starter.get_device_name()] = starter.get_running_dservers()
        return all_dservers
        
    
    def start_all_dservers(self):
        """Start all dservers of the database.
            ::return : 0, if start all dservers is ok,
                       1, otherwise
        """ 
        result = 0
        for starter in self.starters_proxy :
#-------------------start all Starter dservers   
            self.logger.info(unicode("Starter : '%s' start all dservers"%(starter.get_device_name())))               
            if starter.start_all_dservers() == 1 :
                    self.message = "Start all dservers error : '%s'"%(starter.error_message.get_error_message())
                    result = 1
        return result
    
    def stop_all_dservers(self):
        """Stop all dservers of the database.
            ::return : 0, if stop all dservers is ok,
                       1, otherwise
        """ 
        result = 0
        for starter in self.starters_proxy:
            self.logger.info(unicode("Starter : '%s' stop all dservers"%(starter.get_device_name())))
            if starter.stop_all_dservers() == 1 :
                    self.message = "Stop all dservers error : '%s'"%(starter.error_message.get_error_message())
                    result = 1
        return result
    
    def wait(self,period):
        """Wait for period minutes.
           ::parameter : period - number minutes to wait.
        """
        try:
#------affichage d'un element du cycle dans la boucle
#----- pour montré qu'on attend 
            spinner = itertools.cycle(['-', '/', '|', '\\'])
            self.logger.info(unicode("wait for maximum '%s' minutes"%period)) 
#-------------------calcul du temps d'attent
            end_time = datetime.datetime.now()+datetime.timedelta(minutes=period)
#-------------attendre si les starters sont en moving ou le temps maximale  
            time.sleep(1.0)       
            while end_time >= datetime.datetime.now() and any(starter._ismoving() 
                                                              for starter in self.starters_proxy):
                        time.sleep(0.1)
                        #affichage l'element du cycle
                        sys.stdout.write(spinner.next())
                        sys.stdout.flush()
                        #-----effacer l'element affiché
                        sys.stdout.write('\b') 
                
        except Exception, details :
            pass  
        
    def stop(self,wait_time):
        """Stop all dservers in the database.
            ::parameter : wait_time - wait time to stop all dservers,
            ::return : 0, if all dservers are stopped,
                       1, if execution error,
                       2, if process is failed.
        """
        self.execution_time = 0.0
#--------par défaut le resultat est negative 
        result = 1
#---------l'état est unvalid, si on n'as pas trouvé des starters dans la bdd
        if self.get_state().lower() == 'unvalid':
            self.message = "Starters not found in the database : '%s'"%self.message
            self.logger.error(unicode(self.message))
            return result
#----on fixe le debut de l'action
        start_time = time.time() 
#-------------stop all dservers
        if self.stop_all_dservers() == 1 :
            return result
        
#-------------------on attend arret des dservers pour tous les Starters    
        self.wait(wait_time)
#----------si on trouve les dservers non arrétés
        if self.get_all_dservers_running():
            self.message = "Stop dservers error : not all dservers stopped"
            self.logger.error(unicode(self.message))
            result = 2  
            
#-------------------on attend arret des dservers pour tous les Starters 
            self.wait(wait_time/2)
            #------------vérification si les dservers non arrétés existes toujours   
            if  self.get_all_dservers_running():                   
                result = 2   
            else :
                self.message ="process has normally finished"
                result = 0  
        else:
            result = 0
#------------calcul de temps d'execution
        self.execution_time = time.time()-start_time
        return result
        
    def start(self,wait_time):
        """Start all dservers in the database.
            ::parameter : wait_time - wait time to start all dservers,
            ::return : 0, if all dservers are started,
                       1, if execution error,
                       2, if process is failed.
        """
        self.execution_time = 0.0
#--------par défaut le resultat est negative        
        result = 1
#---------l'état est unvalid, si on n'as pas trouvé des starters dans la bdd
        if self.get_state().lower() == 'unvalid':
            self.message = "Starters not found in the database : '%s'"%self.message
            self.logger.error(unicode(self.message))
            return result
#----on fixe le debut de l'action
        start_time = time.time() 
#---------demarrage de tous les dservers  
        if self.start_all_dservers() == 1 :
                return result 
#-------------------on attend que les dservers demarres
        self.wait(wait_time)
        
#--------------si les dservers non démarrés sont detectés
#--------------redemarrage des dservers 
        if self.get_all_dservers_stopped():
            self.message = "Start dservers error : not all dservers started"
            self.logger.info(unicode(self.message))  
            result = 2  
#------------démarrage de tous les dservers non démarrés          
            if self.start_all_dservers() == 1 :
                result = 1 
                return result 
#-------------------on attend que les dservers demarres
            self.wait(wait_time/2)
            
#------------vérification si les dservers stoppées existes toujours   
            if  self.get_all_dservers_stopped():                   
                result = 2   
            else :
                self.message ="process has normally finished"
                result = 0  
#--------------si les dservers sont tous démarrés  
        else:
            result = 0 
#------------calcul de temps d'execution
        self.execution_time = time.time()-start_time
        return result
    
    def start_dserver(self,dserver, wait_time):
        """Start un dserver in the database.
            ::parameter : dserver - dserver to start. Format: <dserver_name>/<instance>
            ::parameter : wait_time - wait time to start dserver.
            ::return : 0, if dserver is started,
                       1, otherwise.
        """
        self.execution_time = 0.0
#--------par défaut le resultat est negative 
        result = 1
        
#-----------flag pour vérifier que le DServer est connue par les Starters
        check_unknown_dserver = True
        
#---------l'état est unvalid, si on n'as pas trouvé des starters dans la bdd
        if self.get_state().lower() == 'unvalid':
            self.message = "Starters not found in the database : '%s'"%self.message
            self.logger.error(unicode(self.message))
            return result
#----on fixe le debut de l'action
        start_time = time.time() 
#-------------start dserver
        for starter in self.starters_proxy:
            if dserver in starter.get_stopped_dservers() :
                check_unknown_dserver = False
                if starter.start_dserver(dserver) == 0:
                    self.logger.info(unicode("Starter '%s' start  DServer %s"%(starter.get_device_name(),dserver)))
                    #-------------------on attend arret des dservers pour tous les Starters    
                    self.wait(wait_time)
                    self.message ="process has normally finished"
                    result = 0
                else :
                    self.message = starter.get_error_message()
                    result = 1
                break
                    
            elif starter.get_running_dservers() and dserver in starter.get_running_dservers():
                check_unknown_dserver = False
                self.logger.info(unicode("DServer %s is already running"%(dserver)))
                result = 0
                break
            elif starter.get_dservers() and dserver in starter.get_dservers():
                check_unknown_dserver = False
                self.logger.info(unicode("DServer %s is never started."%(dserver)))
                result = 0
                break
            
        #-----------si le DServer n'est pas connue par les Servers, erreur
        if check_unknown_dserver :
             self.message = "Start DServer error. DServer %s not recognized by Starters of the database"%(dserver)
        #------------calcul de temps d'execution
        self.execution_time = time.time()-start_time
        return result
    
        
    def stop_dserver(self, dserver, wait_time):
        """Stop un dserver in the database.
            ::parameter : dserver - dserver to stop. Format: <dserver_name>/<instance>
            ::parameter : wait_time - wait time to stop dserver.
            ::return : 0, if dserver is stopped,
                       1, otherwise.
        """
        self.execution_time = 0.0
#--------par défaut le resultat est negative 
        result = 1
        
        #-----------flag pour vérifier que le DServer est connue par les Starters
        check_unknown_dserver = True
        
#---------l'état est unvalid, si on n'as pas trouvé des starters dans la bdd
        if self.get_state().lower() == 'unvalid':
            self.message = "Starters not found in the database : '%s'"%self.message
            self.logger.error(unicode(self.message))
            return result
#----on fixe le debut de l'action
        start_time = time.time() 
#-------------stop dserver
        
        for starter in self.starters_proxy:
            if dserver in starter.get_running_dservers() : 
                check_unknown_dserver = False
                if starter.stop_dserver(dserver) == 0:
                    self.logger.info(unicode("Starter '%s' stop  DServer %s"%(starter.get_device_name(),dserver)))
                    #-------------------on attend arret des dservers pour tous les Starters    
                    self.wait(wait_time)
                    self.message ="process has normally finished"
                    result = 0
                else :
                    self.message = starter.get_error_message()
                    result = 1
                break
            elif starter.get_stopped_dservers() and dserver in starter.get_stopped_dservers():
                check_unknown_dserver = False
                self.logger.info(unicode("DServer %s is already stopped"%(dserver)))
                result = 0
                break
            elif starter.get_dservers() and dserver in starter.get_dservers():
                check_unknown_dserver = False
                self.logger.info(unicode("DServer %s is never started."%(dserver)))
                result = 0
                break
        
        #-----------si le DServer n'est pas connue par les Servers, erreur
        if check_unknown_dserver :
             self.message = "Start DServer error. DServer %s not recognized by Starters of the database"%(dserver)
             self.logger.debug(unicode(self.message))
             result = 0
        #------------calcul de temps d'execution
        self.execution_time = time.time()-start_time
        return result
    