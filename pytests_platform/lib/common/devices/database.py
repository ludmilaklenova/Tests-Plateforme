#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# Synchrotron Soleil
#
# Nom: database.py
#
#La classe Database permettant gérée la base de données Tango.
########################################################################
"""
Created on 14/11/2017
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""

from __future__ import print_function
import PyTango
import os

from utils.logger import Logger
from utils.errormessage import ErrorMessage
from devices.starter import Starter 

class Database(object):
    '''Manage database Tango.'''

    def __init__(self, tango_host,logger_object):
        '''Initialization database device
            ::parameter : tango_host - Tango database host and port. Format : <host>:<port>,
            ::parameter : logger_object - logger of the logs files.
        '''

        #initialisation de l'attribut message d'erreur
        self.error_message = ErrorMessage()
        
        #initialisation de l'attribut logs
        self.logger = logger_object
        #initialisation de l'attribut tango_db comme la connexion avec
        #le host de la base de données
        os.environ['TANGO_HOST']  = tango_host
        try:
            self.tango_db = PyTango.Database()
            self.logger.debug("Tango Database : Host '%s', Port '%s'"%(self.tango_db.get_db_host(),self.tango_db.get_db_port()))	
        except Exception, details :
            self.error_message.set_error_message('CONNECT_DATABASE_ERROR', str(details))
            raise
        #initialisation de l'attribut db_device comme la connexion avec le device de type database
        if not self._init_db_device():
            raise
        
    def _init_db_device(self):
        """Test tango database device connection. 
            ::return: True , if tango database device is running,
                      False, otherwise
        """
    
        db_device_names = ['sys/database/dbds1',
                       'sys/database/dbds',
                       'sys/database/dbds2'
                       ]    
        for db_device_name in db_device_names:
            try:
                self.logger.debug("Checking for database device '%s'..."%db_device_name)
                self.db_device = PyTango.DeviceProxy(db_device_name)
                
                self.logger.debug("Database device state is '%s'"%self.db_device.state())
                return True
            except :
                self.logger.debug(" Check [NOK]")
                self.db_device = None      
        if not self.db_device:
            self.logger.error("check_db_device(): Cannot find a running database device.")
            return False
   
    def get_host(self):
        return self.tango_db.get_db_host()
    
    def get_port(self):
        return self.tango_db.get_db_port()
    
    def get_instances_names(self,dserver):
        """Get instances names list a dsever.
            ::parameter: dsever - dserver name,
            ::return: dserver instances names list.
        """
        return self.db_device.DbGetInstanceNameList(dserver)  
    
    def get_server_list(self):
        return self.tango_db.get_server_list()
    
    def get_server_class_list(self,server):
        return self.tango_db.get_server_class_list(server).value_string
     
    def get_device_name(self,server,server_class):
        return self.tango_db.get_device_name(server,server_class).value_string
    
    def get_devices_list(self,info_dserver):  
        """Get devices list a dserver.
            ::parameter: info_dserver - list of format [<dserver_name/instance>,dserver_class],
            ::return: devices list a dserver.
        """
        return self.db_device.DbGetDeviceList(info_dserver)

    def get_all_starters(self):
        """Get list of devices Starter.
            ::return:   list of devices Starter,
                        empty list otherwise.
        """        
#---------------get all starters
        starters = []
        starter_instances = self.get_instances_names('Starter')
        
        for instance in starter_instances:
            self.logger.debug(unicode('found Starter instance : Starter/%s'%instance))
            instance_dservers = self.get_devices_list(['Starter/' + instance, 'Starter'])
            for dserver in instance_dservers:
                try:
#-------------------initiation de device Starter
#-------------------ajoute de cette instance de Starter dans la liste des devices Starters                  
                    starters.append(Starter(dserver, self.logger))
                except Exception,details:
                    self.error_message.set_error_message('FIND_STARTERS_ERROR', str(details))
                    starters = []
                    return starters
        return starters
    def get_instance_name_list(self, dserver_name):
        """Get dserver instances names list.
            ::parameter: dserver_name - dserver name. Format : <dserver_name>.
            ::return : instances names list.
        """
        return self.tango_db.get_instance_name_list(dserver_name).value_string
    
    def delete_server(self, dserver):
        """Delete server from database. 
            ::parameter: dserver - full dserver name. Format: <dserver_name>/<instance>
        """
        self.tango_db.delete_server(dserver)
        