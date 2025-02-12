# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:51:58 2023

@author: some5124
"""

import os
import numpy as np
import pickle
import pandas as pd 
import trackpy as tp
from scipy import spatial
from sklearn.cluster import DBSCAN

import utilities

def clusterFiltering(tsData, options):
    # Compute DBSCAN
    
    exposureTime = options.get('exposureTime', 30)
    framesPerSec = 1000/exposureTime

    db = DBSCAN(eps=3, min_samples= 50).fit(tsData[['x','y']].to_numpy())
    
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)

    core_samples_mask[db.core_sample_indices_] = True

    labels = db.labels_

    

    tsData['labels']=labels

    tsData=tsData.loc[tsData.labels > -1]    


    goodClusters=[]

    #Loop through clusters and discard if convex hull area is too small

    for cluster in tsData.labels.unique():
        
        subData=tsData.loc[tsData.labels==cluster]


        db = DBSCAN(eps=5/framesPerSec, min_samples=int((len(subData.x)/100))+1).fit(subData[['x','y']].values)
        
        
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)

        core_samples_mask[db.core_sample_indices_] = True

        labels = db.labels_

        

        #Suppress the annoying SettingWithCopyError

        pd.options.mode.chained_assignment = None

        subData.loc[:,"labels"]=labels

        subData=subData.loc[subData.labels > -1]

        

        hull=spatial.ConvexHull(subData[['x','y']])

        convexHullArea=hull.volume

        if convexHullArea > 100:

            goodClusters.append(subData)

            # plt.figure()

            # plt.scatter(subData.x,subData.y,c=subData.labels,s=1)

            # plt.title(convexHullArea)

            # plt.scatter(subData.x,subData.y,c=subData.labels,s=1)


            
    emp = []        
    if goodClusters == emp:
        tsData = pd.DataFrame({'A' : []})
   
    else:
        tsData = pd.concat(goodClusters)
        
    return tsData

def getTracks(filepath, options):
    filebasename, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath = utilities.getPaths(filepath)
    with open(mainDataFolderPath+ dataDir+ "/B_tunderstormData_" + filebasename + ".csv") as file:
        tsData = pd.read_csv(file)
        
    minTrackLen = options.get('minTrackLength', 100)
    maxMemory = options.get('maxMemory', 0)
    get3D = options.get('3D', False)
    pixelsize = options.get('pixelsize', False)
    exposureTime = options.get('exposureTime', 30)
    searchRangeumpersec = options.get('searchRange', 300)
    #this search range is in um per second, so need to convert
    searchRange = searchRangeumpersec/pixelsize*1000/exposureTime
    
    if not os.path.exists(dataOutPath + dataDir + '/' +  filebasename):
        os.mkdir(dataOutPath + dataDir + '/' +  filebasename)
    
    if '[nm]' in tsData.columns.values[1]:

        tsData.iloc[:,1] = tsData.iloc[:,1]/pixelsize

        tsData.iloc[:,2] = tsData.iloc[:,2]/pixelsize

        if get3D is True:
    
            tsData.iloc[:,3] = tsData.iloc[:,3]/pixelsize

    

    new_columns = tsData.columns.values

    #Rename columns to trackpy compatible values

    new_columns[1] = 'x'

    new_columns[2] = 'y'
    
    if get3D is True:

        new_columns[3] = 'z'

    tsData.columns  = new_columns
    
    
    #tsData = clusterFiltering(tsData, options)
    
    if tsData.empty:
        print("No clusters after filtering!")
    else:
    
        #tp.quiet(True)
        
        if get3D is False:
            print("tracking in 2D")
        #writes a dataframe that allows linking of tracks
            dfTracking=pd.DataFrame(data=tsData, columns=["frame","y","x"])
            dfTracking = tp.link_df(tsData, search_range = searchRange, memory=maxMemory, pos_columns = ['frame', 'x', 'y'])
        else:
            print("tracking in 3D")
            dfTracking=pd.DataFrame(data=tsData, columns=["frame","y","x", "z"])
            #performs tracking and filters based on minimum track length
            dfTracking = tp.link_df(tsData, search_range = searchRange, memory=maxMemory, pos_columns = ['frame', 'x', 'y', 'z'])
        print("filtering")
        dfTrackingFiltered = tp.filter_stubs(dfTracking, minTrackLen)
        
        
          
        if dfTrackingFiltered.size == 0:
             with open(dataOutPath + dataDir + '/'  +filebasename+"/NoTracksPostFilter.txt", "w") as f:
                 f.write("NoTracksPostFilter!")
             print("No tracks of sufficient length present after filtering . Aborting!")
                  
        else:  
            dfTrackingFiltered.loc[:,"x"] = dfTrackingFiltered.loc[:,"x"]*pixelsize

            dfTrackingFiltered.loc[:,"y"] = dfTrackingFiltered.loc[:,"y"]*pixelsize

            if get3D is True:
        
                dfTrackingFiltered.loc[:,"z"] = dfTrackingFiltered.loc[:,"z"]*pixelsize
                
            with open(dataOutPath + dataDir + '/' + filebasename+"/dfTrackingFiltered.pickle", "wb") as f:
                pickle.dump(dfTrackingFiltered, f)
                
    return dfTrackingFiltered


            