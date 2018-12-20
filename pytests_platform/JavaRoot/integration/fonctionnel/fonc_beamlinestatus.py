#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################################
# Synchrotron Soleil
#
# Nom: fonc_beamlinestatus.py
# Vérification d’échange correct des données entre le device maitre 
# et le device sous-jacent.
#
########################################################################
"""
Created on 24/08/2018
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""

import pytest
import os
import sys
import time
import datetime
import argparse
import itertools 
from test_generic_common import TestGeneric

class FoncBeamlineStatus(TestGeneric):
    def __init__(self):
        """Configuration class for functional tests"""
        self.prog_version                 = '1.0' #version de l'application
        self.ns                           = None #parser
        self.device_beamline_status       = None #proxy vers le device de type BeamlineStatus
        self.attribute_name               = None #nom de l'attribute du device sous-jacent 
        self.monitored_device             = None #proxy vers le device sous-jacent
        self.property_context_variables   = 'contextVariables' #nom de la propriete du device de type BeamlineStatus
        self.beamline_status_attribute    = 'contextvalidity' #nom de l'attribute du device de type BeamlineStatus
                        
        # define command line parser
        self.parser = argparse.ArgumentParser(prog='fonc_beamlinestatus', description="Options")
        self.parser.add_argument('--version', action='version', version='%(prog)s  version ' + self.prog_version, help ="fonc_beamlinestatus version")
        def_log_file='/tmp/DeviceRoot_JAVA/TestsFonc/logs/fonc_beamlinestatus.log'
        self.parser.add_argument('--log_file',default=def_log_file,type=str,help="Logs file. Default : " + def_log_file)
        self.parser.add_argument('--tango_host',required=True,help="Tango database host and port. Format : host:port")
        
        #----------analyse syntaxique et sémantique de la ligne de commande 
        #------si l'erreur, fin de tests
        try :
            self.ns = self.parser.parse_args() #Les options de la ligne de commande
        except Exception, details :
            self.fonc_message = "Error : %s "%str(details)
            sys.exit(1)
            
        #----mise en place de l'environnement des tests    
        #------si l'erreur, fin de tests
        if self.setEnv(tango_host =self.ns.tango_host ,log_file=self.ns.log_file)== 1 :
            print(self.fonc_message)
            sys.exit(1)
                
    def setUp(self, device_beamline_status, **kwargs):
        """Set up actions.
            ::parameter: device_beamline_status - full BeamlineStatus device name,
            ::return : 0, if all actions ok,
                       1, if execution error.
        """ 
        self.fonc_message = "process has normally finished"
        self.logger.debug(unicode("test set up"))
        self.logger.debug(unicode("Init BeamlineStatus device"))
        self.rc = 1
        
        #------------création du proxy du device de type BeamlineStatus
        self.device_beamline_status = self.create_proxy_obj(device_beamline_status)
        if not self.device_beamline_status:
            return self.rc
        #-------------recuperation des proprietes du device de type BeamlineStatus
        context_variables = self.read_prop_and_check_not_empty(self.device_beamline_status,self.property_context_variables)
        if not context_variables :
            return self.rc
        context_variables = context_variables[0]

        #-----récuperation des noms du device sous-jacent et de son attribute
        #-----récuperation du nom du device sous-jacent en format : <nom_commande :full_device_name/attribute_name>
        full_device_name    = context_variables.rpartition('/')[0]
        full_device_name    = full_device_name.rpartition(':')[2]
        #-----récuperation du nom de l'attribute du device sous-jacent en format : <nom_commande :full_device_name/attribute_name>
        self.attribute_name = context_variables.rpartition('/')[2]
        
        self.logger.debug("Monitored device %s : Initialization"%full_device_name)
        #-------------initialisation du device sous-jacent
        self.monitored_device = self.create_proxy_obj(full_device_name)
        if not self.monitored_device:
            return self.rc
        if not self.call_command_inout(self.monitored_device,"Init"):
            return self.rc 
        #----------vérification q'après initialisation le device sous-jacent n'est pas en FAULT
        if self.monitored_device._isfault() :
            self.fonc_message = "Error device %s : state is FAULT "%full_device_name
            return self.rc
        
        #------------initialisation du device de type BeamlineStatus
        self.logger.debug("device BeamlineStatus %s : Initialization"%device_beamline_status)
        if not self.call_command_inout(self.device_beamline_status,"Init"):
            return self.rc
       
        #----------vérification q'après initialisation le device BeamlineStatus n'est pas en FAULT
        if self.device_beamline_status._isfault() :
            self.fonc_message = "Error device %s : state is FAULT "%device_beamline_status
            return self.rc
        

        self.rc = 0 
        self.logger.debug("BeamlineStatus state is '%s' : '%s'"%(self.device_beamline_status.state(),self.device_beamline_status.status()))
        return self.rc
    
    def check_context(self,data,expected_result):
        """Execute a false context test of BeamlineStatus.
              data - monitored device attribute value.
             ::return :  0, if test is passed,
                         1, if test is failed.
        """
        self.logger.info(u"Test : check context")
        self.logger.debug(u"monitored device attribute '%s' value is '%s', expected_result is '%s' "%(self.attribute_name,str(data),str(expected_result)))
        self.rc = 1
        #------écrire une valeur sur le device sous-jacent qui met le booléen  BeamlineStatus.contextvalidity à False  
        try :
             self.monitored_device.write_attribute(self.attribute_name,data)
             #---------on attend la fin de l'action 
             time.sleep(0.3) 
        except     Exception: 
            self.fonc_message = "Error device  %s : %s "%(self.monitored_device.get_device_name(),self.monitored_device.get_error_message())
            return self.rc 
        
        #------------vérification que BeamlineStatus.contextvalidity est False
        try :
            #------------lecture de l'attribute
            test_result = self.device_beamline_status.read_attribute(self.beamline_status_attribute)
            self.logger.debug(u"check context : test result is '%s', expected result is '%s'"%(str(test_result),str(expected_result)))
            if not (test_result == expected_result):
                self.fonc_message = "Test device %s failed, contextvalidity is %s, expected False "%(self.device_beamline_status.get_device_name(),str(test_result))
                return self.rc
        except     Exception: 
            self.fonc_message = "Error device  %s : %s "%(self.device_beamline_status.get_device_name(),self.self.device_beamline_status.get_error_message())
            return self.rc
        self.rc = 0
        return self.rc
    
    def run(self, device_beamlinestatus_name,test=None,test_data=None,test_expected_result=None,start_time=-1):
        """Execute a fonctionnel test.
             ::parameter: device_beamlinestatus_name - full device name of BeamlineStatus dserver,
             ::parameter: test - executed fonctionnel test,
             ::parameter: test_data - data for test execution,
             ::parameter: test_expected_result - expected test result,
             ::parameter: start_time - test start time
            ::return : 0, if test is passed,
                          1, if test is failed.
        """
        self.logger.debug(u"test start")
        self.logger.debug(u"Device BeamlineStatus name : %s"%device_beamlinestatus_name)
        
        #----------éxécution du test fonctionnel
        #--------avec un argument, si existe
        #--------récuperation du code de retour du test
        if test_data :
            self.rc = test(test_data, test_expected_result) 
        else :
            self.rc = test() 
        
        self.logger.debug(u"test stop")
        return  self.rc
    

class TestBeamlineStatus(object):    
        """Launch all tests of BeamlineStatus.
        """
        #----------création de l'objet qui doit executer les tests
        tests_fonctionnels = FoncBeamlineStatus()
        
        #----------parametrisation et execution du test
        @pytest.mark.parametrize("data_fixture,expected_result_fixture",[(60,True),(40,False)])               
        def test_calcul_context(self,device_beamlinestatus_name,data_fixture,expected_result_fixture):
            """Launch a change all devices states test.
                ::parameter : device_beamlinestatus_name - full device name of BeamlineStatus dserver,
                ::parameter : data_fixture - monitored device attribute value,
                ::parameter : expected_result_fixture - expected BeamlineStatus context validity result.
                ::return : True, if test is passed,
                           False, otherwise
            """
            #----------appel du test et vérification du resultat du test
            assert self.tests_fonctionnels.execute(device_beamlinestatus_name,
                                                test=self.tests_fonctionnels.check_context,
                                                test_data=data_fixture,
                                                test_expected_result = expected_result_fixture,
                                                start_time =time.time()) == 0,self.tests_fonctionnels.get_fonc_message()
      
        
        #-----fixture - nom du device de type BeamlineStatus
        @pytest.fixture(params=[("java/device/beamlinestatus.1")])
        def device_beamlinestatus_name(self,request):
            yield request.param
            
            
if __name__ == '__main__':   
#------------on cherche le chemin absolu du script qu'on lance
    script_name = os.path.abspath(__file__)
#--------------pytest ne doit pas écrire dans le cache
    os.environ['PYTEST_ADDOPTS'] = '-p no:cacheprovider' 
#-------lancement des tests avec pytest
#----que les logs du scripts sont affichés avec --no-print-logs
#----les logs du script sont affichés pendent execution du script et pas aprés l'execution avec  --capture=no  
#----pas d'affichage du traceback avec    tb=no
    return_code = pytest.main([script_name,"-vv","--capture=no","--tb=no","--no-print-logs"], plugins=[TestBeamlineStatus()])
#------retour du resultat des tests
    sys.exit(return_code) 

    
    
    