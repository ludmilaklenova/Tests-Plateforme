#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# Synchrotron Soleil
#
# Nom: reg_dservers.py
#
#Vérification de non regression du nombre de dservers de la base de données Tango
#
########################################################################
"""
Created on 11/01/2018
@author: Ludmila Klenov <ludmila.klenov@synchrotron-soleil.fr>
"""

from __future__ import print_function
import argparse
import os
import sys
import glob
import time
import datetime
import pytest
import requests
from test_generic_common import TestGeneric

class TestNumbersDservers(TestGeneric):
    """Configuration class for check number a dservers in the database"""
    prog_version              = '1' #version de l'application
    rc                        = 0 # code de retour de l'application
    ns                        = None #parser
    fonc_message              = "regression not found" #dernier message de l'application
    var_env                   = 'PYTESTS_PLATFORM_ROOT' #le nom de la" variable d'environnement
    number_dservers_file_name = 'regression_number_dservers.txt' #le nom du fichier du resultat du test sur le nombre de dservers
    regression_number_dservers_file = None #le nom du fichier du resultat du test sur le nombre des dservers dans la base de données
       
    # define command line parser
    parser = argparse.ArgumentParser(prog='reg_dservers', description="Check number dservers options")
    parser.add_argument('--version', action='version', version='%(prog)s  ' + prog_version, help ="reg_dservers version")
    parser.add_argument("--fref",required=True,help="All dservers reference file")
    parser.add_argument("--fcurrent",required=True,help="All dservers current file")
    parser.add_argument('--log_file',default='/tmp/DeviceRoot_CPP/Regression/logs/reg_number_dservers.log',type=str,help="Logs file. Default : /tmp/DeviceRoot_CPP/Regression/logs/reg_number_dservers.log")
    parser.add_argument('--output_dir',default='/tmp/DeviceRoot_CPP/Regression/output',type=str,help="backup results tests directory. Default : /tmp/DeviceRoot_CPP/Regression/output")
    
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

        #----mise en place de l'environnement des tests    
        #------si l'erreur, fin de tests
        if TestGeneric.setEnv(self, tango_host=os.environ['TANGO_HOST'],log_file=self.ns.log_file)== 1 :
                print(self.fonc_message)
                return 1  
          
#----------------si le répertoire du resultat de test n'existe pas, 
#----------------création

        if not os.path.isdir(self.ns.output_dir):
            try:
                os.mkdir(self.ns.output_dir)
            except Exception, details :
                self.fonc_message = "Error : %s "%str(details)
                return 1    
                     
#-------------création du nom absolu du fichier de sauvegarde de resultat de tests sur le nombre des dservers 
#--------------presents la base de données 
        self.regression_number_dservers_file = '%s/%s'%(self.ns.output_dir,self.number_dservers_file_name)
        self.logger.info('\n')
        
        self.logger.info('regression number dservers file : %s'%self.regression_number_dservers_file)
            
        return 0
    
        
    def setUp(self,*args, **kwargs):
        """Clear output directory before a test.
            ::return : 0, if output directory is clear,
                       1, otherwise
        """ 
        self.logger.debug(unicode("test set up")) 
#----------------si le repertoire du resultat de test n'est pas vide
#---------------- suppression 
        all_files = glob.glob('%s/*'%(self.ns.output_dir))
        
        for ffile in all_files :
            try:
                os.remove(ffile)
            except Exception, details :
                self.fonc_message = "Error : %s "%str(details)
                return 1 
#-----------------verification que les fichiers de source et de reference de tous les dservers
#-----------------presents dans la base éxistes
        if not os.path.isfile(self.ns.fref):
            self.fonc_message = "Error : %s is not found"%str(self.ns.fref)
            return 1
        if not os.path.isfile(self.ns.fcurrent):
            self.fonc_message = "Error : %s is not found"%str(self.ns.fcurrent)
            return 1     
        return 0    
    
    def check_regression(self):
        """Execute a test.
            ::return : 0, if test is passed,
                       1, if test is failed.
        """
        self.rc             = 1 # code de retour de l'application    
          
        
#------------lecture de deux fichiers à comparer
        raw_ref     = open(self.ns.fref,'r').readlines()
        raw_current = open(self.ns.fcurrent,'r').readlines()
        
#-----------nettoyage du contenu des fichiers
#------------on enleve de commentaires
        ref     = [dserver_name.strip('\n\r') for dserver_name in raw_ref if '#' not in dserver_name]
        current = [dserver_name.strip('\n\r') for dserver_name in raw_current if '#' not in dserver_name]
        
#----------on enleve des doublons, si exists
        dservers_ref     = set(ref)
        dservers_current = set(current)
        
#-------------vérification s'il n'y a pas de doublons de dservers dans le fichier courant 
        if len(dservers_current) != len(current) :
            self.logger.debug(unicode("doubles dservers are detected in the last check of the database"))
        
#--------vérification si l'ensemble de dservers est toujours le meme par rapport à reference
        if not dservers_ref == dservers_current :
            
#----------vérification si le fichier courant contient les nouvelles dservers 
#----------par rapport à fichier de reference
#-------------la presence des nouveaux dservers est une regression
            source_diff = dservers_current - dservers_ref
#----------vérification si le fichier courant ne contient pas les memes dservers 
#----------que le fichier de reference -> regression
            ref_diff = dservers_ref - dservers_current
           
            with open(self.regression_number_dservers_file, "w") as fname:  
                if source_diff:
                    self.logger.info(unicode("The following DeviceServers are new in the package"))
                    fname.write(unicode("\n#The following DeviceServers are new in the package. Verify this is what is expected - '%s'"%datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")))   
                    fname.write("\n")
                    for dserver in source_diff :
                        fname.write(unicode("%s\n"%dserver))  
                if ref_diff :
                    self.fonc_message = "The following DeviceServers ARE NOT ANYMORE the package"
                    self.logger.info(unicode(self.fonc_message))                    
                    fname.write(unicode("\n#The following DeviceServers ARE NOT ANYMORE the package. Verify this is what is expected  - '%s'"%datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S"))) 
                    fname.write("\n")   
                    for dserver in ref_diff :
                        fname.write(unicode("%s\n"%dserver))      
#-------------le contenu de deux fichiers sont identiques
        else :
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
    
    def test_regression_dservers(self):  
        """Launch test
        """
#----mise en place de l'environnement des tests    
        #------si l'erreur, fin de tests
        
        if self.setEnv()== 1 :
            assert 1==0,self.get_fonc_message()
            
        #----------appel du test et vérification du resultat du test
       
        assert self.execute(None,test=self.check_regression,
                            start_time =time.time()) == 0,self.get_fonc_message()  
        
        
        
    
if __name__ == '__main__':   
#------------on cherche le chemin absolu du script qu'on lance
    script_name = os.path.abspath(__file__)
#--------------pytest ne doit pas écrire dans le cache
    os.environ['PYTEST_ADDOPTS'] = '-p no:cacheprovider' 
#-------le fichier de resultat du test
    #xml_name = '/tmp/DeviceRoot_CPP/Regression/test_regression_dservers_result.xml'
   
#---appel du module pytest avec la creation du fichier du resultat de type XML 
    #return_code = pytest.main([script_name,"-vv","--capture=no","--junitxml=%s"%xml_name], plugins=[TestNumbersDservers()])
    return_code = pytest.main([script_name,"-vv","--capture=no","--tb=no","--no-print-logs"], plugins=[TestNumbersDservers()])
    sys.exit(return_code)

     
