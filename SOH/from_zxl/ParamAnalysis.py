from clickhouse_driver import Client
from sklearn.mixture import GaussianMixture
from sklearn.gaussian_process import GaussianProcessRegressor
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes
from scipy.stats import norm
import pandas as pd
import numpy as np
import datetime
import time
from scipy import interpolate
import os
from CharCycAnalysis import CharCycleAnalysis


class ParamAnalysis(CharCycleAnalysis):
    # initialise
    def __init__(self):
        super(ParamAnalysis, self).__init__()
        # self.client = Client(host='10.122.17.69', port='9005', database='en', user='en', password='en@WSX!')
        self.vin = ''
        self.VinData = pd.DataFrame([])
        self.StatData = pd.DataFrame([])
        self.DymData = pd.DataFrame([])
        self.StatDiff = []
        # self.InterestedFLst = ['uploadtime', 'deviceid', 'devicetype', 'vehiclestatus', 'chargingstatus',
        #                        'operationmode',
        #                        'vehiclespeed', 'accmiles', 'totalvolt', 'totalcurrent', 'soc', 'dcdc', 'ir', 'mxvsysno',
        #                        'mxvcelno', 'mxcelvt', 'mivsysno', 'mivcelno', 'micelvt', 'mxtsysno', 'mxtpno', 'mxtemp',
        #                        'mitsysno', 'mitpno', 'mitemp', 'cocessys1', 'vocesd1',
        #                        'cocesd1', 'cel1num1', 'sbofsn1', 'cfnum1', 'celv1', 'cocessysnum', 'cocessystemp1',
        #                        'cocespro1',
        #                        'cocesprotemp1', 'lgtp', 'lattp', 'lg', 'lat']
        # self.InterestedFields = (", ".join(self.InterestedFLst))
        # self.staticFrmNumPar = 3
        # self.UtIdx = self.InterestedFLst.index('uploadtime')
        # self.VinIdx = self.InterestedFLst.index('deviceid')
        # self.DTypIdx = self.InterestedFLst.index('devicetype')
        # self.VStatIdx = self.InterestedFLst.index('vehiclestatus')
        # self.CharStatIdx = self.InterestedFLst.index('chargingstatus')
        # self.OpModeIdx = self.InterestedFLst.index('operationmode')
        # self.VSpdIdx = self.InterestedFLst.index('vehiclespeed')
        # self.MileIdx = self.InterestedFLst.index('accmiles')
        # self.TotVolIdx = self.InterestedFLst.index('totalvolt')
        # self.CurrIdx = self.InterestedFLst.index('totalcurrent')
        # self.DbSocIdx = self.InterestedFLst.index('soc')
        # self.DcdcIdx = self.InterestedFLst.index('dcdc')
        # self.IsoRIdx = self.InterestedFLst.index('ir')
        # self.MxVSNoIdx = self.InterestedFLst.index('mxvsysno')
        # self.MxVCNoIdx = self.InterestedFLst.index('mxvcelno')
        # self.MxVIdx = self.InterestedFLst.index('mxcelvt')
        # self.MiVSNoIdx = self.InterestedFLst.index('mivsysno')
        # self.MiVCNoIdx = self.InterestedFLst.index('mivcelno')
        # self.MiVIdx = self.InterestedFLst.index('micelvt')
        # self.MxTSPNoIdx = self.InterestedFLst.index('mxtsysno')
        # self.MxTPNoIdx = self.InterestedFLst.index('mxtpno')
        # self.MxTIdx = self.InterestedFLst.index('mxtemp')
        # self.MiTSNodx = self.InterestedFLst.index('mitsysno')
        # self.MiTPNodx = self.InterestedFLst.index('mitpno')
        # self.MiTIdx = self.InterestedFLst.index('mitemp')
        # self.VSNo1Idx = self.InterestedFLst.index('cocessys1')
        # self.SNo1VIdx = self.InterestedFLst.index('vocesd1')
        # self.SNo1CurrIdx = self.InterestedFLst.index('cocesd1')
        # self.CellNumIdx = self.InterestedFLst.index('cel1num1')
        # self.SNo1FCNoIdx = self.InterestedFLst.index('sbofsn1')
        # self.SNo1FCNumIdx = self.InterestedFLst.index('cfnum1')
        # self.CellVolIdx = self.InterestedFLst.index('celv1')
        # self.TSNumIdx = self.InterestedFLst.index('cocessysnum')
        # self.TSNo1NoIdx = self.InterestedFLst.index('cocessystemp1')
        # self.PrbNumIdx = self.InterestedFLst.index('cocespro1')
        # self.PrbTempIdx = self.InterestedFLst.index('cocesprotemp1')
        # self.LgTypIdx = self.InterestedFLst.index('lgtp')
        # self.LatTypIdx = self.InterestedFLst.index('lattp')
        # self.LgIdx = self.InterestedFLst.index('lg')
        # self.LatIdx = self.InterestedFLst.index('lat')

    def GetVinData(self, vinTemp, searchStartTime, searchEndTime):
        """
        Get all data, steady candidate and charging status data in specific time range

        :param vinTemp:
        :param searchStartTime:
        :param searchEndTime:
        :return:
        """
        proj = self.GetProjectParamByVin(vinTemp)
        vinDataTemp = []
        # time periods in two table
        searchStartTimeV1 = str(
            min(datetime.datetime.strptime(searchStartTime, '%Y-%m-%d %H:%M:%S'), self.TableSplitTime))
        searchEndTimeV1 = str(min(datetime.datetime.strptime(searchEndTime, '%Y-%m-%d %H:%M:%S'), self.TableSplitTime))
        searchStartTimeV2 = str(max(datetime.datetime.strptime(searchStartTime, '%Y-%m-%d %H:%M:%S'),
                                    self.TableSplitTime + datetime.timedelta(0, 1)))
        searchEndTimeV2 = str(max(datetime.datetime.strptime(searchEndTime, '%Y-%m-%d %H:%M:%S'),
                                  self.TableSplitTime + datetime.timedelta(0, 1)))

        # if searchStartTimeV1.__le__(searchEndTimeV1):
        #     sql = ("SELECT " +
        #            self.InterestedFields +
        #            " From " + self.ClickhouseTableV1 +
        #            " WHERE deviceid = '" + vinTemp + "' AND abs(totalcurrent) < " + str(
        #                 self.staticCurrPar) + " And uploadtime >= '" + searchStartTimeV1 + "' AND uploadtime <= '" + searchEndTimeV1 + "'" +
        #            " ORDER BY uploadtime")
        #     vinDataTemp.extend(self.client.execute(sql))
        # if searchStartTimeV2.__le__(searchEndTimeV2):
        #     sql = ("SELECT " +
        #            self.InterestedFields +
        #            " From " + self.ClickhouseTableV2 +
        #            " WHERE deviceid = '" + vinTemp + "' AND abs(totalcurrent) < " + str(
        #                 self.staticCurrPar) + " And uploadtime >= '" + searchStartTimeV2 + "' AND uploadtime <= '" + searchEndTimeV2 + "'" +
        #            " ORDER BY uploadtime")
        #     vinDataTemp.extend(self.client.execute(sql))
        # self.StatData = pd.DataFrame(vinDataTemp).drop_duplicates()
        # # self.cellNum = np.argmax(np.bincount(self.StatData.iloc[:, 30].apply(lambda x: self.DefaultInvalidInt(x))))
        # # self.probeNum = np.argmax(np.bincount(self.StatData.iloc[:, 34].apply(lambda x: self.DefaultInvalidInt(x))))

        # vinDataTemp.clear()
        # if searchStartTimeV1.__le__(searchEndTimeV1):
        #     sql = ("SELECT " +
        #            self.InterestedFields +
        #            " FROM " + self.ClickhouseTableV1 +
        #            " WHERE deviceid = '" + vinTemp + "' AND chargingstatus LIKE 'CHARGING_STOPPED%'  AND uploadtime >= '" + searchStartTimeV1 + "' AND uploadtime <= '" + searchEndTimeV1 + "'" +
        #            " ORDER BY uploadtime")
        #     vinDataTemp.extend(self.client.execute(sql))
        # if searchStartTimeV2.__le__(searchEndTimeV2):
        #     sql = ("SELECT " +
        #            self.InterestedFields +
        #            " FROM " + self.ClickhouseTableV2 +
        #            " WHERE deviceid = '" + vinTemp + "' AND chargingstatus LIKE 'CHARGING_STOPPED%' AND uploadtime >= '" + searchStartTimeV2 + "' AND uploadtime <= '" + searchEndTimeV2 + "'" +
        #            " ORDER BY uploadtime")
        #     vinDataTemp.extend(self.client.execute(sql))
        #     self.DymData = pd.DataFrame(vinDataTemp).drop_duplicates()

        vinDataTemp.clear()
        if searchStartTimeV1.__le__(searchEndTimeV1):
            sql = ("SELECT " +
                   self.InterestedFields +
                   " FROM " + self.ClickhouseTableV1 +
                   " WHERE uploadtime >= '" + searchStartTimeV1 + "' AND uploadtime <= '" + searchEndTimeV2 + "' AND deviceid = '" + vinTemp + "' " +
                   " ORDER BY uploadtime")
            vinDataTemp.extend(self.client.execute(sql))
        if searchStartTimeV2.__le__(searchEndTimeV2):
            sql = ("SELECT " +
                   self.InterestedFields +
                   " FROM " + self.ClickhouseTableV2 +
                   " WHERE uploadtime >= '" + searchStartTimeV1 + "' AND uploadtime <= '" + searchEndTimeV2 + "' AND deviceid = '" + vinTemp + "'" +
                   " ORDER BY uploadtime")
            vinDataTemp.extend(self.client.execute(sql))
            self.VinData = pd.DataFrame(vinDataTemp).drop_duplicates()
        return self.StatData, self.DymData, self.VinData

    def StaticInconsisAnalysis(self, statDataTemp):
        """
        Analyze the cell soc and voltage inconsistency in steady status

        :param statDataTemp:
        :return:
        """
        # TODO: PHEV max/min value of voltage and cell voltages seems to be a hint of steady status judgement
        # check if MEB and Lavida has similar phenomenon

        self.StatDiff.clear()
        proj = self.GetProjectParamByVin(statDataTemp.iloc[0, self.VinIdx])
        statDate = statDataTemp.iloc[:, self.UtIdx]
        statDura = np.array((pd.to_datetime(statDate) - pd.to_datetime(statDate.shift(1))).dt.seconds)
        statFStepIdxs = [0]
        statFStepIdxs.extend(np.array(np.where(statDura > self.sampContiDuraPar + self.sampContiDuraThrPar
                                               )).flatten().tolist())
        statFStepIdxs.append(len(statDura))

        statFStepIdxs = np.array(statFStepIdxs)
        statFstepLen = statFStepIdxs[1:] - statFStepIdxs[0:-1]
        statPStepIdxsS = statFStepIdxs[np.where(statFstepLen > self.staticFrmNumPar)].tolist()  # 3 frames is expected
        statPStepIdxsE = statFStepIdxs[np.array(np.where(statFstepLen > self.staticFrmNumPar)) + 1].flatten().tolist()

        statInfoTemp = []

        for i in range(0, len(statPStepIdxsS) - 1):
            statPPcsData = statDataTemp.iloc[statPStepIdxsS[i]:statPStepIdxsE[i], :]
            statPPcsDate = statDataTemp.iloc[statPStepIdxsS[i]:statPStepIdxsE[i], self.UtIdx]
            if (pd.to_datetime(statDate.iloc[statPStepIdxsE[i] - 1]) -
                    pd.to_datetime(statDate.iloc[statPStepIdxsS[i]])
                    > datetime.timedelta(0, (self.sampContiDuraPar - self.sampContiDuraThrPar)
                                            * self.staticFrmNumPar, 0)):
                frmIdx = 0
                while frmIdx in range(0, len(statPPcsData)):
                    dateThr = (pd.to_datetime(statPPcsDate.iloc[frmIdx])
                               + datetime.timedelta(0, (self.sampContiDuraPar - self.sampContiDuraThrPar)
                                                    * self.staticFrmNumPar, 0))
                    try:
                        ucharPcsIdx = list((pd.to_datetime(statPPcsDate) - dateThr)
                                           > datetime.timedelta(0, 0, 0)).index(True)
                    except ValueError:
                        ucharPcsIdx = len(statPPcsData)
                    statDataCandi = statPPcsData.iloc[frmIdx:ucharPcsIdx, :]
                    cellVolTemp, volStd, currMax = self.GetStdVol(np.array(statDataCandi), self.CurrIdx,
                                                                  self.CellVolIdx)
                    if (not volStd.size == 0) and np.max(
                            volStd) < self.staticVolStdPar and currMax < self.staticCurrPar:
                        volMean = np.mean(cellVolTemp, axis=0)
                        cellT = self.GetCellTandPackT(np.array(statDataCandi), self.PrbTempIdx)
                        if int(round(cellT.size / self.cellNum)) > 1:
                            cellT = np.mean(cellT, axis=0)
                        socs = self.GetSocFromOCV(np.mean(cellVolTemp, axis=0), cellT)
                        statInfoTemp.append(vin)
                        statInfoTemp.append(statDataCandi.iloc[0, self.UtIdx])
                        statInfoTemp.append(np.median(socs))
                        statInfoTemp.extend((socs.flatten() - np.median(socs)).tolist())
                        # statInfoTemp.append(np.median(np.mean(cellVolTemp, axis=0)))
                        # statInfoTemp.extend((np.mean(cellVolTemp, axis=0) - np.median(np.mean(cellVolTemp, axis=0)))
                        #                     .tolist())
                        self.StatDiff.append(statInfoTemp[::])
                        statInfoTemp.clear()
                        if not ucharPcsIdx == len(statPPcsData):
                            frmIdx = min(ucharPcsIdx, len(statPPcsData) - self.staticFrmNumPar)
                        else:
                            frmIdx = ucharPcsIdx
                    else:
                        frmIdx += 1
        return self.StatDiff

    # TODO: self discharging analysis(SOC inconsistency info is required)
    def LongParking(self, vinDataTmp):
        vinStr = vinDataTmp.iloc[:, self.VinIdx]
        projstr = self.GetProjectParamByVin(vinDataTmp.iloc[0, self.VinIdx])
        vinDate = vinDataTmp.iloc[:, self.UtIdx]
        vinDura = np.array((pd.to_datetime(vinDate) - pd.to_datetime(vinDate).shift(1)).dt.seconds)
        vinMile = vinDataTmp.iloc[:, self.MileIdx]
        vinDMile = np.array(pd.to_numeric(vinMile) - pd.to_numeric(vinMile).shift(1))
        vinSoc = vinDataTmp.iloc[:, self.DbSocIdx]
        vinDSoc = np.array(pd.to_numeric(vinSoc) - pd.to_numeric(vinSoc).shift(1))
        vinCurr = np.array(vinDataTmp.iloc[:, self.CurrIdx])

        vinFSelfDischarIdxs = np.intersect1d(np.array(np.where(vinDura > 60 * 60 * 1)).flatten(),
                                             np.array(np.where(vinDMile == 0)).flatten())
        vinFSelfDischarIdxs = np.intersect1d(vinFSelfDischarIdxs, np.array(np.where(np.array(vinMile).astype(np.float)
                                                                                    < 999999)).flatten())
        vinSocUchagIdxs = np.intersect1d(np.array(np.where(np.array(vinSoc) == 100)).flatten() - 1,
                                         np.array(np.where(vinDSoc == 1)).flatten())
        vinSocUchagIdxs = np.union1d(np.array(np.where(vinDSoc == 0)).flatten(), vinSocUchagIdxs)
        vinFSelfDischarIdxs = np.array(np.intersect1d(vinFSelfDischarIdxs, vinSocUchagIdxs)).flatten().astype(np.int)

        if vinFSelfDischarIdxs.size > 0:
            longPInfoTmp = np.array([np.array(vinStr)[vinFSelfDischarIdxs].tolist(),
                                     np.array(vinDate)[vinFSelfDischarIdxs].astype(np.datetime64).tolist(),
                                     vinDura[vinFSelfDischarIdxs].tolist(),
                                     self.User2BMSSocBatch(np.array(vinSoc)[vinFSelfDischarIdxs]).tolist()]).T.tolist()
            cellVolsLPArr, volAvaHint = self.UpckDataFromStrArr(np.array(vinDataTmp)[vinFSelfDischarIdxs],
                                                                self.CellVolIdx, self.cellNum, 5, 0, 1)
            cellTempsLPArr, tempAvaHint = self.GetCellTandPackT(np.array(vinDataTmp)[vinFSelfDischarIdxs],
                                                                self.PrbTempIdx, 85, -40, 1)
            vinCurr = np.array(vinDataTmp.iloc[vinFSelfDischarIdxs, self.CurrIdx])
            pAvaHint = np.logical_and(volAvaHint, tempAvaHint)

            avaHint = np.intersect1d(np.array(np.where(pAvaHint.__eq__(True))).flatten(),
                                     np.array(np.where(np.abs(vinCurr) < self.compenCurrPar)).flatten())

            cellSocs = np.ones([pAvaHint.size, self.cellNum]) * -1
            cellSoc2BmsSoc = (np.ones([pAvaHint.size, 1]) * -1).flatten()
            volHint = np.intersect1d(np.array(np.where(tempAvaHint[volAvaHint].__eq__(True))).flatten(),
                                     np.array(np.where(np.abs(vinCurr[volAvaHint])
                                                       < self.compenCurrPar)).flatten())
            tempHint = np.intersect1d(np.array(np.where(volAvaHint[tempAvaHint].__eq__(True))).flatten(),
                                      np.array(np.where(np.abs(vinCurr[tempAvaHint])
                                                        < self.compenCurrPar)).flatten())
            cellSocs[avaHint] = self.GetSocFromOCV(cellVolsLPArr[volHint], cellTempsLPArr[tempHint])
            cellSoc2BmsSoc[avaHint] = self.GetPackSocBatch(projstr, cellSocs[avaHint])

            longPInfoTmp = pd.DataFrame(longPInfoTmp, columns=['vin', 'time', 'duration', 'Db2BmsSoc'])
            colname = ['vin', 'time', 'duration', 'Db2BmsSoc', 'CellSocs', 'BmsSoc',
                       'Temps', 'MaxTemp', 'MaxTempSysInd', 'MaxTempPrbInd']
            longPInfoTmp.reindex(columns=colname)
            longPInfoTmp['Temps'] = pd.DataFrame([x.__str__().replace(',', ';')
                                                  for x in np.array(vinDataTmp.iloc[vinFSelfDischarIdxs-1, self.PrbTempIdx])])
            longPInfoTmp['MaxTemp'] = pd.DataFrame(np.array(vinDataTmp.iloc[vinFSelfDischarIdxs-1, self.MxTIdx])
                                                   .astype(np.float))
            longPInfoTmp['MaxTempSysInd'] = pd.DataFrame(np.array(vinDataTmp.iloc[vinFSelfDischarIdxs-1, self.MxTSPNoIdx])
                                                         .astype(np.float))
            longPInfoTmp['MaxTempPrbInd'] = pd.DataFrame(np.array(vinDataTmp.iloc[vinFSelfDischarIdxs-1, self.MxTPNoIdx])
                                                         .astype(np.float))
            longPInfoTmp['time'] = pd.to_datetime(longPInfoTmp['time'].astype(np.float64))
            longPInfoTmp['CellSocs'] = pd.DataFrame([x.__str__().replace('\n', '') % x for x in cellSocs])
            longPInfoTmp['BmsSoc'] = cellSoc2BmsSoc
            return longPInfoTmp

    def LocBeloAndSeasons(self, infoDf, resDf):
        pass

    def NewLongParking(self, ClickhouseTable, Project, SearchStartTime, SearchEndTime):
        """
        get vin info of specific project in specific time range, ordered by "accmiles" field(mileage)

        :param ClickhouseTable:
        :param Project:
        :param SearchStartTime:
        :param SearchEndTime:
        :param limitConf: set for limit the amount of cars returned, if no limit is desired, use [] instead
        :return VinInfoForProject: list with 4 rows of vin list, latest uploadtime list, earliest uploadtime list and
                                   latest accmile list
        """

        if Project == 'Tiguan':
            prefix1 = 'LSVU'
            prefix2 = '60T'
            sql = (
                    "SELECT deviceid, arr_timemi, arr_timemx, arr_timemx-arr_timemi, arr_socmi, arr_milemi, arr_mxTmnomi, arr_mxTpnomi, arr_mxTmi, arr_mxTmx FROM " +
                    "(SELECT deviceid, num, arr_timemx, arr_socmx, arr_milemx, arr_mxTmnomx, arr_mxTpnomx, arr_mxTmx FROM " +
                    "(SELECT deviceid, groupArray(mxt) as arr_timemx, groupArray(mxsoc) as arr_socmx, groupArray(mxmile) as arr_milemx, groupArray(mxmxTmno) as arr_mxTmnomx, groupArray(mxmxTpno) as arr_mxTpnomx, groupArray(mxmxT) as arr_mxTmx FROM " +
                    "(SELECT * FROM " +
                    "((SELECT deviceid, max(uploadtime) AS mxt, max(soc) as mxsoc, max(accmiles) as mxmile, max(mxtsysno) as mxmxTmno, max(mxtpno) as mxmxTpno, max(mxtemp) as mxmxT FROM " +
                    ClickhouseTable +
                    " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime + "' AND toFloat32OrZero(accmiles) < 999999" +
                    " GROUP BY deviceid HAVING startsWith(deviceid,'LSVUB6E48L2011361'))" +
                    " UNION ALL " +
                    "(SELECT deviceid, uploadtime as mxt, soc as mxsoc, accmiles as mxmile , mxtsysno as mxmxTmno, mxtpno as mxmxTpno, mxtemp as mxmxT FROM " +
                    ClickhouseTable +
                    " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime + "' AND toFloat32OrZero(accmiles) < 999999 AND deviceid = 'LSVUB6E48L2011361'))" +
                    " ORDER BY mxt)" +
                    " GROUP BY deviceid)" +
                    " ARRAY JOIN" +
                    " arr_timemx, arr_socmx, arr_milemx, arr_mxTmnomx, arr_mxTpnomx, arr_mxTmx, arrayEnumerate(arr_timemx) as num)" +

                    " INNER JOIN " +

                    "(SELECT deviceid, num, arr_timemi, arr_socmi, arr_milemi, arr_mxTmnomi, arr_mxTpnomi, arr_mxTmi FROM " +
                    "(SELECT deviceid, groupArray(mit) as arr_timemi, groupArray(misoc) as arr_socmi, groupArray(mimile) as arr_milemi, groupArray(mimxTmno) as arr_mxTmnomi, groupArray(mimxTpno) as arr_mxTpnomi, groupArray(mimxT) as arr_mxTmi FROM " +
                    "(SELECT * FROM " +
                    "((SELECT " +
                    "deviceid,min(uploadtime) AS mit, min(soc) as misoc, min(accmiles) as mimile, min(mxtsysno) as mimxTmno, min(mxtpno) as mimxTpno, min(mxtemp) as mimxT FROM " +
                    ClickhouseTable +
                    " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime + "' AND toFloat32OrZero(accmiles) < 999999" +
                    " GROUP BY deviceid HAVING startsWith(deviceid, '" + prefix1 + "') AND substring(deviceid,6,3) = '" + prefix2 + "') " +
                    "UNION ALL " +
                    "(SELECT deviceid, uploadtime as mit, soc as misoc, accmiles as mimile, mxtsysno as mimxTmno, mxtpno as mimxTpno, mxtemp as mimxT FROM " +
                    ClickhouseTable +
                    " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime + "' AND toFloat32OrZero(accmiles) < 999999 AND startsWith(deviceid, '" + prefix1 + "') AND substring(deviceid,6,3) = '" + prefix2 + "'))" +
                    " ORDER BY mit)" +
                    " GROUP BY deviceid)" +
                    " ARRAY JOIN" +
                    " arr_timemi, arr_socmi, arr_milemi, arr_mxTmnomi, arr_mxTpnomi, arr_mxTmi, arrayEnumerate(arr_timemi) as num)" +
                    " USING deviceid, num WHERE arr_timemx - arr_timemi > 60*60 AND arr_milemx = arr_milemi AND arr_socmx = arr_socmi")
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
                prefix = 'LSVUA'
            else:
                print('Wrong Project Name')
                return [[], [], [], []]
            sql = (
                    "SELECT deviceid, arr_timemi, arr_timemx, arr_timemx-arr_timemi, arr_socmi, arr_milemi, arr_mxTmnomi, arr_mxTpnomi, arr_mxTmi, arr_mxTmx FROM " +
                    "(SELECT deviceid, num, arr_timemx, arr_socmx, arr_milemx, arr_mxTmnomx, arr_mxTpnomx, arr_mxTmx FROM " +
                    "(SELECT deviceid, groupArray(mxt) as arr_timemx, groupArray(mxsoc) as arr_socmx, groupArray(mxmile) as arr_milemx, groupArray(mxmxTmno) as arr_mxTmnomx, groupArray(mxmxTpno) as arr_mxTpnomx, groupArray(mxmxT) as arr_mxTmx FROM " +
                    "(SELECT * FROM " +
                    "((SELECT deviceid, max(uploadtime) AS mxt, max(soc) as mxsoc, max(accmiles) as mxmile, max(mxtsysno) as mxmxTmno, max(mxtpno) as mxmxTpno, max(mxtemp) as mxmxT FROM " +
                    ClickhouseTable +
                    " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime + "' AND startsWith(deviceid, '" + prefix + "') AND toFloat32OrZero(accmiles) < 999999" +
                    " GROUP BY deviceid)" +
                    " UNION ALL " +
                    "(SELECT deviceid, uploadtime as mxt, soc as mxsoc, accmiles as mxmile , mxtsysno as mxmxTmno, mxtpno as mxmxTpno, mxtemp as mxmxT FROM " +
                    ClickhouseTable +
                    " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime + "' AND startsWith(deviceid, '" + prefix + "') AND toFloat32OrZero(accmiles) < 999999))" +
                    " ORDER BY mxt)" +
                    " GROUP BY deviceid)" +
                    " ARRAY JOIN" +
                    " arr_timemx, arr_socmx, arr_milemx, arr_mxTmnomx, arr_mxTpnomx, arr_mxTmx, arrayEnumerate(arr_timemx) as num)" +

                    " INNER JOIN " +

                    "(SELECT deviceid, num, arr_timemi, arr_socmi, arr_milemi, arr_mxTmnomi, arr_mxTpnomi, arr_mxTmi FROM " +
                    "(SELECT deviceid, groupArray(mit) as arr_timemi, groupArray(misoc) as arr_socmi, groupArray(mimile) as arr_milemi, groupArray(mimxTmno) as arr_mxTmnomi, groupArray(mimxTpno) as arr_mxTpnomi, groupArray(mimxT) as arr_mxTmi FROM " +
                    "(SELECT * FROM " +
                    "((SELECT " +
                    "deviceid,min(uploadtime) AS mit, min(soc) as misoc, min(accmiles) as mimile, min(mxtsysno) as mimxTmno, min(mxtpno) as mimxTpno, min(mxtemp) as mimxT FROM " +
                    ClickhouseTable +
                    " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime + "' AND toFloat32OrZero(accmiles) < 999999" +
                    " GROUP BY deviceid HAVING startsWith(deviceid, '" + prefix + "'))" +
                    " UNION ALL " +
                    "(SELECT deviceid, uploadtime as mit, soc as misoc, accmiles as mimile, mxtsysno as mimxTmno, mxtpno as mimxTpno, mxtemp as mimxT FROM " +
                    ClickhouseTable +
                    " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime + "' AND startsWith(deviceid, '" + prefix + "') AND toFloat32OrZero(accmiles) < 999999))" +
                    " ORDER BY mit)" +
                    " GROUP BY deviceid)" +
                    " ARRAY JOIN" +
                    " arr_timemi, arr_socmi, arr_milemi, arr_mxTmnomi, arr_mxTpnomi, arr_mxTmi, arrayEnumerate(arr_timemi) as num)" +
                    " USING deviceid, num WHERE arr_timemx - arr_timemi > 60*60 AND arr_milemx = arr_milemi AND arr_socmx = arr_socmi")

        vinInfoForProjectTemp = self.client.execute(sql)
        self.VinInfoForProject = [list(row) for row in list(zip(*vinInfoForProjectTemp))]
        return self.VinInfoForProject


if __name__ == "__main__":
    searchSTime = '2019-05-01 00:00:00'
    searchETime = '2021-05-01 23:59:59'

    pa = ParamAnalysis()

    vinList = ['LSVAY60E2K2010108']
    proj = 'Passat'

    statInfo = []
    selfDischarInfo = []
    statSleepInfo = []
    allVolDiffInfo = []
    lPInfo = pd.DataFrame([])
    for vin in vinList:
        print(vin)
        statData, dymData, vinData = pa.GetVinData(vin, searchSTime, searchETime)
        if vinData.empty:
            continue
        longPInfo = pa.LongParking(vinData)
        lPInfo = lPInfo.append(longPInfo)
        lPInfo.to_csv("D:\\WorkSpace\\" + vin + "_longparkinginfo.csv", sep=',', index=False, header=None)
        vinData.to_excel(r"D:\WorkSpace\ " + vin + r"_all.xlsx")

    print('end')
