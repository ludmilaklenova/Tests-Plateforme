#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import os
import time
import pytest
import sys
import requests
from test_generic_common import TestGeneric


class TestScanServiceValidity(TestGeneric):
    """Configuration class for scan tests"""   
    prog_version    = '1' #version de l'application
    rc              = 1 # code de retour de l'application
    fonc_message    = "process has normally finished" #dernier message de l'application
    var_env         = 'PYTESTS_PLATFORM_ROOT' #le nom de la variable d'environnement
    ns              = None #parser de la ligne de la commande
    nmb_tests       = 0 #nombre de tests executes
    ScanServer      = None #class ScanServer
    NexusFile       = None #class NexusFile
    list_data       = None #liste des données à vérifier dans le fichier Nexus du resultat du scan

    # define command line parser
    parser = argparse.ArgumentParser(prog='fonc_scan_scanserver', description="ScanTest options")
    parser.add_argument('--version', action='version', version='%(prog)s  ' + prog_version, help ="fonc_scan_scanserver version")
    parser.add_argument('--log_file',default='/tmp/DeviceRoot_CPP/ScanServiceValidity/logs/scan_test.log',type=str,help="Logs file. Default : /tmp/DeviceRoot_CPP/ScanServiceValidity/logs/scan_test.log")
    parser.add_argument('--config_file',default='scan_config.cfg',type=str,help="configuration file of the scan. Default : scan_config.cfg")
    parser.add_argument('--scan',required=True,help="configuration of the scan in the configuration file")
    parser.add_argument('--nb_scan',type = int,default=1, help="numbers of scans. Default : 1 scan")
    
        
    def _print_error_message(self):
        """Print process error message in the console.
        """
        print('-'*60)
        print("-E----Test Scan error : %s"%self.fonc_message)
        print('-'*60)
        print('Test return 1\n')
        print('Test failed\n') 
        print('='*60)
            
        
    def setEnv(self,**kwargs): 
        """Initialize the environment that the application can turn.
                   :: return :
                         0,if the environment is set up,
                         1, otherwise.
        """
        
#----------Analyse syntaxique et sémantique de la ligne de commande 
        try :
            self.ns = self.parser.parse_args() #Les options de la ligne de commande
        except Exception, details :
            self.fonc_message = "Error : %s "%str(details)
            self._print_error_message()
            return 1
        
        #----mise en place de l'environnement des tests    
        #------si l'erreur, fin de tests
        if TestGeneric.setEnv(self, tango_host=os.environ['TANGO_HOST'],log_file=self.ns.log_file)== 1 :
                print(self.fonc_message)
                return 1   
        #--------------importation des modules
        try:
            from core.nexus_file import NexusFile
            from macro.scanmacro import ScanServer 
            self.ScanServer = ScanServer
            self.NexusFile  = NexusFile  
        except Exception, details :
            self.fonc_message = "Importation error '%s'"%str(details)
            self._print_error_message()
            return 1  
#--------------verification que le fichier de la configuration exist    
        if not os.path.exists(self.ns.config_file) :
            self.fonc_message = "config file '%s' does not exist"%self.ns.config_file
            return 1
        return 0
    
    def setUp(self,*args, **kwargs):
        """Initialization a device ScanServer before a test.
            ::return : 0, if init is correct,
                       1, otherwise
        """ 

#------------initialisation du device ScanServer    
        try:
                self.scan_server = self.ScanServer(self.ns.scan,self.ns.config_file,self.logger)
                self.logger.debug("ScanServer state is '%s' : '%s'"%(self.scan_server.state(),self.scan_server.status()))
        except Exception,details:
            self.fonc_message = "Error ScanServer device : %s "%(str(details))
            return 1
        
        return 0 
    
       
    def run_scan_service(self):
        """Execute a scan test.
            ::return : 0, if test is passed,
                   1, if execution error,
                   2, if test is failed.
        """
        self.rc             = 1 # code de retour de l'application

#--------------lancement du scan   
        for i in range(self.ns.nb_scan) :
            
            self.nmb_tests = str(i+1)
            self.logger.info("-----------Scan %s----------------\n"%self.nmb_tests)
            #----------------verification du resultat de lancement du scan
            if self.scan_server.run() == 1 :
                self.fonc_message = self.scan_server.error_message.get_error_message()
                return self.rc
            #initialisation du fichier Nexus  du resultat du scan
            self.logger.info("-----------Check Nexus file of the Scan result----------------")
           
            nexus_file = self.NexusFile(self.scan_server.get_current_nexus_file(),self.logger)
            self.logger.info("-----------Scan %s----------------\n"%self.nmb_tests)
            
            #-------------initialisation de la liste des données à vérifier dans le fichier Nexus
            self.list_data = ["/%s/scan_data/actuator_1_1"%self.scan_server.get_data_root_name(),
                          "/%s/scan_data/data_01"%self.scan_server.get_data_root_name(),
                          "/%s/scan_data/trajectory_1_1"%self.scan_server.get_data_root_name()]    
            #verification du contenu du fichier
            if not nexus_file.check_data(self.list_data):
                self.fonc_message =  nexus_file.error_message.get_error_message()  
                return self.rc
        # l'application est finie avec succès
        self.rc = 0
        
        return self.rc
    
    def run(self,args,test=None,test_argument=None, start_time=-1):
        """Execute a fonctionnel test.
             ::parameter: test - executed fonctionnel test,
             ::parameter: test_argument - fonctionnel test argument,
             ::parameter: start_time - test start time
             ::return : 0, if test is passed,
                   1, if execution error,
                   2, if test is failed.
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
    
    def test_scan_service_validity(self):  
        """Launch test
        """
        #----mise en place de l'environnement des tests    
        #------si l'erreur, fin de tests
        
        if self.setEnv()== 1 :
            assert 1==0,self.get_fonc_message()
            
        #----------appel du test et vérification du resultat du test
       
        assert self.execute(None,test=self.run_scan_service,
                            start_time =time.time()) == 0,self.get_fonc_message()  
    
if __name__ == '__main__':   
#------------on cherche le chemin absolu du script qu'on lance
    script_name = os.path.abspath(__file__)
#--------------pytest ne doit pas écrire dans le cache
    os.environ['PYTEST_ADDOPTS'] = '-p no:cacheprovider' 
#-------le fichier xml de resultat du test
    #xml_name = '/tmp/DeviceRoot_CPP/ScanServiceValidity/test_scan_scanserver.xml' 
#---appel du module pytest avec la creation du fichier du resultat de type XML 
    #return_code = pytest.main([script_name,"-vv","--capture=no","-p no:cacheprovider","--no-print-logs","--junitxml=%s"%xml_name], plugins=[TestScanServiceValidity()])
    return_code = pytest.main([script_name,"-vv","--capture=no","--tb=no","--no-print-logs"], plugins=[TestScanServiceValidity()])
   
#---mise a jour du test case dans la test execution avec appel de la commande curl
    #dans la commande le ticket est mise en dure
    #cmd = '''curl -H "Content-Type: multipart/form-data" -u admin:jira2013 -F "file=@py-results1.xml" http://jira-test.ica.synchrotron-soleil.fr:80/jira/rest/raven/1.0/import/execution/junit?testExecKey=XRAYT2LK-4'''
    #preparation de la requete pour la mise a jour du JIRA
    #url du site 
    '''url=u'http://jira-test.ica.synchrotron-soleil.fr:80/jira/rest/raven/1.0/import/execution/junit?testExecKey=TESTSPLTF-5'
    #fichier XML du resultat du test
    files = {u'file': open(u'%s'%xml_name, 'rb')}
    #envoi de la requete vers le site JIRA
    try :
        res = requests.post(url,  files=files,auth=(u'admin', u'jira2013'),verify=False)  
        print("Send for JIRA : '%s' "%res.content)
        #verification du resultat 
        if res.status_code == requests.codes.ok :
            print("Update issue : OK")
            #fin de mise a jour de la ticket test du JIRA
           
        else :
            #error lors de mise à jour du JIRA
            print("ERROR : Update issue NOK")
            #le status du resultat de la requete
            print(res.raise_for_status())
            
    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            print("ERROR JIRA REQUEST  : '%s'",str(e.message))
            res.raise_for_status()'''
    sys.exit(return_code)
    
    
