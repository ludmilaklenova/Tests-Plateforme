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

from __future__ import absolute_import
import sys
from IPython.terminal.embed import InteractiveShellEmbed
import ConfigParser
from utils.logger import Logger
from utils.errormessage import ErrorMessage


class Config(object):
    """Manage file scan config """
    
    def __init__(self, type_scan, config_file_name, logger_object) :
        '''Initialize Config.
            ::parameter: type_scan - the name of the scan in the configuration file,
            ::parameter: config_file_name - absolute path of the configuration file,
            ::parameter : logger_object - logger of the logs files.
        '''
        #parser du fichier de configuration
        self.parser = None
        #initialisation du shell interactive
        self.shell =  InteractiveShellEmbed()
        #un seul shell doit etre cree 
        self.shell.dummy_mode = True
        #nom du device de type ds_ScanServer
        self.scan_server_name = ''
        #nom du device de type ds_DataRecorder
        self.datarecorder_name = ''
        #dictionnaire qui contient la configuration du scan
        self.scan_server_config_attr_values = {}
        #initialisation de l'attribut logs
        self.logger = logger_object
        #initialisation de l'attribute message d'erreur
        self.error_message = ErrorMessage()
        
        #lire la configuration du scan <type_scan> dans le fichier configuration config_file_name
        #initialisa tous les attributs de la class
        self.load(type_scan, config_file_name)

    def load( self,config_name ,filename):
        '''Read scan configuration. Initialize class attributes.
            ::parameter : config_name - the name of the scan in the configuration file,
            ::parameter: filename - absolute path of the configuration file.
        '''
        try:
            self.parser = ConfigParser.ConfigParser()
            #lecture du fichier
            self.parser.read(filename)
            #dans la section <global> recuperation de la valeur <scan_server_name>
            self.scan_server_name = self.parser.get('global','scan_server_name' )
            #dans la section <global> recuperation de la valeur <datarecorder_device_name>
            self.datarecorder_name = self.parser.get('global','datarecorder_device_name')
            #lecture de la configuration du scan comme un dictionnaire
            self.scan_server_config_attr_values = dict(self.parser.items(config_name))
            #evaluation de chaque valeur de chaque attribute du configuration
            for attr,value in self.scan_server_config_attr_values.iteritems():
                self.scan_server_config_attr_values[attr] = self.shell.ev(value)
              
        except Exception, details:
            self.error_message.set_error_message('CONFIG_LOAD_ERROR',str(details))
            self.logger.error("Config.load : '%s'"%self.error_message.get_error_message())
            raise
    



