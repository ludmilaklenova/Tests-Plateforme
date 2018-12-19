#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# Synchrotron Soleil
#
# Nom: scanmacro.py
#
#La classe ScanServer lance un scan.
#La classe DataRecorder gere l'instance du device ds_DataRecorder.
########################################################################
"""
Created on 11/08/2017
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""

from devices.tango import DeviceProxy,DataRecorder

#import tools
from scanconfig import Config
import time
import sys
import PyTango


class ScanServer( DeviceProxy):
    '''Generic scan class.
    '''
#scanserver herit de  proxy vers le device de type ds_ScanServer
    
    def __init__(self, type_scan, config_file_name, logger_object) :
        """ Scan server init.
	        ::parameter : type_scan - config name of the scan,
	        ::parameter : config_file_name - name of the file configuration of the scans,
	        ::parameter : logger_object - logger of the logs files.
        """
        
        #initialisation de l'attribut conf avec une config du scan
        try:
            self.conf = Config(type_scan,config_file_name,logger_object)
        except:
            raise
        #initialisation de DeviceProxy
        try:
            DeviceProxy.__init__( self, self.conf.scan_server_name,logger_object)
  
        except :
            self.logger.error(self.error_message.get_error_message())
            raise
        #initialisation de l'attribut storage avec le device ds_DataRecorder
        self.storage = DataRecorder(self.conf.datarecorder_name,logger_object)
        
    def set_config(self, config_object):
        """set scan server configuration.
            ::parameter: config_object - object of type Config.
        """   
        self.conf = config_object
        
    
    def set_attributes(self):
        """set scan values in the scan server attributes.
        """
#-------dp est un attribut de tango.DeviceProxy : proxy vers ScanServer
#-------scan_server_config_attr_values est une list de tuple (attribute_name,value)
        for attr_name,value in self.conf.scan_server_config_attr_values.iteritems() :
                try:
                    self.logger.debug("ScanServer.set_attributes() '%s' = '%s'"%(attr_name,value))
                    self.dp.write_attribute(attr_name,value)
                except Exception, details :
                    self.error_message.set_error_message('WRITE_ATTRIBUTE_ERROR',value,attr_name,str(details))
                    return 1

        try:
            self.dp.write_attribute('recorddata',True)
        except Exception, details :
                    self.error_message.set_error_message('WRITE_ATTRIBUTE_ERROR',True,'recorddata',str(details))
                    return 1
        return 0

    def get_current_nexus_file(self):  
        """get full current nexus file name.
            ::return: full current data file name
        """ 
        return self.storage.get_current_file()
    
    def get_data_root_name(self):
        """get root name of the data in the Nexus file.
            ::return : root name of the data in the Nexus file
        """
        return self.storage.get_nx_entry_name()
    
    def run(self):
        '''The run process.
            ::return : 0, if scan is successfully finished,
                       1, otherwise. 
        '''
        try:
            self.pre_scan()
            if self.scan_conf() == 1:
                return 1
            if self.start() == 1 :
                return 1
            if self.wait() == 1 :
                return 1
            if self.post_scan() == 1 :
                return 1
            
        except KeyboardInterrupt:
            self.error_message.set_error_message('INTERRUPTION_DETECTED')
            self.logger.error("ScanServer.run() : %s"%self.error_message.get_error_message())
            try:
                self.abort_scan()
            except Exception, details :
                self.error_message.set_error_message('ABORT_FAILED', str(details))
            return 1
        except PyTango.DevFailed,e:
            self.error_message.set_error_message('PYTANGO_DEVICE_FAILED_ERROR',str(e))
            self.logger.error("ScanServer.run() : %s"%self.error_message.get_error_message())
            try:
                self.abort_scan()
            except Exception, details :
                self.error_message.set_error_message('ABORT_FAILED', str(details))
            return 1
        return 0 

    def pre_scan(self):
        '''Pre scan action.
        '''
        self.logger.debug('pre scan action')
        #initialisation du devices ds_ScanServer avant le scan
        self.dp.Init()
        time.sleep(0.5)
        #si le device DataRecorder ecrit dans un fichier Nexus, stop ecriture
        if (self.storage.dp.state() in [ PyTango.DevState.RUNNING, PyTango.DevState.MOVING]):
            self.storage.dp.EndRecording()
        self.logger.info("scan server device : %s "%self.dp.name())
        self.logger.info("storage device : %s "%self.storage.dp.name())
        message = "storage : project directory %s, subdirectory %s"%(self.storage.dp.projectdirectory,self.storage.dp.subdirectory)
        self.logger.info(message)
        

    ## Scan configuration
    def scan_conf(self):
        if self.set_attributes() == 1 :
            return 1
        return 0

    def init_time(self):
        return 0

    
    def start(self):
        '''start a scan via the scan server'''
        self.logger.info('start scan')
        self.init_time()
        self.dp.Start()
        time.sleep(0.5)
        if ( self.dp.state() == PyTango.DevState.FAULT ):
            self.error_message.set_error_message('SCAN_SERVER_STATE_FAULT','FAULT')
            self.logger.error("ScanServer.post_scan() : %s"%self.error_message.get_error_message())
            return 1
        if (  self.dp.status().find("Nexus file already exists")!=-1 ):
            self.error_message.set_error_message('DATASTORAGE_FILE_ALREADY_EXIST')
            self.logger.error("ScanServer.start() : %s"%self.error_message.get_error_message())
            return 1
        return 0    


    def wait(self):
        '''wait the end of the scan'''
        try:
            while ( self._ismoving() or self._isstandby() ) :
                time.sleep(.1)
                if self._isstandby():
                    self.info( "-- PAUSE --  ")
                sys.stdout.write( "Progress : %1.2f" % self.dp.scanCompletion+" %   (Scan Remaining Time : " + self.dp.scanRemainingTime + " min)                   \r")
                sys.stdout.flush()
            sys.stdout.write('\n')
            if self._isalarm():
                self.error_message.set_error_message('SCAN_SERVER_STOPPED')
                self.logger.error("ScanServer.wait() : %s"%self.error_message.get_error_message())
                return 1
        except KeyboardInterrupt:
            self.error_message.set_error_message('INTERRUPTION_DETECTED')
            self.logger.error("ScanServer.wait() : %s"%self.error_message.get_error_message())
            try:
                self.abort_scan()
            except Exception, details :
                self.error_message.set_error_message('ABORT_FAILED', str(details))
                self.logger.error("ScanServer.wait() : '%s'"%self.error_message.get_error_message())
            self.post_scan()
            return 1   
        return 0

    def post_scan(self):
        """post scan action"""
        self.logger.info('post scan action')
        if ( self.dp.state() == PyTango.DevState.FAULT ):
            self.error_message.set_error_message('SCAN_SERVER_STATE_FAULT','FAULT')
            self.logger.debug("ScanServer.post_scan() : %s"%self.error_message.get_error_message())
            return 1
        self.logger.info("storage : Nexus file name : %s \n"%self.storage.get_current_file())
        return 0

    def abort_scan(self) :
        """abort scan action"""
        self.logger.info('abort scan')
        self.dp.Abort()
        

