#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# Synchrotron Soleil
#
# Nom: tango.py
#
#La classe DeviceProxy permettant effectuer la connexion avec les devices.
#La classe DataRecorder qui gere l'instance du device ds_DataRecorder.
########################################################################
"""
Created on 11/08/2017
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""


from __future__ import absolute_import
import PyTango

from utils.logger import Logger
from utils.errormessage import ErrorMessage
import datetime
import time
import itertools 
import sys

class DeviceProxy(object):
    '''Manage deviceproxy( "domain/family/member" ).
    '''

    def __init__(self, name,logger_object):
        '''Initialization deviceproxy( "domain/family/member" ).
            ::parameter : name - full name of the tango device, should be of type "domain/family/member",
            ::parameter : logger_object - logger of the logs files.
        '''
        #initialisation de l'attribut message d'erreur
        self.error_message = ErrorMessage()
        
        #initialisation de l'attribut logs
        self.logger = logger_object
        
        # initialisation du nom du device tango 
        self.device_name = name
        
        #initialisation de l'attribut etat du device
        #self.device_state = "unknown" 
        
        #proxy vers le device
        self.dp = None
        
        #verification que le nom du device est correct
        if (len(self.device_name.split('/') )!=3):
            self.error_message.set_error_message('DEVICE_ADDRESS_EXPECTED', name)
            self.logger.error("DeviceProxy._init_ : '%s'"%self.error_message.get_error_message())
            raise
        
        #initialisation de proxy vers le device
        self._init_proxy()

    def _init_proxy(self):
        '''Initialization of the deviceproxy with device_name.
        '''
        try:
            #reference vers le proxy de device tango
            self.dp = self._get_deviceproxy()
        except:
            self.error_message.set_error_message('PROXY_GET_ERROR', self.device_name)
            raise

    def init(self):
        self.dp.Init()
        
    def status(self):
        '''Get the device status.
            ::return : device status
                       ("UNKNOWN",PyTango.DevState.UNKNOWN), if unable to get the device status
        '''
        try:
            return self.dp.status()
        except:
            self.error_message.set_error_message('UNABLE_READ_DEVICE_STATUS',self.dp.state(),self.device_name)
            self.logger.warning("DeviceProxy.status : '%s'"%self.error_message.get_error_message())
            return ("UNKNOWN",PyTango.DevState.UNKNOWN)

    def state(self):
        """Device state. 
           ::return : device state value
        """
        try:
            return self.dp.state()
        except PyTango.DevFailed,e:
            self.error_message.set_error_message('PYTANGO_DEVICE_FAILED_ERROR',str(e))
            self.logger.error("DeviceProxy.state : '%s'"%self.error_message.get_error_message() )
            raise
        except Exception, details:
            self.error_message.set_error_message('DEVICE_STATE_ERROR',str(details))
            self.logger.error("DeviceProxy.state : '%s'"%self.error_message.get_error_message() )
            raise
    
            
    def _get_device_class(self):
        '''Get the device class.
            ::return : device class name 
                       UNKNOWN, if unable to get the device class name
        '''
        try:
            return self.dp.info().dev_class
        except:
            self.error_message.set_error_message('UNABLE_GET_DEVICE_CLASS',self.dp.state(),self.device_name)
            self.logger.warning("DeviceProxy._get_device_class : '%s'"%self.error_message.get_error_message())
            return "UNKNOWN"
        
    def _get_servername(self):
        """Get server name of the device.
           ::return : server name of the device,
                      empty string, otherwise
        """
        #recuperation objet bdd tango
        db = PyTango.Database()
        #recuperation de la liste des servers dans la bdd
        server_list = db.get_server_list()
        server_name = ''
        #pour chaque servers de la liste
        for server in server_list:
            #recuperation de la liste des noms des devices
            lst_devices_address = db.get_device_class_list(server).value_string
            #mise de la liste en lower case
            lst_devices_address_lower = [ i.lower() for i in lst_devices_address]
            #si le nom du device est dans la liste, alors on retourne le nom du serveur
            if self.device_name.lower() in lst_devices_address_lower:
                server_name = server
        return server_name
            
    def _get_deviceproxy(self):
        '''Obtain the deviceproxy with device_name.
        '''
        
        try:
            dev_proxy = PyTango.DeviceProxy( self.device_name )
            dev_proxy.ping()
            return dev_proxy
        except PyTango.DevFailed,e:
            self.error_message.set_error_message('PROXY_FROM_DATABASE_ERROR', str(e))
            raise
        except PyTango.ConnectionFailed,e:
            self.error_message.set_error_message('PROXY_FROM_DATABASE_ERROR', str(e))
            print"DeviceProxy _get_deviceproxy ping ne pass pas !!!!",str(e)
            raise
        except Exception,details:
            self.error_message.set_error_message('PROXY_FROM_TANGO_ERROR',str(details))
            raise
        
    def get_device_name(self):
        '''Get device full name. 
        '''
        return self.device_name 
    
    def get_property_list(self,filtr):
        """Get the list of property names for the device. 
           ::parameter : filtr - allows the user to filter the returned name list. The
            wildcard character is '*'. 
           ::return : the list filled with the property names, 
                      empty list, if not propertys.
        """


        return self.dp.get_property_list(filtr)
    
    def get_property(self,name):
        """Get property values list.
            ::parameter : name - property name
            ::return : the dictionnary filled with the tuple <property name>:<list_values>, 
                      the dictionnary filled with the tuple <property name>:<empty list>, if not property.
        """
        return self.dp.get_property(name)
    
    def get_attribute_list(self):
        """Get device attribute list.
            ::return : list of all device attributes
        """
        return self.dp.get_attribute_list()
    
    def get_error_message(self):
        """Get device error message.
            ::return : device error message string.
        """
        return self.error_message.get_error_message()
    
    def command_inout(self, *args, **kwargs):

        '''Execute a command on a device.
            ::parameters :
            - cmd_name  : (str) Command name.
            - cmd_param : (any) It should be a value of the type expected by the
                          command or a DeviceData object with this value inserted.
                          It can be ommited if the command should not get any argument.
            - green_mode : (GreenMode) Defaults to the current DeviceProxy GreenMode.
                           (see :meth:`~PyTango.DeviceProxy.get_green_mode` and
                           :meth:`~PyTango.DeviceProxy.set_green_mode`).
            - wait       : (bool) whether or not to wait for result. If green_mode
                           is *Synchronous*, this parameter is ignored as it always
                           waits for the result.
                           Ignored when green_mode is Synchronous (always waits).
            - timeout    : (float) The number of seconds to wait for the result.
                           If None, then there is no limit on the wait time.
                           Ignored when green_mode is Synchronous or wait is False.
            ::return     : the result of the command. The type depends on the command. It may be None.
        '''
        try:
            return self.dp.command_inout(*args, **kwargs)
        except Exception,details:
            self.error_message.set_error_message('COMMAND_INOUT_ERROR',self.get_device_name(),str(details))
            raise
    
    def read_attribute(self, attribute_name):
        """Read attribut value from device.
            ::parameter : attribute_name - attribute name,
            ::return : attribute value
        """
        try:
            return self.dp.read_attribute(attribute_name).value
        except Exception,details:
            self.error_message.set_error_message('READ_ATTRIBUTE_ERROR',attribute_name,str(details))
            raise
        
    
    def write_attribute(self, attribute_name,value):
        """Write attribut value.
            ::parameter : attribute_name - attribute name,
            ::parameter:  value - attribute value
        """
        try:
            self.dp.write_attribute(attribute_name,value)
        except Exception,details:
            self.error_message.set_error_message('WRITE_ATTRIBUTE_ERROR',value,attribute_name,str(details))
            raise
            
        
    def write_attributes(self, attributes_values):
        """Write attributs values.
            ::parameter : attributes_values - list of tuples (attribute,value)
        """   
        try:    
            self.dp.write_attributes(attributes_values)
        except Exception,details:
            self.error_message.set_error_message('WRITE_ATTRIBUTES_ERROR',str(details))
            raise

    def wait_spinner(self, wait_time):
        """wait until device state is MOVING.
            ::parameter : wait_time - delta time for wait (minutes)
        """
#------affichage d'un element du cycle dans la boucle
#----- pour montré qu'on attend 
        spinner = itertools.cycle(['-', '/', '|', '\\'])
            
        try:
            self.logger.debug(u"wait for max '%s' minute(s)"%wait_time)   
            time.sleep(1.0)
#-------------------on attend que le device ne soit plus en MOVING ou on attend un period de temps 
            end_time = datetime.datetime.now()+datetime.timedelta(minutes=wait_time)
            while end_time >= datetime.datetime.now() and self._ismoving():
                time.sleep(0.1)
                #affichage l'element du cycle
                sys.stdout.write(spinner.next())
                sys.stdout.flush()
                #-----effacer l'element affiché
                sys.stdout.write('\b')
        except Exception, details :
             self.error_message.set_error_message("Wait error : ",str(details))
             raise  
  
    def __str__ (self):
        '''Show informations with the print command.
            ::return : server and device address for print command.
        '''
        str_msg = ''
        str_msg += 'Server address : %s\n'%self._get_servername()
        str_msg += 'Device address : %s\n'%self.device_name
        return str_msg

    def __repr__(self):
        return self.__str__()

    def stop(self):
        '''Stop device '''
        self.dp.Stop()

    def set_timeout_millis(self, value):
        """set the timeout in milliseconds """
        self.dp.set_timeout_millis(value)
 
    def get_timeout_millis(self):
        """get the timeout in milliseconds """
        return self.dp.get_timeout_millis()
    
    def _isinit(self):
        """return true if the device is in the iinit state, false otherwise """
        return self.dp.state()==PyTango.DevState.INIT

    def _isalarm(self):
        """return true if the device is in the alarm state, false otherwise """
        return self.dp.state()==PyTango.DevState.ALARM

    def _ismoving(self):
        """return true if the device is in the moving state, false otherwise """
        return self.dp.state()==PyTango.DevState.MOVING

    def _isrunning(self):
        """return true if the device is in the running state, false otherwise """
        return self.dp.state()==PyTango.DevState.RUNNING

    def _isstandby(self):
        """return true if the device is in the standby state, false otherwise """
        return self.dp.state()==PyTango.DevState.STANDBY

    def _ison(self):
        """return true if the device is in the on state, false otherwise """
        return self.dp.state()==PyTango.DevState.ON

    def _isoff(self):
        """return true if the device is in the off state, false otherwise """
        return self.dp.state()==PyTango.DevState.OFF

    def _isopen(self):
        """return true if the device is in the open state, false otherwise """
        return self.dp.state()==PyTango.DevState.OPEN

    def _isclose(self):
        """return true if the device is in the close state, false otherwise """
        return self.dp.state()==PyTango.DevState.CLOSE

    def _isdisable(self):
        """return true if the device is in the close state, false otherwise """
        return self.dp.state()==PyTango.DevState.DISABLE

    def _iswaiting(self):
        """return true if the device is waiting ( on or standby state ), false otherwise """
        return self._ison() or self._isstandby()

    def _isfault(self):
        """return true if the device is in the FAULT state, false otherwise """
        return self.dp.state()==PyTango.DevState.FAULT


class DataRecorder(DeviceProxy):
    '''Manage device DataRecorder.
    '''
    def __init__(self,datarecorder_name,logger_object):
        '''Initialization of the class.
            ::parameter : datarecorder_name - name of the DataRecorder device, should be of type "domain/family/member",
            ::parameter : logger_object - logger of the logs files.
        '''
        
        #Initialise la classe tango.deviceproxy
        try:
            DeviceProxy.__init__(self, datarecorder_name,logger_object)
            
        except PyTango.DevFailed,e:
            self.error_message.set_error_message('PYTANGO_DEVICE_FAILED_ERROR', str(e))
            self.logger.error("DataRecorder._init_ : '%s'"%self.error_message.get_error_message() )
            raise
        except Exception, details:
            self.error_message.set_error_message('PYTANGO_DEVICE_FAILED_ERROR', str(details))
            self.logger.error("DataRecorder._init_ : '%s'"%self.error_message.get_error_message() )
            raise

    def set_filename_index(self, nb):
        self.dp.ResetFileNameIndex()
        if (nb>1):
            for i in range(1,nb):
                self.dp.IncFileNameIndex()

    def set_experiment_index(self, nb):
        self.dp.resetexperimentindex()
        if (nb>1):
            for i in range(1,nb):
                self.dp.incexperimentindex()

    def increment_experiment_index(self):
        self.dp.incexperimentIndex()

    def increment_filename_index(self):
        self.dp.IncFileNameIndex()

    def get_experiment_index(self):
        return self.dp.experimentIndex

    def set_subdirectory( self,  txt="" ):
        '''Set sub directory name in the device'''
        if (txt==""):
            print self.dp.subdirectory
        else:
            self.dp.subdirectory=txt

    def set_rootdirectory( self, txt="" ):
        '''Set root directory name in the device'''
        self.dp.SetRootDirectory(txt)

    def get_path( self ):
        '''Get project directory path.
            ::return : project directory path
        '''
        return self.dp.projectdirectory
    
    def wait(self, period):
        """Wait a period minutes.
            ::parameter: period - wait period (minutes)
        """
        try:
            self.logger.info("DataRecorder wait '%s' minutes"%period) 
#-------------------on attend que les dservers demarres
            end_time = datetime.datetime.now()+datetime.timedelta(minutes=period)
            while end_time >= datetime.datetime.now() and self._isrunning():
                        time.sleep(0.5)
            
            
        except Exception, details :
            self.logger.error("Wait time error : '%s'"%str(details)) 
            pass
        
    def get_current_file(self):
        """Get current data file.
           ::return: full current data file name
        """
#-----------on attend la fin de creation du fichier Nexus
        
        while self._ismoving():
            self.logger.debug("DataRecorder creat Nexus file") 
            time.sleep(1.0)
        return self.dp.currentFiles[0]
    
    def get_nx_entry_name(self):
        """get nx entry name value.
            ::return: nxEntryName attribute value
        """
        return self.dp.nxEntryName