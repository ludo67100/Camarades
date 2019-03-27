# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 22:56:10 2019

@author: ludov
"""

import electroPy 

path = 'E:/Ephy 2535/HDF5'

import os 
import re 

list_dir = os.listdir(path)

for file in list_dir : 
    print ('Converting' + file)
    new_path = '%s/%s'%(path,file)

    data = electroPy.HdF5IO(new_path)
    
    traces = data.filt_record()
    #time = data.filt_time()

    name = re.sub('\.h5$', '', file)

    file_save = 'D:/Federica/RAW_BINARY_FILES/%s.rbf'%name

    with open(file_save, mode='wb') as file : 
        traces.transpose().tofile(file,sep='')
