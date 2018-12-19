# -*- coding: utf-8 -*-
########################################################################
# Synchrotron Soleil
#
# Nom: setup.py
#
#création et installation du package
#
########################################################################

import os
import re
from distutils.core import setup, Extension

#BuildDoc sera utiliser pour la création de la documentation
try:
    from sphinx.setup_command import BuildDoc
except:
    sphinx = None

#récuperation du répertoire root du package - chemin absolu du répertoire du setup.py
setup_dir = os.path.dirname(os.path.abspath(__file__))

#le répertoire pytests_platform est un sous-répertoire le répertoire root 
scripts_dir = os.path.join(setup_dir, 'pytests_platform')

#le répertoire des fichiers des configurations
config_dir = os.path.join(setup_dir, 'pytests_platform','goldenFiles','configFiles')

#le répertoire des fichiers CSV
csv_files_dir = os.path.join(setup_dir, 'pytests_platform','goldenFiles','csv4tango')
#le répertoire des fichiers de reference
ref_files_dir = os.path.join(setup_dir, 'pytests_platform','goldenFiles','referenceFiles')

#expression regulier pour trouver tous les fichiers .py
reg_py = '.py$'

#expression regulier pour trouver tous les fichiers .py
reg_sh = '.sh$'

def get_scripts(folder_path,reg):
	"""recherche tous les scripts presents dans le package.
	   Les scripts qui se trouvent dans les répertoires avec le nom lib sont ignorés.
	   ::parametre : folder_path - le répertoire racine de la recherche,
	   ::parametre : reg - expression regulier pour la recherche des fichiers
	   ::return : la liste des fichiers correspondants à l'expression regulier <reg> si present dans l'arborescence, 
		      la liste vide sinon
	"""
	scripts = []
#---------pour chaque tuple (chemin absolut, nom du répertoire du fichier, nom du fichier)
#---------trouver dans l'arborescence du folder_path
	for path, dirs, files in os.walk(folder_path):
#-----------------si le chemin absolut contient lib, alors on ne cherche pas des scripts
		if re.compile('lib').search(path):
			continue
#-----------------pour chaque fichier du répertoire path
		for filename in files:
#---------------------si le nom du fichier est fini par .py et ce n'est pas le fichier __init__.py
#---------------------ajoute de ce script avec son chemin absolu dans la liste des scripts python trouvés
			if re.compile(reg).search(filename) and not '__init__.py' == filename:
                		scripts.append(os.path.join(path,filename))
	return scripts
    
def get_data_files(folder_path):
    """recuper tous les fichiers, presents dans le repertoire donnes en parametre, comme les fichiers de configuration.
       ::parametre : folder_path - le répertoire ou se trouvent les fichiers des configurations.
       ::return : la liste de tous les fichiers present dans folder_path, 
                  la liste vide si le repertoire folder_path est vide.
    """
    configs = []
#---------pour chaque tuple (chemin absolut, nom du répertoire du fichier, nom du fichier)
#---------trouver dans l'arborescence du folder_path
    for path, dirs, files in os.walk(folder_path):

#-----------------pour chaque fichier du répertoire path
        for filename in files:
#---------------------ajoute du fichier avec son chemin absolu dans la liste des configurations trouvées
                    configs.append(os.path.join(path,filename))
    return configs

def get_libs(folder_path):
	"""recherche de tous les API python presents dans le package - les scripts qui se trouvent dans les répertoires avec le nom lib.
	   ::parametre : folder_path - le répertoire racine de la recherche.
	   ::retourn : la liste des API python si present dans l'arborescence, 
		      la liste vide sinon.
	"""
	libs = []
#---------pour chaque tuple (chemin absolut, nom du répertoire du fichier, nom du fichier)
#---------trouver dans l'arborescence du folder_path
	for path, dirs, files in os.walk(folder_path):
#-----------------si le chemin absolut contient lib, alors on cherche des APIs python
		if re.compile('lib').search(path):
			for filename in files:
#-------------------si un des fichiers du répertoire path est le fichier __init__.py
#-------------------alors c'est un package API trouvé
				if '__init__.py' == filename :
#------------------création du chemin relatif accepter par la commande setup
					path_relatif = path[path.find('pytests_platform'):]
#------------------ajoute du chemin créé dans la liste des APIs python trouvés
                			libs.append(path_relatif)
					break
	return libs


# Setup ----------------------------------------------------------------------
import release #fichier release.py contient la description du package


def read(fname):
    """lecture du fichier qui se-trouve dans le répertoire de lancement du script setup.
	::parametre : fname - nom du fichier,
	::retourn : le contenu du fichier
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

#commande de la création et d'installation du package
setup(name='pytests_platform', #nom du répertoire qui contient les codes du packages
      description=release.description,
      long_description=read('README'), #lecture du fichier README comme long description du package
      author=release.author,
      author_email=release.author_email,
      maintainer=release.maintainer,
      maintainer_email=release.maintainer_email,
      url=release.url,
      download_url=release.download_url,
      platforms=release.platforms,
      keywords=release.keywords,
      classifiers=release.classifiers,
      packages=get_libs(scripts_dir), #récuperation des bibliotheques du package
      data_files=[('config-files',get_data_files(config_dir)),
                  ('csv-files',get_data_files(csv_files_dir)),
                  ('scripts',get_scripts(scripts_dir,reg_sh)),
                  ('ref-files',get_data_files(ref_files_dir))
                  ], #récuperation des fichiers des configurations
      package_dir={'pytests_platform': 'pytests_platform', },
      provides=['pytests_platform', ],
      requires=['python (==2.7)',
                'pytests (>=3.2.2)',
                'robot (>=3.0.2)',
               ],
     scripts=get_scripts(scripts_dir,reg_py) #récuperation des scripts des tests du package

      )
