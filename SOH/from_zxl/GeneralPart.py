# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 14:27:05 2021

@author: Zhouxiaolei
"""

from operator import itemgetter
from clickhouse_driver import Client
import pandas as pd
import datetime
import time
import xlsxwriter
import numpy

class GeneralDataProcessing:
    def __init__(self):
        self.client = Client(host='10.122.17.69',port='9005',database='en',user='en',password='en1Q')
        self.VinInfoForProject = []

    # get vinlist of specific project in specific time range, ordered by "accmiles" field
    # return list*4
    # VinForProject: vin list
    # vinMaxutForProject: latest uploadtime list
    # VinMinutForProject: earliest uploadtime list
    # VinAccmileForProject: latest accmile list
    def GetVinListForSpecificProject(self,ClickhouseTable,Project,SearchStartTime,SearchEndTime,limitconf):
        if Project == 'Tiguan':
            prefix1 = 'LSVU'
            prefix2 = '60T'
            sql = ("SELECT " \
                   "deviceid,maxut,minut,accmiles " \
                   "FROM " \
                       "(SELECT " \
                       "deviceid,uploadtime AS maxut,accmiles FROM " \
                       + ClickhouseTable +
                       " WHERE startsWith(deviceid, '" + prefix1 + "') AND substring(deviceid,6,3) = '" + prefix2 + "') " \

                       "INNER JOIN " \

                       "(SELECT " \
                       "deviceid,max(uploadtime) AS maxut,min(uploadtime) AS minut FROM " \
                       + ClickhouseTable + \
                       " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime \
                       + "' GROUP BY deviceid HAVING startsWith(deviceid, '" + prefix1 + "') AND substring(deviceid,6,3) = '" + prefix2 + "')" \
                       " USING deviceid,maxut " \
                   "ORDER BY toFloat32OrZero(accmiles) DESC")
        else:
            if Project == 'Lavida':
                prefix = 'LSVA'
            elif Project == 'Tharu':
                prefix = 'LSVUZ6B2'
            elif Project == 'Passat':
                prefix = 'LSVC'
            elif Project == 'MEB82':
                prefix = 'LSVUB'
            elif Project == 'MEB55':
                prefix = 'LSVUB'
            else:
                print('Wrong Project Name')
                return [[],[],[],[]]
            sql = ("SELECT " \
                   "deviceid,maxut,minut,accmiles " \
                   "FROM " \
                       "(SELECT " \
                       "deviceid,uploadtime AS maxut,accmiles FROM " \
                       + ClickhouseTable +
                       " WHERE startsWith(deviceid, '" + prefix + "')) " \

                       "INNER JOIN " \

                       "(SELECT " \
                       "deviceid,max(uploadtime) AS maxut,min(uploadtime) AS minut FROM " \
                       + ClickhouseTable + \
                       " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime \
                       + "' GROUP BY deviceid HAVING startsWith(deviceid, '" + prefix + "'))" \
                       " USING deviceid,maxut " \
                   "ORDER BY toFloat32OrZero(accmiles) DESC")

        if bool(limitconf):
            sql += " LIMIT " + "%s" % limitconf
        self.VinInfoForProject = self.client.execute(sql)
        [VinForProject,VinMaxutForProject,VinMinutForProject,VinAccmileForProject] = [list(row) for row in list(zip(*self.VinInfoForProject))]
        return VinForProject,VinMaxutForProject,VinMinutForProject,VinAccmileForProject

    def XlsWrite(self,data,filename):
        df = pd.DataFrame(data)
        df.to_excel(filename)

    def XlsRead(self,filename,dheader):
        if dheader:
            df = pd.read_excel(filename)
        else:
            df = pd.read_excel(filename,header=None)
        return df

    def ShiftSubNum(self,df):
        return df - df.shift(1)

    def ShiftSubDatetime(self,df):
        return (pd.to_datetime(df) - pd.to_datetime(df).shift(1)).dt.seconds

    # direction = 0 for default, direction = 1 for reverse
    def LocIdxFromStrStep(self,df,pattern,direction):
        if not direction:
            try:
                Idx = list(df.str.contains('|'.join(pattern))).index(False)
            except ValueError:
                Idx = len(df) - 1
        else:
            try:
                Idx = len(df) - list(df.str.contains('|'.join(pattern)))[-1:-len(df)-1:-1].index(False)
            except ValueError:
                Idx = 0
        return Idx