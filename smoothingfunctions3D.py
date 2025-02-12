# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:52:16 2023

@author: some5124
"""
import numpy as np
import pandas as pd
import json

import utilities

#note that all the smoothing methods here give a p_dataSmoothed with the first n and last n frames 'missing', so the dataframe starts from frame n+1

def getpdata(dfTrackingFiltered, p):
    p_data = dfTrackingFiltered[dfTrackingFiltered.particle==p]
    p_data = p_data.drop('frame', axis = 1)
    
    column=p_data.index
    firstframe = int(column.min())

    # makes it so that the first frame of every particle is 1
    p_data.index = p_data.index - firstframe +1
    #reindexes the particle frames and then forward fills them to remove any "blanks" that result from memory in tracking
    p_data = p_data.reindex(pd.RangeIndex(start = 1, stop = p_data.index.max() + 1))
    #convert from nm to um for better plotting
    p_data = utilities.convertnmtoum(p_data)
    return p_data


def boxcar_kernel(n):
    size = 2 * n + 1
    kernel = np.ones(size) / size
    return kernel

def linear_kernel(n):
    size = 2 * n + 1
    weights = np.linspace(1, size, num=size)
    weights = np.where(weights <= (size + 1) / 2, weights, size + 1 - weights)
    return weights / np.sum(weights)

def mean_using_kernel(points, n,  kernel_function, sigma=1):
    weighted_sum = 0
    normalisation_factor = 0

    for i, p in enumerate(points):
        if not np.isnan(p):
            kernel = kernel_function(n)
            weight = kernel[i]
            weighted_sum += float(weight * p)
            normalisation_factor += weight
    weightedmean = weighted_sum / normalisation_factor

    return weightedmean

def medianfilter_smoothing(dataframe, options):
    n = options.get('smoothness')
    smoothed_data = pd.DataFrame(columns=['x', 'y', 'z'])
    for i in range(len(dataframe)-2*n):
        start = i
        end = i + 2*n + 1
        window = dataframe.iloc[start:end]
        smoothed_data.loc[i+n, 'x'] = window['x'].median()
        smoothed_data.loc[i+n, 'y'] = window['y'].median()
        smoothed_data.loc[i+n, 'z'] = window['z'].median()
    return smoothed_data

def meanfilter_smoothing(dataframe, options, n):
    # have to get n separately from options in case i want to pass vsmoothness for getting speeds
    kernelname = options.get('kernel')
    kernel_function = globals()[kernelname]
    smoothed_data = pd.DataFrame(columns=['x', 'y', 'z'])  # Create an empty DataFrame for smoothed data
    
   
    for i in range(len(dataframe)-(2*n)):
        start = i
        end = i + 2*n + 1
        window = dataframe.iloc[start:end]
        smoothed_data.loc[i+n, 'x'] = mean_using_kernel(window['x'], n, kernel_function, sigma=1)
        smoothed_data.loc[i+n, 'y'] = mean_using_kernel(window['y'], n, kernel_function, sigma=1)
        smoothed_data.loc[i+n, 'z'] = mean_using_kernel(window['z'], n, kernel_function, sigma=1)

    return smoothed_data

def smoothing(dfTrackingFiltered, p, options):
    
    smoothness = options.get('smoothness', 3)
    usemedianfilter = options.get('usemedianfilter', False)
    p_data = getpdata(dfTrackingFiltered, p)
    if usemedianfilter == True:
        p_dataSmoothed = medianfilter_smoothing(p_data, options)
    else:
        p_dataSmoothed = meanfilter_smoothing(p_data, options, smoothness)
    return p_dataSmoothed

def calculate_diff(df, n):
    diff_array= np.array([]).reshape(0,3)
    firsti = int(n-(n-1)/2)
    lasti = len(df) - n + 1
    for i in range(firsti, lasti + 1):
        precede = int(i - (n+1)/2)
        succede = int(i + (n+1)/2)
        diff = np.array([df.iloc[succede]['x'] - df.iloc[precede]['x'], df.iloc[succede]['y'] - df.iloc[precede]['y'], df.iloc[succede]['z'] - df.iloc[precede]['z']])
        diff_array = np.append(diff_array, [diff], axis = 0)
    return diff_array

def calculate_speeds(vector_array):
    speeds = np.linalg.norm(vector_array, axis=1)  # Calculate Euclidean norms for speed
    return speeds


def datatoarrays(dataframe):
    column=dataframe.index
    frameNum = int(column.max())
    x = list()
    y = list()
    z = list()
    framelist = list()
    #iterates through each frame, checks if it is missing, and appends its xy data to the dataset for plotting
    for frame in range(1,frameNum+1):
        exists = frame in dataframe.index
        if exists ==True:
            frame_data = dataframe[dataframe.index == frame]
            x.append(frame_data.iloc[0, 0]) 
            y.append(frame_data.iloc[0, 1])
            z.append(frame_data.iloc[0, 2])
            framelist.append(frame)
    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)
    framelist = np.asarray(framelist)
    
    return x, y, z, framelist


def getVs(dfTrackingFiltered, p, options):
    p_data2 = getpdata(dfTrackingFiltered, p)
    smoothness = options.get('smoothness')
    vsmoothness = int((smoothness - 1)/2)
    p_dataSmoothed2 = meanfilter_smoothing(p_data2, options, vsmoothness)
    #v_data is padded to have the first and last n rows intact, to ensure frames stay the same?
    v_data = calculate_diff(p_dataSmoothed2, smoothness)
    
    np.savetxt('C:/Users/some5124/Downloads/vdata.txt', v_data, delimiter=',')
    
    speeds = calculate_speeds(v_data)  # Calculate Euclidean norms for speed
    #####
    np.savetxt('C:/Users/some5124/Downloads/speeds.txt', speeds, delimiter=',')
    
    return speeds