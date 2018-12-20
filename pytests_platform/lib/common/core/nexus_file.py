# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
#  Copyright (c) 2017 Synchrotron Soleil
#
#  Distributed under the terms of the GNU LGPL.
#
#  The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------
"""

Created on 04 aout 2017
@author: Ludmila KLENOV <ludmila.klenov@synchrotron-soleil.fr>
"""

import h5py    # HDF5 support
import os
from utils.errormessage import ErrorMessage
import numpy


class NexusFile(object) :
	"""Manage of the Nexus file.
	""" 
	def __init__(self,file_name, logger_object) :
		"""read NeXus file and check the content.
	   	::parameter : file_name - Nexus file name,
	   	::parameter : logger_object - logger of the logs files.
		"""
		
		self.nexus_file_name = file_name
		
		self.logger = logger_object
		self.error_message = ErrorMessage()
		if not self.check_file():
			self.logger.info("'%s' is not HDF5 file"%self.nexus_file_name)
			self.nexus_file_name = None

	def check_file(self) :
		"""check Nexus file exist and not empty.
		   ::return : True if Nexus file exist and not empty,
			      	  False, otherwise.
		"""
#---------si le fichier Nexus n'existe pas, erreur
		if not os.path.isfile(self.nexus_file_name) :
			self.error_message.set_error_message('FILE_NOT_FOUND',self.nexus_file_name)
			self.logger.error("NexusFile.check_file : '%s'"%self.error_message.get_error_message())
			return False

#--------si on ne peut pas accéder au fichier Nexus en lecture, erreur
		if not os.access(self.nexus_file_name, os.R_OK) :
			self.error_message.set_error_message('FILE_NOT_READABLE',self.nexus_file_name)
			self.logger.error("NexusFile.check_file : '%s'"%self.error_message.get_error_message())
			return False
		
#--------si le fichier n'est pas un hdf5 file, erreur
		f = h5py.File(self.nexus_file_name, 'r')
		
		if not self._is_hdf5_file(f):
			self.error_message.set_error_message('FILE_NOT_HDF5FILE',self.nexus_file_name)
			self.logger.error("NexusFile.check_file : '%s'"%self.error_message.get_error_message())
			f.close()
			return False
		self.logger.info("'%s' is a HDF5 file"%self.nexus_file_name)
		f.close()
		return True
	
	def get_data(self,data_name):
		"""get data from file.
		   ::parameter : data_name - full data path
		   ::return : data, if exist,
					  None, otherwise
		"""
		try:
			f = h5py.File(self.nexus_file_name,  "r")
		except Exception, message :
			self.error_message.set_error_message('FILE_NOT_FOUND',self.nexus_file_name)
			return None
		data = self._get_data_from_file(f,data_name)
		f.close()
		return data

	def _get_data_from_file(self,nx_file,data_name):
		"""get data from Nexus file.
			::parameter : nx_file - Nexus file,
			::parameter : data_name - full data path
			::return : data, if exist,
					   None, otherwise
		"""
		try:
				#------------récuperation des données
				present   = nx_file[data_name]
				#--------si la taille des données est 0, erreur
				if present.size == 0 :
					self.error_message.set_error_message('NEXUS_FILE_DATA_ERROR', present.name)
					self.logger.error("NexusFile._get_data_from_file : '%s'"%self.error_message.get_error_message())
					return None
		except Exception, details :
				# ignore any Exceptions, they mean that result stays "False"
				self.error_message.set_error_message('CHECK_NEXUS_FILE_ERROR',str(details))
				self.logger.error("NexusFile._get_data_from_file : '%s'"%self.error_message.get_error_message())
				return None	
		return present
		
	def check_data(self, list_data) :
		"""check Nexus file data.
		   ::parameter : list_data - list data for check.
		   ::return : True, if file is valid Nexus file
			      	  False, otherwise.
		"""
		try:
			f = h5py.File(self.nexus_file_name,  "r")
		except Exception, message :
			self.error_message.set_error_message('FILE_NOT_FOUND',self.nexus_file_name)
			f.close()
			return False
		
		if not self._is_nexusfile_bynxdata_attrs(f):
			self.error_message.set_error_message('FILE_NOT_NEXUSFILE',self.nexus_file_name)
			self.logger.error("NexusFile.check_data : '%s'"%self.error_message.get_error_message())
			f.close()
			return False
		
			#vérification que les données sont présent dans le fichier
		for data in list_data :
			if not self._get_data_from_file(f,data) :
				f.close()
				return False	
		f.close()
		self.logger.info("'%s' is a valid Nexus file "%self.nexus_file_name)
		return True

	def _is_hdf5_file(self,obj):
		"""check if `obj` is an HDF5 file.
	   	::parameter : obj - the file in read mode.
	   	::return : True, if obj is an HDF5 file,
	   			   False, otherwise.
		"""
		return isinstance(obj, h5py.File)

	def _is_hdf5_group(self,obj):
		"""check if `obj` an HDF5 group.
			::parameter : obj - group in the file.
			::return : True, if obj is an HDF5 group,
	   			       False, otherwise.
		"""
		return isinstance(obj, h5py.Group)

	

	def _get_group(self,parent, attribute, nxclass_name):
		"""
    		Search group named by the attribute.
    		::parameter : parent       - file or group, parent of the attribute,
    		::parameter : attribute    - group name,
    		::parameter : nxclass_name - class name of attribute,
    		::return    : group corresponding to this attribute.
    	"""
		#recherche le group correspondant a l'attribute
		group = parent.attrs.get(attribute, None)
		#si l'attribute n'est pas à la racine du parent, recherche dans tous les HDF5 groups
		#si il sont leur NX_class attribut décrite comme ``nxclass_name``
		if group :
			group = parent[group]
		else:
			for node0 in parent.values():
				if self._is_nexus_group(node0, nxclass_name):
					group = node0
					break
		return group

	def _is_nexus_group(self,obj):
		"""check if  `obj` a NeXus group.
			::parameter : obj    - group in the file,
			::return : True, if obj is a Nexus group,
	   			       False, otherwise.
		"""
		is_group = False
		nxclass  = None
		#--------vérification si object est une groupe 
		if self._is_hdf5_group(obj):
			nxclass = obj.attrs.get('NX_class', None)
			if isinstance(nxclass, numpy.ndarray):
				is_group = True
				break
		return is_group

	def _is_nexusfile_bynxdata_attrs(self,file_obj):
			"""
    			Verify these NeXus classpaths exist::
    
       			 /@default={entry_group}
       			 /{entry_group}:NXentry/@default={data_group}
       			 /{entry_group}:NXentry/{data_group}:NXdata
       			 ::return : True, if file_obj is a Nexus file,
	   			       		False, otherwise.
    		"""
			try:
				#---recherche NXentry groupe
				nxentry = self._get_group(file_obj, 'default', 'NXentry')
				#---si la groupe n'existe pas, erreur
				if nxentry is None:
					return False
					
				# recherche NXdata groupe
				nxdata = self._get_group(nxentry, 'default', 'NXdata')
				
				#---si la groupe n'existe pas, erreur
				if nxdata is None:
					return False        # no NXdata group identified
				return True
			except Exception as _exc:
				self.error_message.set_error_message('CHECK_NEXUS_FILE_ERROR',str(_exc))
				self.logger.error("NexusFile.isnexusfile_bynxdata_attrs : '%s'"%self.error_message.get_error_message())  
				return False



	

	

