# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:50:36 2023

@author: some5124
"""

import numpy as np
from numpy.linalg import eig, inv, svd
import math
from math import atan2
import skimage as ski
from skimage import io, feature
from scipy import ndimage as ndi
from scipy import spatial
#import pyclesperanto_prototype as cle
import pandas as pd
import trackpy as tp
import os
import glob
import pickle
import re
import sklearn
from sklearn.cluster import DBSCAN


import utilities
import trackingFunctions
import smoothingfunctions
import smoothingfunctions3D
import plottingfunctions
import segmentAnalysisFunctions 


analysisOptions = {'plotGraph': True,
                   'plotFullFOVGraph': False,
                   'plotSpeeds':False,
            # the smoothness is the number of points either side of point I that will be averaged for smoothing, i.e. a rolling average between i-n and i+n inclusive
            'smoothness': 3,
            'usemedianfilter' : False,
            '3D' : True,
            'colourmap' : 'viridis',
            'minxyrange' : 0.5,
            'minArea' : 600000,
            'angles': [0,-90,0],
            'fontsize' : 4,
            'linewidth' : 0.2,
            'kernel': 'linear_kernel',
            'minTrackLength': 30,
            'maxMemory': 2,
            'searchRange': 5, #put this in um per second
            'minSpeed' : 0.1,
            'getSequences': False,       
            'exposureTime': 30, #in ms
            'pixelsize': 116.9 #in nm
            }

mainDataFolderPath="F:/XL SPT/SprF Cys mutants 250203/250223/3D" + "/" #just so I remember it needs to have the / added
dataDirs=os.listdir(path=mainDataFolderPath)
exclude = 'results'
if exclude in dataDirs:
    dataDirs = [file for file in dataDirs if file != exclude]

#iterate through all genotypes
for dataDir in dataDirs:
    print("Now working in dir:"+dataDir)
    allFiles=os.listdir(mainDataFolderPath+dataDir)
    check = 'R'
    filenames = [idx for idx in allFiles if idx[0].lower() == check.lower()]
    dataOutPath=mainDataFolderPath + "results/"
    #iterate through each individual acquisition folder (named _X)
    for filename in filenames:
        filebasename = filename[0:-4]
        filepath = mainDataFolderPath + dataDir + '/' + filename 
        locsfilepath = dataOutPath + dataDir + '/B_tunderstormData_' + filebasename + '.csv'
        #get all of the file names without having to put them all as arguments
        filebasename, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath = utilities.getPaths(filepath)
        if not os.path.exists(dataOutPath + dataDir + '/'  +filebasename + "_NoTracksPostFilter.txt"):
            
            if not os.path.exists(dataOutPath + dataDir + '/'  +filebasename + "/dfTrackingFiltered.pickle"):
                dfTrackingFiltered = trackingFunctions.getTracks(filepath, analysisOptions)   
        
            dfTrackingFiltered = pd.read_pickle(dataOutPath + dataDir + '/'  +filebasename + "/dfTrackingFiltered.pickle")
            
            if os.path.exists(dataOutPath + dataDir + '/'  +filebasename + "/dfTrackingFiltered.pickle"):
                if analysisOptions.get('plotGraph') == True:
                    if analysisOptions.get('3D') == True:
                        if analysisOptions.get('plotSpeeds') == True:
                            print("Now plotting 2D tracks with 3D Speeds")
                            plottingfunctions.plot2DTrajectoriesand3DSpeeds(dfTrackingFiltered, dataOutPath, filepath, analysisOptions)
                        else: 
                            print("Now plotting in 3D")
                            plottingfunctions.plotTrajectories3Dmultiangle(dfTrackingFiltered, dataOutPath, filepath, analysisOptions)
                        
                    else:
                        if analysisOptions.get('plotSpeeds') == True:
                            print("Now plotting Speeds in 2D")
                            plottingfunctions.plotTrajectoriesandSpeeds(dfTrackingFiltered, dataOutPath, filepath, analysisOptions)
                        else: 
                            print("Now plotting in 2D")
                            plottingfunctions.plotTrajectories(dfTrackingFiltered, dataOutPath, filepath, analysisOptions)
                        
                if analysisOptions.get('getSequences') == True:
                    segmentAnalysisFunctions.getAllSequences(dfTrackingFiltered, analysisOptions, filepath)
                        
                                
                if analysisOptions.get('plotFullFOVGraph') == True:    
                    plottingfunctions.plotTrajectoriesFullFOV(dfTrackingFiltered, dataOutPath, filepath, analysisOptions)