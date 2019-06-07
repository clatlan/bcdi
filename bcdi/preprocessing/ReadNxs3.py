#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 14:39:36 2019

@author: andrea
"""

import tables
import os
import numpy as np
import pickle

class DataSet(object):
    '''Dataset read the file and store it in an object, from this object we can 
    retrive the data to use it: 
    Use as:
    dataObject = nxsRead3.DataSet( path/filename, path 
    filename can be /path/filename or just filename
    directory is optional and it can contain /path/path
    both are meant to be string
    Meant to be used on the data produced after the 11/03/2019 data of the 
    upgrade of the datarecorder''' 
    def __init__(self,filename, directory = ''):
        
        self.directory = directory 
        self.filename = filename
        attlist = []  # used for self generated file attribute list 
        aliases = [] # used for SBS imported with alias_dict file
        
        try:
            self._alias_dict = pickle.load(open('/home/andrea/MyPy3/alias_dict.txt','rb'))
        except FileNotFoundError:
            print('NO ALIAS')
            self._alias_dict = None
            
        def is_empty(any_structure):
            '''Quick function to determine if an array, tuple or string is empty '''
            if any_structure:
                return False
            else:
                return True
        ## Load the file 
        fullpath = os.path.join(self.directory,self.filename)
        ff = tables.open_file(fullpath,'r') 
        f = ff.list_nodes('/')[0]
          
        #### Discriminating between SBS or FLY scans      
        try:
            if f.scan_data.data_01.name == 'data_01':
                scantype = 'SBS'
        except tables.NoSuchNodeError:
            scantype = 'FLY'
        
        ########################## Reading FLY ################################        
        if scantype == 'FLY':
            ### generating the attributes with the recorded scanned data
            
            for leaf in f.scan_data:
                list.append(attlist,leaf.name) 
                self.__dict__[leaf.name] = leaf[:]
            self._attlist = attlist 
        ###################### Reading SBS ####################################
        if scantype == 'SBS':
            if  self._alias_dict:  #### Reading with dictionary
                for leaf in f.scan_data:
                        try :
                            alias = self._alias_dict[leaf.attrs.long_name.decode('UTF-8')]
                            if alias not in aliases:
                                aliases.append(alias)
                                self.__dict__[alias]=leaf[:]
                            
                        except :
                            self.__dict__[leaf.attrs.long_name.decode('UTF-8')]=leaf[:]
                            aliases.append(leaf.attrs.long_name.decode('UTF-8'))
                            pass
                self._aliases = aliases
            
            else:
                for leaf in f.scan_data: #### Reading with dictionary
                    ### generating the attributes with the recorded scanned data    
                    attr = leaf.attrs.long_name.decode('UTF-8')
                    attrshort = leaf.attrs.long_name.decode('UTF-8').split('/')[-1]
                    attrlong = leaf.attrs.long_name.decode('UTF-8').split('/')[-2:]
                    if attrshort not in attlist:
                        if attr.split('/')[-1] == 'sensorsTimestamps':   ### rename the sensortimestamps as epoch
                            list.append(attlist, 'epoch')
                            self.__dict__['epoch'] = leaf[:]
                        else:
                            list.append(attlist,attr.split('/')[-1])
                            self.__dict__[attr.split('/')[-1]] = leaf[:]
                    else: ### Dealing with for double naming
                        list.append(attlist, '_'.join(attrlong))
                        self.__dict__['_'.join(attrlong)] = leaf[:]
                self._attlist = attlist   
                
        ### adding some useful attributes common between SBS and FLY
        mono = f.SIXS.__getattr__('i14-c-c02-op-mono')
        self.waveL = mono.__getattr__('lambda')[0]
        self.energymono = mono.energy[0]
        
        #### probing time stamps and eventually use epoch to rebuild them
        if is_empty(np.shape(f.end_time)):
            try:
                self.end_time = max(self.epoch)
            except AttributeError:
                print('File has time stamps issues')
        else:
            self.end_time = f.end_time[0]
     
        if is_empty(np.shape(f.start_time)):
            try:
                self.start_time = min(self.epoch)
            except AttributeError:
                print('File has time stamps issues')
        else:
            self.start_time = f.start_time[0]   
            
        ff.close()


