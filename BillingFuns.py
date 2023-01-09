# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 13:35:47 2023

@author: jkern
"""

import numpy as np
import pandas as pd
import os
import math
import streamlit as st
from zipfile import ZipFile
import io


def readData(string, x):
    devicedf = pd.read_csv(string, skiprows=3)
    if x == 0:
        devicedf = getFactorize(devicedf)

    return devicedf



def getFactorize(df):
    df = df.loc[:, ['Serial Number', 'Database','Customer', 'VIN', 
                                'Bill Days', 'Quantity', 'Unit Cost', 'Cost']]
    
    ##if db is OH, then db = cust
    df.loc[df['Database'] == 'o_halloran', 'Database'] = df['Customer']
    
    df['Database'] = np.where((df['Database'] == 'landmark') & 
                              (df['Customer'] == 'Total Polish Solutions (Brian Diffin  Knoxvilee  Tennessee)'), 
                              'Total Polish Solutions', df['Database'])

    df.loc[df['Database'] == 'ls', 'Database'] = 'John LeJune'
    df.loc[df['Database'] == 't_b', 'Database'] = 'Ted Parker'
    
    df = df[df['Database'].notna()]
    df['id'] = df['Database'].factorize()[0]
    df['check'] = 0
    return df


def editProductPrice(df):
    df['Unit Cost'] = np.where(df['Unit Cost'] == 19, 32, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 14, 25, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 16, 27, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 18, 27, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 14.12, 32, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 15.4, 32, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 6, 15, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 7, 15, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 9, 20, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 22.85, 32, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 13, 20, df['Unit Cost'])
    df['Unit Cost'] = np.where(df['Unit Cost'] == 5, 7, df['Unit Cost'])
    
    return df


def setQuantity(d, m, y):
    days = getPrevMonDays(m, y)
    for i in range(len(d)):
        for x in range(len(d[i])):
            if d[i]['Serial Number'][x][:2] == 'G7' and d[i]['check'][x] == 0 and d[i]['Bill Days'][x] < days:
                z = 0
                while z < 1:
                    for y in range(len(d[i])):
                        if d[i]['Serial Number'][y][:2] == 'G9' and d[i]['check'][y] == 0 and d[i]['Bill Days'][y] == days:
                            z = 1
                            d[i].at[y, 'Bill Days'] = days - d[i]['Bill Days'][x]
                            d[i].at[y, 'check'] = 1
                            d[i].at[x, 'check'] = 1
                            break
                    z = 1
        d[i]['Quantity'] = d[i]['Bill Days'] / days
        d[i] = setCost(d[i])
    
    return d



def setCost(df):
    df['Cost'] = df['Unit Cost'] * df['Quantity']
    return df


def writeToCsv(d, lng, i):
    
    idx = i
    file = d[idx]['Database'].iloc[0]
    file += '.csv'
        
    df = d[idx]
    df = df[['Serial Number', 'VIN', 'Bill Days', 'Quantity', 'Unit Cost', 'Cost']]
    df.index = np.arange(1, len(df) + 1)
    return df, file
        
    
    
@st.cache
def convert_df(df, f):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(f).encode('utf-8')

    
def getYear(y):
    if y < 2022 | y > 2999:
        y = 0
    return y
    

def getPrevMonDays(m, y):
    m = m.lower()
    days = 0
    if m == 'jan':
        days = 31
    elif m == 'feb':
        days = 31
    elif m == 'mar':
        days = 28
        if y % 4 == 0:
            days = 29
    elif m == 'apr':
        days = 31
    elif m == 'may':
        days = 30
    elif m == 'jun':
        days = 31
    elif m == 'jul':
        days = 30
    elif m == 'aug':
        days = 31
    elif m == 'sep':
        days = 31
    elif m == 'oct':
        days = 30
    elif m == 'nov':
        days = 31
    elif m == 'dec':
        days = 30
    else:
        days = 0
    return days


def getMonth(m):
    m = m.lower()
    if m == 'january':
        m = 'Jan'
    elif m == 'february':
        m = 'Feb'
    elif m == 'march':
        m = 'Mar'
    elif m == 'april':
        m = 'Apr'
    elif m == 'may':
        m = 'May'
    elif m == 'june':
        m = 'Jun'
    elif m == 'july':
        m = 'Jul'
    elif m == 'august':
        m = 'Aug'
    elif m == 'september':
        m = 'Sep'
    elif m == 'october':
        m = 'Oct'
    elif m == 'november':
        m = 'Nov'
    elif m == 'december':
        m = 'Dec'
    else:
        m = 'nono'
    return m