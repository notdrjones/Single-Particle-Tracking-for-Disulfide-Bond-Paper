# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 12:26:22 2023

@author: some5124
"""

import os

def getPaths(filepath):
    # the name of the tif file
    filename = os.path.basename(filepath)
    filebasename = filename[0:-4]
    # the overall file for the genotype
    dataDirPath = os.path.dirname(filepath) 
    # the genotype name
    dataDir = os.path.basename(dataDirPath)
    # the overall file containing all genotypes
    mainDataFolderPath = os.path.dirname(dataDirPath) + '/' 
    dataOutPath=mainDataFolderPath + "results/"
    
    if not os.path.exists(dataOutPath):
        os.mkdir(dataOutPath)
    if not os.path.exists(dataOutPath + dataDir):
        os.mkdir(dataOutPath + dataDir)
    
    
    return filebasename, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath

def convertnmtoum(df):
    
    df.iloc[:,0] = df.iloc[:,0]/1000

    df.iloc[:,1] = df.iloc[:,1]/1000

    if df.columns.values[2] == 'z':

        df.iloc[:,2] = df.iloc[:,2]/1000
        
    return df