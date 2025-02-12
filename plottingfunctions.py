# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:52:16 2023

@author: some5124
"""
import math
import numpy as np
import matplotlib as mpl
import matplotlib.collections as mcoll
import matplotlib.path as mpath
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib.ticker as ticker
from matplotlib.collections import LineCollection
import os

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import colorcet as cc

import utilities
import trackingFunctions
import smoothingfunctions
import smoothingfunctions3D

def getArea(dfTrackingFiltered, p):
    
    p_data = dfTrackingFiltered[dfTrackingFiltered.particle==p]
    # should add the area check here lol
    area = (p_data['x'].max() - p_data['x'].min())*(p_data['y'].max() - p_data['y'].min())
    
    return area

def normaliseplotsize(x, y, options):
    minxyrange = options.get('minxyrange')
    xmin = math.floor(x.min())
    xmax = math.ceil(x.max())
    ymin = math.floor(y.min())
    ymax = math.ceil(y.max())
    xrange = xmax - xmin
    yrange = ymax - ymin
    
    while xrange < minxyrange:
        xmax = xmax + 0.1
        xmin = xmin - 0.1
        xrange = xmax - xmin 
    while yrange < minxyrange:
        ymax = ymax + 0.1
        ymin = ymin - 0.1
        yrange = ymax - ymin 
    
    return xmin, xmax, ymin, ymax

def set_axes_equal(ax):

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5*max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

def plotgradientcolor(ax, x, y, framelist, options, plot2):
    cmap = options.get('colourmap')
    lw = options.get('linewidth')
    fontsize = options.get('fontsize')
    plt.rcParams['font.size'] = fontsize
    
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    norm = plt.Normalize(framelist.min(), framelist.max())
    lc = LineCollection(segments, cmap='viridis', norm=norm)
    # Set the values used for colormapping
    lc.set_array(framelist)
    lc.set_linewidth(lw)
    line = ax.add_collection(lc)
    xmin, xmax, ymin, ymax = normaliseplotsize(x, y, options)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    if plot2 == True:
        plt.colorbar(line, ax=ax)


def plotgradientcolor3D(ax, x, y, z, framelist, viewingangles, options):
    cmap = options.get('colourmap')
    lw = options.get('linewidth')
    fontsize = options.get('fontsize')
    
    plt.rcParams['font.size'] = fontsize
    
    points = np.array([x, y, z]).T.reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    norm = plt.Normalize(framelist.min(), framelist.max())
    lc = Line3DCollection(segments, cmap= cmap, norm=norm)
    
    xmin, xmax, ymin, ymax = normaliseplotsize(x, y, options)
    # Set the values used for colormapping
    lc.set_array(framelist)
    lc.set_linewidth(lw)
    line = ax.add_collection3d(lc)
    #plt.colorbar(line, ax=ax)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_zlim(z.min(), z.max())
    set_axes_equal(ax)
    ax.view_init(elev= viewingangles[0], azim= viewingangles[1], roll = viewingangles[2])
    #ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([aspect_x, aspect_y, aspect_z, 1]))
    ax.set_xlabel('$X$')
    ax.set_ylabel('$Y$')
    ax.set_zlabel('$Z$')
    

def plot2DTrajectoriesand3DSpeeds(dfTrackingFiltered, dataOutPath, fname, options):
    minSpeed = options.get('minSpeed')
    minArea = options.get('minArea', 0)
    if minArea == 0:
        filterbyArea = False
    else: 
        filterbyArea = True
    filebasename, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath = utilities.getPaths(fname)
    column=dfTrackingFiltered["particle"]
    unique_particles = column.max()  
    for p in range(1, unique_particles+1):
        exists = p in dfTrackingFiltered["particle"].unique()
        if exists ==True:
            if not os.path.exists(dataOutPath + dataDir + '/' + filebasename):
                os.mkdir(dataOutPath + dataDir + '/' + filebasename)
            goOn = 0 
            if filterbyArea is False:
                goOn = 1
            else:
                area = getArea(dfTrackingFiltered, p)
                if area > minArea:
                    goOn = 1
                    
            if goOn == 1:   
                p_dataSmoothed = smoothingfunctions3D.smoothing(dfTrackingFiltered, p, options)
                x, y, framelist = smoothingfunctions.datatoarrays(p_dataSmoothed)
                smoothness = options.get('smoothness')
                equaliser = int((smoothness - 5)/2)
                framelist = framelist[:-equaliser]
                x = x[:-equaliser]
                y = y[:-equaliser]
                v = smoothingfunctions3D.getVs(dfTrackingFiltered, p, options)
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
                plotgradientcolor(ax1, x, y, framelist, options, False)
                ax1.axis('equal')
                plotgradientcolor(ax2, framelist, v, framelist, options, True)
                ax2.set_ylim(0, 1)
                ax2.axhline(y = minSpeed, color = 'r', linestyle = '--', linewidth = 0.2)
                p = str(p)
                plt.savefig(dataOutPath + dataDir + '/' + filebasename + "/particle3Dspeedplot" + p + ".png", dpi=1200)
                plt.close()
            

def plotTrajectoriesandSpeeds(dfTrackingFiltered, dataOutPath, fname, options):
    filebasename, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath = utilities.getPaths(fname)
    column=dfTrackingFiltered["particle"]
    unique_particles = column.max()  
    minArea = options.get('minArea', 0)
    if minArea == 0:
        filterbyArea = False
    else: 
        filterbyArea = True
    for p in range(1, unique_particles+1):
        exists = p in dfTrackingFiltered["particle"].unique()
        if exists ==True:
            if not os.path.exists(dataOutPath + dataDir + '/' + filebasename):
                os.mkdir(dataOutPath + dataDir + '/' + filebasename)
            goOn = 0 
            if filterbyArea is False:
                goOn = 1
            else:
                area = getArea(dfTrackingFiltered, p)
                if area > minArea:
                    goOn = 1
                    
            if goOn == 1:   
                p_dataSmoothed = smoothingfunctions.smoothing(dfTrackingFiltered, p, options)
                x, y, framelist = smoothingfunctions.datatoarrays(p_dataSmoothed)
                smoothness = options.get('smoothness')
                equaliser = int((smoothness - 5)/2)
                framelist = framelist[:-equaliser]
                x = x[:-equaliser]
                y = y[:-equaliser]
                v = smoothingfunctions.getVs(dfTrackingFiltered, p, options)
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
                plotgradientcolor(ax1, x, y, framelist, options, False)
                ax1.axis('equal')
                plotgradientcolor(ax2, framelist, v, framelist, options, True)
                ## need to return ax ? or do ax = here?
                ax2.set_ylim(ymin=0, ymax = 0.2)
                p = str(p)
                plt.savefig(dataOutPath + dataDir + '/' + filebasename + "/particlespeedplot" + p + ".png", dpi=1200)
                plt.close()

def plotTrajectories(dfTrackingFiltered, dataOutPath, fname, options):
    filebasename, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath = utilities.getPaths(fname)
    column=dfTrackingFiltered["particle"]
    unique_particles = column.max()  
    minArea = options.get('minArea', 0)
    if minArea == 0:
        filterbyArea = False
    else: 
        filterbyArea = True
    for p in range(1, unique_particles+1):
        exists = p in dfTrackingFiltered["particle"].unique()
        if exists ==True:
            if not os.path.exists(dataOutPath + dataDir + '/' + filebasename):
                os.mkdir(dataOutPath + dataDir + '/' + filebasename)
            goOn = 0 
            if filterbyArea is False:
                goOn = 1
            else:
                area = getArea(dfTrackingFiltered, p)
                if area > minArea:
                    goOn = 1
                    
            if goOn == 1:   
                p_dataSmoothed = smoothingfunctions.smoothing(dfTrackingFiltered, p, options)
                x, y, framelist = smoothingfunctions.datatoarrays(p_dataSmoothed)
                fig, ax1 = plt.subplots()
                ax1.axis('equal')
                plotgradientcolor(ax1, x, y, framelist, options, True)
                p = str(p)
                plt.savefig(dataOutPath + dataDir + '/' + filebasename + "/particleplot" + p + ".png", dpi=1200)
                plt.close()
            
            
def plotTrajectories3D(dfTrackingFiltered, dataOutPath, fname,  options):
    filebasename, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath = utilities.getPaths(fname)
    column=dfTrackingFiltered["particle"]
    unique_particles = column.max()  
    minArea = options.get('minArea', 0)
    minArea = options.get('minArea', 0)
    if minArea == 0:
        filterbyArea = False
    else: 
        filterbyArea = True
    for p in range(1, unique_particles+1):
        exists = p in dfTrackingFiltered["particle"].unique()
        if exists ==True:
            print(p)
            if not os.path.exists(dataOutPath + dataDir + '/' + filebasename):
                os.mkdir(dataOutPath + dataDir + '/' + filebasename)
            goOn = 0 
            if filterbyArea is False:
                goOn = 1
            else:
                area = getArea(dfTrackingFiltered, p)
                if area > minArea:
                    goOn = 1
                    
            if goOn == 1:   
                p_dataSmoothed = smoothingfunctions3D.smoothing(dfTrackingFiltered, p, options)
                x, y, z, framelist = smoothingfunctions3D.datatoarrays(p_dataSmoothed)
                fig = plt.figure()
                ax = fig.add_subplot(projection='3d')
                viewingangles = options.get('angles')
                plotgradientcolor3D(ax, x, y, z, framelist, viewingangles, options)
                p = str(p)
                fig.savefig(dataOutPath + dataDir + '/' + filebasename + "/particle3Dplot" + p + ".png", dpi=1200)
                plt.close()
                
                
                
                
def plotTrajectories2Dand3D(dfTrackingFiltered, dataOutPath, fname, options):
    filebasename, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath = utilities.getPaths(fname)
    column=dfTrackingFiltered["particle"]
    unique_particles = column.max()  
    minArea = options.get('minArea', 0)
    minArea = options.get('minArea', 0)
    if minArea == 0:
        filterbyArea = False
    else: 
        filterbyArea = True
    for p in range(1, unique_particles+1):
        exists = p in dfTrackingFiltered["particle"].unique()
        if exists ==True:
            print(p)
            if not os.path.exists(dataOutPath + dataDir + '/' + filebasename):
                os.mkdir(dataOutPath + dataDir + '/' + filebasename)
            goOn = 0 
            if filterbyArea is False:
                goOn = 1
            else:
                area = getArea(dfTrackingFiltered, p)
                if area > minArea:
                    goOn = 1
                    
            if goOn == 1:   
                p_dataSmoothed = smoothingfunctions3D.smoothing(dfTrackingFiltered, p, options)
                x, y, z, framelist = smoothingfunctions3D.datatoarrays(p_dataSmoothed)
                
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
                plotgradientcolor(ax1, x, y, framelist, options, False)
                ax1.axis('equal')
                ax2 = fig.add_subplot(projection='3d')
                viewingangles = options.get('angles')
                plotgradientcolor3D(ax2, x, y, z, framelist, viewingangles, options)
                p = str(p)
                fig.savefig(dataOutPath + dataDir + '/' + filebasename + "/particle2Dand3Dplot" + p + ".png", dpi=1200)
                plt.close()
                
def plotTrajectories3Dmultiangle(dfTrackingFiltered, dataOutPath, fname, options):
    filebasename, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath = utilities.getPaths(fname)
    column=dfTrackingFiltered["particle"]
    unique_particles = column.max()  
    minArea = options.get('minArea', 0)
    minArea = options.get('minArea', 0)
    if minArea == 0:
        filterbyArea = False
    else: 
        filterbyArea = True
    for p in range(1, unique_particles+1):
        exists = p in dfTrackingFiltered["particle"].unique()
        if exists ==True:
            print(p)
            if not os.path.exists(dataOutPath + dataDir + '/' + filebasename):
                os.mkdir(dataOutPath + dataDir + '/' + filebasename)
            goOn = 0 
            if filterbyArea is False:
                goOn = 1
            else:
                area = getArea(dfTrackingFiltered, p)
                if area > minArea:
                    goOn = 1
                    
            if goOn == 1:   
                p_dataSmoothed = smoothingfunctions3D.smoothing(dfTrackingFiltered, p, options)
                x, y, z, framelist = smoothingfunctions3D.datatoarrays(p_dataSmoothed)
                
                fig = plt.figure()
               
                viewingangles = [90,-90,0]
                ax1 = fig.add_subplot(1,3,1,projection='3d')
                plotgradientcolor3D(ax1, x, y, z, framelist, viewingangles, options)
                
                viewingangles = [0,-90,0]
                ax2 = fig.add_subplot(1,3,2,projection='3d')
                plotgradientcolor3D(ax2, x, y, z, framelist, viewingangles, options)
                
                viewingangles = [0,0,0]
                ax3 = fig.add_subplot(1,3,3,projection='3d')
                plotgradientcolor3D(ax3, x, y, z, framelist, viewingangles, options)
                p = str(p)
                fig.savefig(dataOutPath + dataDir + '/' + filebasename + "/particle3Dplots" + p + ".png", dpi=1200)
                plt.close()                
                
            
# NB if dataframes end up being inhomogeneous (different lengths) for some reason, they are complicated ish
# assuming original p_data is len. x
# p_dataSmoothed is len x - 2*smoothness
# p_dataSmoothed2 is len x - n + 1    (because vSmoothness is (n-1)/2)
# speeds takes from p_dataSmoothed2 and is len x - 2n   (same as p_data) (difference is taken between )

def plotTrajectoriesFullFOV(dfTrackingFiltered, dataOutPath, fname, options):
    
    filebasename, filename, dataDirPath, dataDir, mainDataFolderPath, dataOutPath = utilities.getPaths(fname)
    column=dfTrackingFiltered["particle"]
    unique_particles = column.max()  
        #iterates through each particle and checks if it exists, since sometimes numbers are missing
    fig, ax = plt.subplots()
    fig.set_size_inches(5, 8)
    plt.gca().invert_yaxis()
    ax.set_xlim(0,50)
    ax.set_ylim(0,80)
    
    ax.axis('equal')
    for p in range(1, unique_particles+1):
        exists = p in dfTrackingFiltered["particle"].unique()
        if exists ==True:
            p_dataSmoothed = smoothingfunctions.smoothing(dfTrackingFiltered, p, options)
            x, y, framelist = smoothingfunctions.datatoarrays(p_dataSmoothed)
            p = str(p)
            print("plotting partile " + p)
            ax.plot(x,y, linewidth=0.05)
            
    plt.savefig(dataOutPath + dataDir + '/' + filebasename + "/particleplot.png", dpi=1200)
    plt.close()