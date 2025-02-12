# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:52:39 2023

@author: some5124
"""
import pandas as pd
import numpy as np

import smoothingfunctions
import smoothingfunctions3D
import utilities



def findallsequences(v, options):
    minSpeed = options.get('minSpeed')
    sequences= np.array([]).reshape(0,5)
    sumofspeeds = 0
    #iterates through i, which corresponds to individual speeds in the array
    for i in range(len(v)):
        speed = v[i]
        if i == 0:
            startframehold = i
            if speed > minSpeed:
                stopped = 0
            else:
                stopped = 1
        else:
            if speed > minSpeed:
                newstopped = 0
            else:
                newstopped = 1
                
            if newstopped != stopped:
                endframehold = i - 1
                length = (endframehold - startframehold + 1)
                meanSpeed = sumofspeeds/length
                temp = np.array([startframehold, endframehold, stopped, meanSpeed, length])
                startframehold = i
                stopped = newstopped    
                sequences = np.append(sequences, [temp], axis = 0)
                sumofspeeds = 0
                sumofspeeds += speed
            else:
                sumofspeeds += speed
    return sequences


def getAllSequences(dfTrackingFiltered, options, locsfilePath):   
    filePath, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath = utilities.getPaths(locsfilePath)
    sequenceData = pd.DataFrame(columns = ['start', 'end', 'stopped', 'meanSpeed', 'length', 'particle'])
    column=dfTrackingFiltered["particle"]
    unique_particles = column.max()  
    for p in range(1, unique_particles+1):
        exists = p in dfTrackingFiltered["particle"].unique()
        if exists ==True:
            if options.get('3D') == True:
                v = smoothingfunctions3D.getVs(dfTrackingFiltered, p, options)
            else:
                v = smoothingfunctions.getVs(dfTrackingFiltered, p, options)
            sequences = findallsequences(v, options)
            new_rows = pd.DataFrame(sequences, columns = ['start', 'end', 'stopped', 'meanSpeed', 'length'])
            new_rows['particle'] = p
            sequenceData = pd.concat([sequenceData, new_rows])
    sequenceData.to_csv(dataOutPath + dataDir + '/' + filename + '_allseqs.csv')
    

    
    