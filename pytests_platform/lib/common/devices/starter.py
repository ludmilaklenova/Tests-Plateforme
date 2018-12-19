#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# Synchrotron Soleil
#
# Nom: starter.py
#
#La classe Starter gere l'instance du device Starter.
########################################################################
"""
Created on 16/11/2017
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""


from tango import DeviceProxy

class Starter( DeviceProxy):
    '''Generic Starter class.
    '''
    
    def __init__(self, starter_name, logger_object) :
        """ Starter init.
            ::parameter : starter_name - full name of the Starter device, should be of type "domain/family/member",,
            ::parameter : logger_object - logger of the logs files.
        """
        #initialisation de DeviceProxy
        try:
            DeviceProxy.__init__( self, starter_name,logger_object)
            
        except :
            self.logger.error(self.error_message.get_error_message())
            raise
        
    def starter_init(self):   
        """Init device starter
        """ 
        self.dp.Init()
        
    def get_error_message(self):
        """Get last error message.
        """
        return self.error_message.get_error_message()
        
    def get_running_dservers(self):
        '''Get starter tuple of running servers.
            ::return : tuple of running servers,
                       empty tuple, otherwise
        '''
        if self.dp.RunningServers :
            result = self.dp.RunningServers
        else :
            result = ()
        return result
    
    def get_stopped_dservers(self):
        '''Get starter tuple of stopped servers.
            ::return : tuple of stopped servers,
                       empty tuple, otherwise
        '''
        if self.dp.StoppedServers :
            result = self.dp.StoppedServers
        else :
            result = ()
        return result
     
    def get_dservers(self):
        '''Get starter list of servers.
            ::return : list of all starter servers,
                       empty list, otherwise
        '''
        return list(self.dp.Servers)
    
    def hardkillserver(self, dserver_name):
        """Hard kill dserver.
            ::parameter : dserver_name - name of the dserver. Format: <dserver_name>/<instance>
            ::return : 0, if kill dserver,
                      1, otherwise
        """
        try:
            self.dp.hardkillserver(dserver_name)
        except Exception,details:
            self.error_message.set_error_message('KILL_DSERVER_FAILED', str(details))
            return 1
        return 0
    
    def start_dserver(self,dserver_name):
        """Start a device.
           ::parameter: dserver_name - dserver name for start. Format: <dserver_name>/<instance>
           ::return : 0, if start dserver,
                      1, otherwise
        """
        try:
            self.dp.DevStart(dserver_name)
        except Exception,details:
            self.error_message.set_error_message('START_DEVICE_FAILED', str(details))
            return 1
        return 0
        
    def stop_dserver(self,dserver_name):
        """Stop a device.
           ::parameter: dserver_name - dserver name for stop
           ::return : 0, if stop dserver,
                      1, otherwise
        """
        try:
            self.dp.DevStop(dserver_name)
        except Exception,details:
            self.error_message.set_error_message('STOP_DEVICE_FAILED', str(details))
            return 1
        return 0
        
    def start_all_level_dservers(self,level):
        """Start all devices of the level.
           ::parameter: level - number of run level to start dservers
           ::return : 0, if start all dservers of the level,
                      1, otherwise
        """   
        result = 0 
        try:
                self.logger.debug("Start dservers for Starter '%s',level '%s'"%(self.get_device_name(),str(level)))
                self.dp.DevStartAll(level)
        except Exception,details:
                self.error_message.set_error_message('START_DEVICE_FAILED', str(details))
                self.logger.error(self.error_message.get_error_message())
                result = 1
        return result
    
    def start_all_dservers(self):
        """Start all dservers of the starter.
           ::return : 0, if start all dservers of the starter,
                      1, otherwise
        """
        result = 0
        for runlevel in [1,2,3,4,5]:
            if self.start_all_level_dservers(runlevel)==1:
                result = 1
        return result
    
    def stop_all_level_dservers(self,level):
        """Stop all devices of the level.
           ::parameter: level - number of level to stop dservers
           ::return : 0, if stop all dservers of the level,
                      1, otherwise
        """  
        result = 0 
        #vérification que State du Starter est OFF-> tous les devices sont déjà arretés 
        if   self._isoff():
            return result
        try:
                self.dp.DevStopAll(level)
        except Exception,details:
                self.error_message.set_error_message('STOP_DEVICE_FAILED', str(details))
                self.logger.error(self.error_message.get_error_message())
                result = 1
        return result
    
    def stop_all_dservers(self):
        """Stop all dservers of the starter.
           ::return : 0, if stop all dservers of the starter,
                      1, otherwise
        """
        result = 0
        for level in [1,2,3,4,5]:
            if self.stop_all_level_dservers(level)==1:
                result = 1
        return result
    
    