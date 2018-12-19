#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
#  Copyright (c) 2017, Synchrotron SOLEIL
#
#  Distributed under the terms of the GNU LGPL.
#
#  The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

"""
Created on 11/08/2017
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""


class ErrorMessage(object):
    
    def __init__(self) :
        """Manage the error message produced at the given moment based on a dictionary of error messages."""
        self.no_error = 0
        self.error    = -1
        self.return_code = self.no_error #contains the code of the last produced message (self.no_error or self.error)
        
        self.messages = {'NO_ERROR'              : "process has normally finished",
                'EXTERNAL_ERROR'                 : "%s",
                'INTERNAL_ERROR'                 : "internal error: %s (%s)",
                'NOT_IMPLEMENTED'                : "'%s' is not yet implemented",
                'DEVICE_ADDRESS_EXPECTED'         : "wrong device address, should be of type domain/family/member : '%s'",
                'PROXY_GET_ERROR'                : "impossible to get a proxy from %s",
                'PROXY_FROM_DATABASE_ERROR'      : "impossible to get a device proxy from the tango database : %s\n",
                'CONNECT_DATABASE_ERROR'         : "cannot connect to Tango database : '%s'",
                'PROXY_FROM_TANGO_ERROR'         : "impossible to get a device proxy from Tango :'%s'",
                'FIND_STARTERS_ERROR'            : "impossible find starters : '%s'",
                'DEVICE_STATE_ERROR'             : "impossible to get the device state : '%s' \n",
                'API_UNSUPPORTED_ATTRIBUTE'       : "wrong attribute : Should be of type domain/family/member[/attribute]",
                'API_DEVICE_NOT_EXPORTED'        : "device server is not running",
                'ALREADY_RUNNING'                : "device server is already running",
                'UNABLE_READ_DEVICE_STATUS'      : "unable to read the status of device '%s' '%s'",
                'UNABLE_GET_DEVICE_CLASS'        : "unable to get the device class : device state '%s', device name '%s'",
		        'SCANSERVER_DEAD'                : "scanserver is dead",
		        'WARNING_STOP_SCAN'              : "wait while stopping scan",
		        'PYTANGO_DEVICE_FAILED_ERROR'    : "PyTango DevFailed error : '%s'",
		        'DATASTORAGE_FILE_ALREADY_EXIST' : "datastorage filename already exist",
		        'SCAN_SERVER_STOPPED'            : "scan server has been stopped",
		        'FILE_NOT_FOUND'                 : "file '%s' is not found ",
                'FILE_NOT_READABLE'              : "file '%s' is not readable",
                'DIRECTORY_NOT_WRITABLE'         : "directory '%s' is not writable",
                'CONFIG_LOAD_ERROR'              : "configuration error : '%s'",
                'FILE_NOT_HDF5FILE'              : "'%s' is not HDF5 file",
                'FILE_NOT_NEXUSFILE'             : "'%s' is not Nexus file",
                'CHECK_NEXUS_FILE_ERROR'         : "check NexusFile error : '%s'",
                'NEXUS_FILE_DATA_ERROR'          : "'%s data is empty",
                'ABORT_FAILED'                   : "abort failed : '%s'",
                'RUNNING_FAILED'                 : "running failed",
                'START_DEVICE_FAILED'            : "start device failed : '%s'",
                'STOP_DEVICE_FAILED'             : "stop device failed : '%s'",
                'KILL_DSERVER_FAILED'            : "hard kill dserver failed : '%s'",
                'INTERRUPTION_DETECTED'          : "interruption detected",
                'SCAN_SERVER_STATE_FAULT'        : "scan server state : '%s'",
                'CONFIG_FILE_NOT_EXIST'          : "config file '%s' does not exist",
                'READ_ATTRIBUTE_ERROR'           : "read attribute error : '%s' - '%s'",
                'WRITE_ATTRIBUTE_ERROR'          : "bad value '%s' of attribute '%s' : %s",
                'WRITE_ATTRIBUTES_ERROR'         : "write device attributes error : %s",
                'COMMAND_INOUT_ERROR'            : "device %s command error : %s"
        
        }
        self.message  = self.messages['NO_ERROR'] # contains the last produced error message

    def get_error_message(self):
        return self.message

    def get_return_code(self):
        return self.return_code

    def set_error_message(self,key, *args): 
        """Constructed the message according to the key 'key' and the arguments 'args'. 
           Modify the attribute self.message with the constructed message.
            Modify self.return_code with the value of self.error.
           ::parameter: key : code of the message in the dictionary of messages,
           ::parameter : args : arguments of the message
        
        """
#---------construit le message selon la clé et les arguments args
           
        if key not in self.messages.keys() : 
            self.message = self.messages['INTERNAL_ERROR']%('Unknown message type (ErrorMessage.set_error_message)', key)
        else :
            self.message = self.messages[key]%(args)

#---------- modifie l'attribut self.return_code    selon la clé 
        self.return_code = self.error

    def set_no_error(self) :
        """Initialize the code of return as "NO_ERROR" and initialize the error message as None. 
        """
        self.return_code = self.no_error
        self.message     = self.messages['NO_ERROR'] # contains the last produced error message
        
    def is_error(self) :
        
        if self.return_code == self.error :
            return True
        if self.return_code == self.no_error:
            return False

