# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 11:09:49 2023

@author: some5124
"""

import pandas as pd
import os
import glob
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import ols
import statsmodels.graphics.gofplots as smqq
import statsmodels.graphics.regressionplots as smrp
import seaborn as sns


mainDataFolderPath="C:/Users/some5124/XLmutantSPT" + "/" #just so I remember it needs to have the / added
dataDirs=os.listdir(path=mainDataFolderPath)
exclude = 'results'
if exclude in dataDirs:
    dataDirs = [file for file in dataDirs if file != exclude]


def getAveSpeed(df, stopped):
    state_seqs = df[df.stopped == stopped]
    totLengths = state_seqs['length'].sum()
    product = state_seqs['length'] * state_seqs['meanSpeed']
    totAveSpeed = product.sum() / totLengths

    return totLengths, totAveSpeed


    
#iterate through all genotypes
def compileStateData(mainDataFolderPath, stopped):

    dataDirs=os.listdir(path=mainDataFolderPath)
    exclude = 'results'
    if exclude in dataDirs:
        dataDirs = [file for file in dataDirs if file != exclude]
    dataOutPath = mainDataFolderPath + 'results/'
    overalldf = pd.DataFrame(columns = ['meanSpeed', 'length', 'particle', 'acq','genotype'])
    for dataDir in dataDirs:
        dirdf = pd.DataFrame(columns = ['meanSpeed', 'length', 'particle', 'acq'])
        print("Now working in dir:"+dataDir)
        allFiles=os.listdir(mainDataFolderPath + dataDir)
        check = '_'
        filenames = [idx for idx in allFiles if idx[0].lower() == check.lower()]
        print(filenames)
        #iterate through each individual acquisition folder (named _X)
        for filename in filenames:

            seqsFilePath = dataOutPath + dataDir + '/' + filename + '_allseqs.csv'
            if os.path.exists(seqsFilePath):

                sequencedf = pd.read_csv(seqsFilePath)
                    
                filedf = sequencedf[sequencedf.stopped==stopped]
                filedf = filedf.iloc[:, 4:]
                print(filedf)        
                filedf['acq'] = filename
                dirdf = pd.concat([dirdf, filedf])
                
        dirdf['genotype'] = dataDir
        overalldf = pd.concat([overalldf, dirdf])    
        
    return overalldf

mainDataFolderPath="C:/Users/some5124/XLmutantSPT" + "/"
dataOutPath = mainDataFolderPath + 'results/'
overallMovingdf = compileStateData(mainDataFolderPath, 0)
overallMovingdf.to_csv(dataOutPath + 'allMovingSeqs.csv')

def prepforanova(df):
    df['particle'] = df['particle'].astype(str)
    #need to add genotype reference to particle name in case a number is repeated between genotypes
    df['particle'] = df['acq'] + df['particle']
    #similarly, need to merge particle and genotype in case there are repeats
    df['particle'] = df['genotype'] + df['particle']
    df = df.drop('acq', axis = 1)
    return df

def diagnosticplots(model):
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
    smqq.qqplot(model.resid, line='s', ax=axes[0])
    axes[0].set_title("Q-Q plot")
    #smrp.plot_regress_exog(model, 'C(genotype)', fig=axes[1].figure)
    #axes[1].set_title("Residuals vs Fitted")
    plt.show()
    
def freqplots(df):

    plt.figure(figsize=(8, 6))
    sns.kdeplot(data=df, x='length', hue='genotype', fill=False, common_norm=False)
    plt.show()
        
def anova(df, options, dep_var):
    df = prepforanova(df)
    formulastring = f"{dep_var} ~ C(genotype) + C(particle)"
    model = ols(formulastring, data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    print("ANOVA for " + dep_var + ':')
    print(anova_table)
    diagnosticplots(model)

### EXECUTION
options = {}
FilePath = mainDataFolderPath + 'results/allMovingSeqs.csv'
overalldf = pd.read_csv(FilePath)
freqplots(overalldf)
anova(overalldf, options, 'meanSpeed')