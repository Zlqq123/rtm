# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 14:27:05 2021

charging cycle analysis: extracting the main feature of charge cycle, as well as calculating the SOH

@program derivative:
SOC jump analysis and related raw data
possible quantity of ampere hour error involved in each charging cycle

@author: Zhou XiaoLei
@version: 0.3
"""

from clickhouse_driver import Client
from sklearn.mixture import GaussianMixture
from sklearn.gaussian_process import GaussianProcessRegressor
import matplotlib.pyplot as plt
from scipy.stats import mode
import pandas as pd
import numpy as np
import datetime
from scipy import interpolate


class TicToc:
    def __init__(self):
        self.tp = None
        self.deltat = None

    @classmethod
    def tic(cls):
        cls.tp = datetime.datetime.now()

    @classmethod
    def toc(cls, conf):
        cls.deltat = datetime.datetime.now() - cls.tp
        print(conf + " consuming time: " + str(cls.deltat.seconds) + "." + str(cls.deltat.microseconds))


class CharCycleAnalysis:
    """

    """

    def __init__(self):
        """
        initialising generic and necessary variables
        """
        # configuration of clickhouse
        self.client = Client(host='10.122.17.69', port='9005', database='en', user='en', password='en@WSX!')
        self.ClickhouseTableV1 = 'ods.rtm_details'
        self.ClickhouseTableV2 = 'ods.rtm_details_v2'
        self.TableSplitTime = datetime.datetime(2020, 9, 25, 23, 59, 59)

        self.InterestedFLst = ['uploadtime', 'deviceid', 'devicetype', 'vehiclestatus', 'chargingstatus',
                               'operationmode',
                               'vehiclespeed', 'accmiles', 'totalvolt', 'totalcurrent', 'soc', 'dcdc', 'ir', 'mxvsysno',
                               'mxvcelno', 'mxcelvt', 'mivsysno', 'mivcelno', 'micelvt', 'mxtsysno', 'mxtpno', 'mxtemp',
                               'mitsysno', 'mitpno', 'mitemp', 'cocessys1', 'vocesd1',
                               'cocesd1', 'cel1num1', 'sbofsn1', 'cfnum1', 'celv1', 'cocessysnum', 'cocessystemp1',
                               'cocespro1',
                               'cocesprotemp1', 'gpsvalid', 'lgtp', 'lattp', 'lg', 'lat']

        self.InterestedFields = (
            ", ".join(self.InterestedFLst))
        self.UtIdx = self.InterestedFLst.index('uploadtime')
        self.VinIdx = self.InterestedFLst.index('deviceid')
        self.DTypIdx = self.InterestedFLst.index('devicetype')
        self.VStatIdx = self.InterestedFLst.index('vehiclestatus')
        self.CharStatIdx = self.InterestedFLst.index('chargingstatus')
        self.OpModeIdx = self.InterestedFLst.index('operationmode')
        self.VSpdIdx = self.InterestedFLst.index('vehiclespeed')
        self.MileIdx = self.InterestedFLst.index('accmiles')
        self.TotVolIdx = self.InterestedFLst.index('totalvolt')
        self.CurrIdx = self.InterestedFLst.index('totalcurrent')
        self.DbSocIdx = self.InterestedFLst.index('soc')
        self.DcdcIdx = self.InterestedFLst.index('dcdc')
        self.IsoRIdx = self.InterestedFLst.index('ir')
        self.MxVSNoIdx = self.InterestedFLst.index('mxvsysno')
        self.MxVCNoIdx = self.InterestedFLst.index('mxvcelno')
        self.MxVIdx = self.InterestedFLst.index('mxcelvt')
        self.MiVSNoIdx = self.InterestedFLst.index('mivsysno')
        self.MiVCNoIdx = self.InterestedFLst.index('mivcelno')
        self.MiVIdx = self.InterestedFLst.index('micelvt')
        self.MxTSPNoIdx = self.InterestedFLst.index('mxtsysno')
        self.MxTPNoIdx = self.InterestedFLst.index('mxtpno')
        self.MxTIdx = self.InterestedFLst.index('mxtemp')
        self.MiTSNodx = self.InterestedFLst.index('mitsysno')
        self.MiTPNodx = self.InterestedFLst.index('mitpno')
        self.MiTIdx = self.InterestedFLst.index('mitemp')
        self.VSNo1Idx = self.InterestedFLst.index('cocessys1')
        self.SNo1VIdx = self.InterestedFLst.index('vocesd1')
        self.SNo1CurrIdx = self.InterestedFLst.index('cocesd1')
        self.CellNumIdx = self.InterestedFLst.index('cel1num1')
        self.SNo1FCNoIdx = self.InterestedFLst.index('sbofsn1')
        self.SNo1FCNumIdx = self.InterestedFLst.index('cfnum1')
        self.CellVolIdx = self.InterestedFLst.index('celv1')
        self.TSNumIdx = self.InterestedFLst.index('cocessysnum')
        self.TSNo1NoIdx = self.InterestedFLst.index('cocessystemp1')
        self.PrbNumIdx = self.InterestedFLst.index('cocespro1')
        self.PrbTempIdx = self.InterestedFLst.index('cocesprotemp1')
        self.GpsValIdx = self.InterestedFLst.index('gpsvalid')
        self.LgTypIdx = self.InterestedFLst.index('lgtp')
        self.LatTypIdx = self.InterestedFLst.index('lattp')
        self.LgIdx = self.InterestedFLst.index('lg')
        self.LatIdx = self.InterestedFLst.index('lat')

        # parameters for charging cycle analysis(part of which are set afterwards)
        self.Q = 0
        self.charDiscDuraPar = 10 * 60  # maximum durable time discontinued duration in seconds
        self.sampContiDuraPar = 28  # sample data continuous duration in seconds
        self.sampContiDuraThrPar = 2  # maximum threshold in seconds for possible continuous sample duration delay
        self.staticFrmNumPar = 2  # minimum amount of frames for steady status judgement
        self.staticDiscDuraPar = 5 * 60  # minimum ignition off duration in seconds for gaining one steady candidate
        self.staticCurrPar = 0  # current threshold for steady candidate
        self.compenCurrPar = 0  # current threshold for depolar compensate
        self.staticVolStdPar = 0.002  # voltage fluctuation standard value threshold for steady candidate
        self.socDbRes = 1  # resolution of SOC value on dashboard

        # features of charging cycles(part of which are set afterwards)
        self.VinInfoForProject = []  # VIN list Info for specific project
        self.project = ''  # project, e.g. 'Tiguan'
        self.vin = ''  # VIN
        self.CharData = pd.DataFrame([])  # potential charging related data
        self.SocJumpAbnData = pd.DataFrame([])  # potential soc abnormal jump data
        self.cellNum = 0  # number of cells in the pack
        self.probeNum = 0  # number of probes in the pack
        self.CharInfoList = []  # list of features of each charging cycle
        self.CharFcycIdxsS = []
        self.CharFcycIdxsE = []  # frame indexes where charging cycles begin and end
        self.ACCurrThr = 20  # AC charging current threshold
        self.CurrLimTempThr = 50  # temperature threshold caused DC/AC charging fuzzy zone

        # module split edge of cell(set afterwards)
        self.ModuEdge = np.array([])
        self.PrbEdge = np.array([])

        # OCV-SOC look-up table for different projects under different temperatures(set afterwards)
        self.OCVols = np.array([])
        self.Temp = np.array([])
        self.OCSocs = np.array([])
        self.CR0 = np.array([])
        self.DR0 = np.array([])
        self.CR1 = np.array([])
        self.DR1 = np.array([])
        self.CR2 = np.array([])
        self.DR2 = np.array([])
        self.RCSocs = np.array([])
        self.RC1Coef = 0
        self.RC2Coef = 0

    def User2BMSSoc(self, DBSOC):
        """
        user soc 2 bms soc
        :param DBSOC:
        :return: BMSSOC
        """
        project = self.project
        if project.__eq__('Tiguan') or project.__eq__('Passat'):
            return 24 + (float(DBSOC) - 1.25) / (100.2 - 1.25) * (95 - 24)
        else:
            finterp = interpolate.interp1d(np.array(range(100, -1, -10)),
                                           np.array([96, 86.2, 77.3, 68.4, 59.4, 50, 41.6, 32.5, 25.6, 14.5, 4.5]),
                                           kind='linear')
            BMSSOC = finterp(np.array([min(max(DBSOC, 0), 100)])).flatten()
            return BMSSOC[0]

    def User2BMSSocBatch(self, DBSOC):
        project = self.project
        if project.__eq__('Tiguan') or project.__eq__('Passat'):
            return 24 + (DBSOC.astype(np.float) - 1.25) / (100.2 - 1.25) * (95 - 24)
        else:
            finterp = interpolate.interp1d(np.array(range(100, -1, -10)),
                                           np.array([96, 86.2, 77.3, 68.4, 59.4, 50, 41.6, 32.5, 25.6, 14.5, 4.5]),
                                           kind='linear')
            DBSOC[np.array(np.where(DBSOC < 0)).flatten()] = 0
            DBSOC[np.array(np.where(DBSOC > 100)).flatten()] = 100
            BMSSOC = finterp(DBSOC).flatten()
            return BMSSOC

    def DefaultInvalidInt(self, x):
        """
        str2int

        :param x: expected a string of an int
        :return int(x) or -1

        :except ValueError e.g. NULL
        """
        try:
            return int(x)
        except ValueError:
            return -1

    def UpckDataFromStrArr(self, npArr, interIdx, expcNum, valH, valL, avaIdxsConf=0):
        """
        Unpack numpy string array with comma

        :param avaIdxsConf:
        :param npArr: numpy array with a column of string vector needs to be split by comma
        :param interIdx: String Vector column index
        :param expcNum: expected number of values in string
        :param valH: upper limit of value
        :param valL: lower limit of value
        :return upckData: numpy float array unpacked
        """

        # TODO: Unknown Voltage and temperature valid range

        if npArr.size == 0:
            if avaIdxsConf == 0:
                return np.array([])
            else:
                return np.array([]), np.array([])
        elif 0 < npArr.size / len(self.InterestedFields.split(',')) < 2:
            Data = [npArr.flatten().tolist()[interIdx]]
        else:
            Data = npArr[0:, interIdx]
        avaIdxs = np.ones([int(round(npArr.size / len(self.InterestedFields.split(',')))), 1]).any(1)
        upckData = np.array([])
        dataRow = 0
        row = 0
        for frm in Data:
            try:
                FrmTemp = np.array(frm.split(',')).astype(np.float)
            except ValueError:
                avaIdxs[row] = False
                row += 1
                continue
            if (len(FrmTemp) == expcNum and np.array(
                    np.where((FrmTemp > valH) | (FrmTemp < valL)))
                    .size == 0):
                upckData = np.concatenate((upckData, FrmTemp))
                dataRow += 1
            else:
                avaIdxs[row] = False
            row += 1
        upckData = upckData.reshape(dataRow, expcNum)
        if avaIdxsConf == 0:
            return upckData
        else:
            return upckData, avaIdxs

    def GetSocFromOCV(self, volsArr, TsArr):
        """
        get soc values based on OCV-SOC

        1D interpolation is adopted currently

        :param volsArr: numpy array of voltages
        :param TsArr: numpy array of temperature
        :return: socs: numpy array of corresponding socs

        Attention: temperature over 40 or lower than -25 would be set to nearest value
        """

        temp = self.Temp
        soc = self.OCSocs
        xTemp, zSoc = np.meshgrid(temp, soc)
        yVol = self.OCVols
        socs = interpolate.griddata(np.vstack((xTemp.flatten(), yVol.T.flatten())).T, zSoc.flatten(), (TsArr, volsArr),
                                    method='linear')
        return socs

    def GetRC(self, curr, socArr, TsArr):
        """
        abandoned method
        get resistance by calibrated parameters
        :param curr:
        :param socArr:
        :param TsArr:
        :return:
        """
        if self.CR1.size == 0:
            return 0, 0, 0
        temp = self.Temp
        RCsoc = self.RCSocs
        if curr < 0:
            ZR0 = self.CR0
            ZR1 = self.CR1
            ZR2 = self.CR2
        else:
            ZR0 = self.DR0
            ZR1 = self.DR1
            ZR2 = self.DR2
        socArr[np.where(socArr > np.max(RCsoc))] = np.max(RCsoc)
        socArr[np.where(socArr < np.min(RCsoc))] = np.min(RCsoc)
        xTemp, ySoc = np.meshgrid(temp, RCsoc)

        R0 = interpolate.griddata(np.vstack((xTemp.flatten(), ySoc.flatten())).T, ZR0.T.flatten(), (TsArr, socArr),
                                  method='linear')
        R1 = interpolate.griddata(np.vstack((xTemp.flatten(), ySoc.flatten())).T, ZR1.T.flatten(), (TsArr, socArr),
                                  method='linear')
        R2 = interpolate.griddata(np.vstack((xTemp.flatten(), ySoc.flatten())).T, ZR2.T.flatten(), (TsArr, socArr),
                                  method='linear')
        return R0, R1, R2

    def GetDePolarVolsAndSocs(self, dataDfSameCurr):
        """
        abandoned method
        compensate polarization voltage by calibrated parameters
        :param dataDfSameCurr:
        :return: compensated voltage and soc of each cell
        """
        Ts = self.GetCellTandPackT(np.array(dataDfSameCurr), self.PrbTempIdx)
        if dataDfSameCurr.__len__() != dataDfSameCurr.size:
            curr = dataDfSameCurr.iloc[0, self.CurrIdx]
            dbSoc = dataDfSameCurr.iloc[0, self.DbSocIdx]
        else:
            curr = dataDfSameCurr.iloc[self.CurrIdx]
            dbSoc = dataDfSameCurr.iloc[self.DbSocIdx]
        vols = self.UpckDataFromStrArr(np.array(dataDfSameCurr), self.CellVolIdx, self.cellNum, 5, 0)
        R0, R1, R2 = self.GetRC(curr, np.array([self.User2BMSSoc(dbSoc)]), Ts)
        RC1coef = self.RC1Coef
        RC2coef = self.RC2Coef
        try:
            compenVols = vols + curr * R0 + RC1coef * curr * R1 + RC2coef * curr * R2
            socs = self.GetSocFromOCV(compenVols, Ts)
            R0, R1, R2 = self.GetRC(curr, socs, Ts)
            compenVols = vols + curr * R0 + RC1coef * curr * R1 + RC2coef * curr * R2
            compenSocs = self.GetSocFromOCV(compenVols, Ts)
        except ValueError:
            compenVols = np.array([])
            compenSocs = np.array([])
        return compenVols, compenSocs

    def GetPackSoc(self, project, socs):
        """
        calculate pack SOC
        :param project:
        :param socs:
        :return: round(packsoc, 2)
        """
        if socs.size == 0:
            return -1

        rMin = 30
        if project.__eq__('Tiguan') or project.__eq__('Passat'):
            rMax = 85
        else:
            rMax = 90
        if np.min(socs) <= rMin:
            packsoc = np.min(socs)
        elif np.min(socs) > rMin and np.max(socs) >= rMax:
            packsoc = np.max(socs)
        else:
            packsoc = rMin + (np.min(socs) - rMin) * (rMax - rMin) / ((rMax - rMin) - (np.max(socs) - np.min(socs)))

        return round(packsoc, 2)

    def GetPackSocBatch(self, project, socs):
        minSocs = np.min(socs, axis=1)
        maxSocs = np.max(socs, axis=1)
        rMin = 30
        if project.__eq__('Tiguan') or project.__eq__('Passat'):
            rMax = 85
        else:
            rMax = 90
        minIdx = np.array(np.where(minSocs < rMin)).flatten()
        nMinIdx = np.array(np.where(minSocs >= rMin)).flatten()
        maxIdx = np.intersect1d(np.array(np.where(maxSocs >= rMax)).flatten(), nMinIdx)
        midIdx = np.intersect1d(np.array(np.where(maxSocs < rMax)).flatten(), nMinIdx)

        packsoc = (np.ones([int(socs.size / self.cellNum), 1]) * -1).flatten()
        packsoc[minIdx] = minSocs[minIdx]
        packsoc[maxIdx] = maxSocs[maxIdx]
        packsoc[midIdx] = rMin + (minSocs[midIdx] - rMin) * (rMax - rMin) / ((rMax - rMin) - (maxSocs[midIdx]
                                                                                              - minSocs[midIdx]))
        return packsoc

    def GetAveMaxMinT(self, Data, TIdx, valH=85, valL=-40):
        """
        unpack temperature data from an string array of temperatures, and get its average, max, min value
        explore the invalid value of Temperatures

        :param valL:
        :param valH:
        :param Data: piece of data in numpy array with all of the fields
        :param TIdx: temperature index
        :return statPPcsTDataTemp: numpy float array of temperature
        :return TMean: average temperature
        """
        statPPcsTDataTemp = self.UpckDataFromStrArr(Data, TIdx, self.probeNum, valH, valL)
        if statPPcsTDataTemp.size / self.probeNum > 0:
            TMean = np.mean(np.mean(statPPcsTDataTemp))
            TMax = np.max(np.max(statPPcsTDataTemp))
            TMin = np.min(np.min(statPPcsTDataTemp))
        else:
            # Set default as infinity
            TMean = np.inf
            TMax = -np.inf
            TMin = np.inf
        return TMean, TMax, TMin

    def GetCellTandPackT(self, DataArr, TIdx, valH=85, valL=-40, avaIdxsConf=0):
        """
        unpack temperature data from an string array of temperatures, and get cell temperatures and pack temperature
        :param valL:
        :param valH:
        :param DataArr: piece of data in numpy array with all of the fields
        :param TIdx: temperature index
        :return cellT: cell temperatures for OCV-SOC

        # TODO: pack temperature calculation
        """
        if avaIdxsConf.__eq__(0):
            statPPcsTDataTemp = self.UpckDataFromStrArr(DataArr, TIdx, self.probeNum, valH, valL)
        else:
            statPPcsTDataTemp, avaHint = self.UpckDataFromStrArr(DataArr, TIdx, self.probeNum, valH, valL, 1)

        if statPPcsTDataTemp.size / self.probeNum > 0:
            # set upper and lower limit of temperature for OCV-SOC
            statPPcsTDataTemp[statPPcsTDataTemp > np.max(self.Temp)] = np.max(self.Temp)
            statPPcsTDataTemp[statPPcsTDataTemp < np.min(self.Temp)] = np.min(self.Temp)

            prbInd = 0
            cellTTemp = (np.array(statPPcsTDataTemp[:, prbInd].tolist() * self.PrbEdge[prbInd]).reshape(
                int(round(statPPcsTDataTemp.size / self.probeNum, 0)), self.PrbEdge[prbInd]))
            for prbInd in range(1, self.probeNum):
                cellTTemp = (np.hstack((cellTTemp, np.array(statPPcsTDataTemp[:, prbInd].tolist() * self.PrbEdge[
                    prbInd]).reshape(int(round(statPPcsTDataTemp.size / self.probeNum, 0)),
                                     self.PrbEdge[prbInd]))))

        else:
            cellTTemp = np.array([])
        if avaIdxsConf.__eq__(0):
            return cellTTemp
        else:
            return cellTTemp, avaHint

    def GetDynR(self, DataArr2Rows, IIdx, volIdx, valH=5, valL=0):
        """
        calculate resistance by delta v/delta I
        :param DataArr2Rows:
        :param IIdx:
        :param volIdx:
        :param valH:
        :param valL:
        :return: calculated resistance (OhmR + (1-e**(-t/RC))*PR)
        """
        volDataP = self.UpckDataFromStrArr(DataArr2Rows[0, :], volIdx, self.cellNum, valH, valL)
        volDataA = self.UpckDataFromStrArr(DataArr2Rows[1, :], volIdx, self.cellNum, valH, valL)
        IData = DataArr2Rows[:, IIdx].astype(np.float)
        try:
            if IData[1] - IData[0] != 0:
                R = (volDataA - volDataP) / (IData[1] - IData[0])
            else:
                R = np.array([])
        except ValueError or IndexError:
            R = np.array([])
        return R, IData[0], IData[1]

    def GetStdVol(self, DataArr, IIdx, volIdx, valH=5, valL=0):
        """
        get voltage value unpacked and get standard voltage value

        :param valL:
        :param valH:
        :param DataArr: piece of data in numpy array with all of the fields, frames with time gap within 30s is expected
        :param IIdx: current index
        :param volIdx: voltage index
        :return statPPcsVolDataTemp: numpy float array of voltage
        :return volStd: standard value of voltage
        :return IMax: maximum current value among the frames
        """
        statPPcsVolDataTemp = self.UpckDataFromStrArr(DataArr, volIdx, self.cellNum, valH, valL)
        if statPPcsVolDataTemp.size == 0:
            return np.array([]), np.array([]), np.inf
        IData = DataArr[:, IIdx].astype(np.float)
        IMax = np.max(np.abs(IData))

        if statPPcsVolDataTemp.size / self.cellNum >= self.staticFrmNumPar and IMax < self.staticCurrPar:
            volStd = np.std(statPPcsVolDataTemp, axis=0)
        else:
            volStd = np.array([])
        return statPPcsVolDataTemp, volStd, IMax

    def GetVinListForSpecificProject(self, ClickhouseTable, Project, SearchStartTime, SearchEndTime, limitConf=None):
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
            sql = ("SELECT " +
                   "deviceid,maxut,minut,accmiles " +
                   "FROM " +
                   "(SELECT " +
                   "deviceid,uploadtime AS maxut,accmiles FROM " +
                   ClickhouseTable +
                   " WHERE startsWith(deviceid, '" + prefix1 + "') AND substring(deviceid,6,3) = '" + prefix2 + "') " +

                   "INNER JOIN " +

                   "(SELECT " +
                   "deviceid,max(uploadtime) AS maxut,min(uploadtime) AS minut FROM " +
                   ClickhouseTable +
                   " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime + "' AND toFloat32OrZero(accmiles) < 999999" +
                   " GROUP BY deviceid HAVING startsWith(deviceid, '" + prefix1 + "') AND substring(deviceid,6,3) = '" + prefix2 + "')" +
                   " USING deviceid,maxut" +
                   " ORDER BY toFloat32OrZero(accmiles) DESC")
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
            sql = ("SELECT " +
                   "deviceid,maxut,minut,accmiles " +
                   "FROM " +
                   "(SELECT " +
                   "deviceid,uploadtime AS maxut,accmiles FROM " +
                   ClickhouseTable +
                   " WHERE startsWith(deviceid, '" + prefix + "')) " +

                   "INNER JOIN " +

                   "(SELECT " +
                   "deviceid,max(uploadtime) AS maxut,min(uploadtime) AS minut FROM " +
                   ClickhouseTable +
                   " WHERE uploadtime < '" + SearchEndTime + "' AND uploadtime >= '" + SearchStartTime + "' AND toFloat32OrZero(accmiles) < 999999" +
                   " GROUP BY deviceid HAVING startsWith(deviceid, '" + prefix + "'))" +
                   " USING deviceid,maxut" +
                   " ORDER BY toFloat32OrZero(accmiles) DESC")

        if limitConf is not None:
            sql += " LIMIT " + "%s" % limitConf
        vinInfoForProjectTemp = self.client.execute(sql)
        self.VinInfoForProject = [list(row) for row in list(zip(*vinInfoForProjectTemp))]
        return self.VinInfoForProject

    def GetProjectParamByVin(self, vinStr):
        """
        set battery parameters of the vin by project
        :param vinStr:
        :return project: project of vin
        """
        self.project = ''
        if vinStr.startswith('LSVU'):
            if vinStr[5:8].__eq__('60T'):
                self.project = 'Tiguan'
            elif vinStr.startswith('LSVUA'):
                self.project = 'MEB55'
        if vinStr.startswith('LSVA'):
            self.project = 'Lavida'
        elif vinStr.startswith('LSVUZ6B2'):
            self.project = 'Tharu'
        elif vinStr.startswith('LSVC'):
            self.project = 'Passat'
        elif vinStr.startswith('LSVUB'):
            self.project = 'MEB82'
        if self.project.__eq__('Tiguan') or self.project.__eq__('Passat'):
            self.Q = 37
            self.staticCurrPar = 0.05 * self.Q  # current threshold for steady candidate
            self.compenCurrPar = 0.15 * self.Q
            self.socDbRes = 1  # resolution of SOC value on dashboard
            self.ModuEdge = np.array(range(0, 97, 12))
            self.cellNum = 96
            self.probeNum = 8
            self.PrbEdge = np.array([12] * self.probeNum)
            self.OCVols = np.array(
                [[3.528076, 3.515381, 3.516113, 3.55542, 3.573975, 3.591553, 3.606445, 3.62207,
                  3.638428, 3.659424, 3.69043, 3.724609, 3.762451, 3.806885, 3.854004, 3.902588,
                  3.951416, 4.00293, 4.047119, 4.084473, 4.12793],
                 [3.469971, 3.493896, 3.539551, 3.571533, 3.587891, 3.601563, 3.614014, 3.626953,
                  3.641602, 3.660889, 3.688477, 3.730957, 3.770996, 3.813477, 3.85791, 3.903564,
                  3.951416, 4.001465, 4.05542, 4.113037, 4.164063],
                 [3.459961, 3.506592, 3.544922, 3.575439, 3.591553, 3.604492, 3.616943, 3.629395,
                  3.644043, 3.662598, 3.691406, 3.735107, 3.772949, 3.813965, 3.857422, 3.903564,
                  3.950928, 4.000488, 4.053955, 4.111084, 4.170898],
                 [3.47998, 3.520996, 3.554932, 3.582031, 3.600098, 3.612549, 3.624512, 3.637451,
                  3.651611, 3.67041, 3.703613, 3.741455, 3.775391, 3.814453, 3.857422, 3.9021,
                  3.948486, 3.996582, 4.047607, 4.103027, 4.172119],
                 [3.469971, 3.513916, 3.548096, 3.575439, 3.600098, 3.613525, 3.625488, 3.637939,
                  3.6521, 3.669922, 3.700439, 3.739014, 3.772949, 3.812012, 3.85498, 3.899902,
                  3.945557, 3.993408, 4.044434, 4.099609, 4.166992]
                 ])
            self.Temp = np.array([-25, -10, 0, 23, 40])
            self.OCSocs = np.array(range(0, 101, 5))
            self.CR0 = np.array([[0.011404, 0.011372, 0.011395, 0.010778, 0.011097, 0.011232, 0.016912],
                                 [0.0064648, 0.0062714, 0.0061702, 0.0059246, 0.0060492, 0.0061464, 0.0088546],
                                 [0.003172, 0.002871, 0.002687, 0.002689, 0.002684, 0.002756, 0.003483],
                                 [0.001076, 0.001013, 0.000986, 0.000944, 0.000944, 0.000912, 0.000957],
                                 [0.000765, 0.000744, 0.000723, 0.000708, 0.00071, 0.000696, 0.000721]])
            self.DR0 = np.array([[0.014551, 0.009712, 0.007973, 0.007187, 0.007603, 0.007603, 0.007603],
                                 [0.008053, 0.005629, 0.0048008, 0.004436, 0.00457, 0.0045508, 0.0050578],
                                 [0.003721, 0.002907, 0.002686, 0.002602, 0.002548, 0.002516, 0.003361],
                                 [0.001093, 0.001019, 0.000984, 0.000946, 0.00094, 0.000916, 0.000996],
                                 [0.000763, 0.000746, 0.000721, 0.00071, 0.00071, 0.000696, 0.000736]])
            self.CR1 = np.array([[0.016907, 0.009451, 0.007122, 0.005222, 0.004343, 0.003725, 0.004128],
                                 [0.0070658, 0.0038434, 0.0028602, 0.0021554, 0.0018128, 1.64E-03, 1.78E-03],
                                 [0.000505, 0.000105, 0.000019, 0.000111, 0.000126, 0.00025, 0.000214],
                                 [2.80E-04, 3.05E-04, 0.000275, 0.000328, 0.00024, 0.00025, 0.000221],
                                 [0.000305, 0.000298, 0.000238, 0.000242, 0.000193, 0.000206, 0.000141]])
            self.DR1 = np.array([[0.027565, 0.014069, 0.006863, 0.005001, 0.004589, 0.004827, 0.007095],
                                 [0.01147, 0.0058634, 0.002885, 0.0022098, 0.0020132, 0.0020718, 0.002979],
                                 [0.00074, 0.000393, 0.000233, 0.000349, 0.000296, 0.000235, 0.000235],
                                 [0.00032, 0.000278, 0.00024, 0.000269, 0.000227, 0.000242, 0.000204],
                                 [0.000303, 0.000273, 0.000217, 0.000212, 0.000189, 0.000204, 0.000132]])
            self.CR2 = np.array([[0.000439, 0.000343, 0.000856, 0.000994, 0.000349, 0.000217, 0.000227],
                                 [0.0008176, 0.000835, 0.0012454, 0.0013438, 0.0011788, 0.0014866, 0.0016898],
                                 [0.00107, 0.001163, 0.001505, 0.001577, 0.001732, 0.002333, 0.002665],
                                 [0.000502, 0.000437, 0.000467, 0.000479, 0.000568, 0.000622, 0.000652],
                                 [0.000357, 0.000256, 0.000238, 0.000267, 0.000319, 0.000332, 0.000351]])
            self.DR2 = np.array([[0.001375, 0.000982, 0.000027, 0.000093, 0.000093, 0.000093, 0.000093],
                                 [0.0014704, 0.001027, 0.0008268, 0.0008832, 0.0011976, 0.0015798, 0.0017034],
                                 [0.001534, 0.001057, 0.00136, 0.00141, 0.001934, 0.002571, 0.002777],
                                 [0.000635, 0.00057, 0.000591, 0.000633, 0.000837, 0.00082, 0.000742],
                                 [0.000422, 0.00034, 0.00033, 0.000357, 0.0005, 0.00045, 0.000435]])
            self.RC1Coef = 0.971833
            self.RC2Coef = 0.997063
            self.RCSocs = np.array([5, 20, 35, 50, 65, 80, 100])
        elif self.project.__eq__('MEB82'):
            self.Q = 234
            self.staticCurrPar = 0.03 * self.Q  # current threshold for steady candidate
            self.compenCurrPar = 0.1 * self.Q
            self.ModuEdge = np.array(range(0, 97, 8))
            self.cellNum = 96
            self.probeNum = 24
            self.PrbEdge = np.array([4] * self.probeNum)
            self.OCVols = np.array([[4.1785, 4.1135, 4.0855, 4.054, 4.0045, 3.9525, 3.9075, 3.8625, 3.814, 3.7625,
                                     3.707, 3.6645, 3.634, 3.609, 3.586, 3.561, 3.529, 3.483, 3.4275, 3.359,
                                     3.098],
                                    [4.1775, 4.112, 4.086, 4.0565, 4.0065, 3.9555, 3.9135, 3.874, 3.8245, 3.7605,
                                     3.705, 3.665, 3.636, 3.6125, 3.59, 3.566, 3.536, 3.4855, 3.425, 3.373,
                                     3.2085],
                                    [4.175, 4.112, 4.087, 4.056, 4.0055, 3.955, 3.9135, 3.8735, 3.8265, 3.761,
                                     3.7055, 3.666, 3.637, 3.613, 3.5905, 3.566, 3.535, 3.4825, 3.4225, 3.3725,
                                     3.221],
                                    [4.1745, 4.1125, 4.0875, 4.0565, 4.0055, 3.9555, 3.9135, 3.874, 3.828, 3.765,
                                     3.708, 3.668, 3.639, 3.615, 3.592, 3.5675, 3.5355, 3.4835, 3.423, 3.3735,
                                     3.234],
                                    [4.1725, 4.1125, 4.088, 4.0555, 4.0045, 3.9545, 3.913, 3.8725, 3.827, 3.767,
                                     3.7085, 3.6695, 3.6405, 3.6165, 3.593, 3.568, 3.5315, 3.4805, 3.4205, 3.371,
                                     3.2275],
                                    [4.1685, 4.1125, 4.088, 4.055, 4.0035, 3.9535, 3.912, 3.8725, 3.827, 3.768,
                                     3.7105,
                                     3.6725, 3.6435, 3.6185, 3.595, 3.5655, 3.5265, 3.4765, 3.4165, 3.37, 3.207]])
            self.Temp = np.array([-25, -10, 0, 10, 25, 40])
            self.OCSocs = np.array(range(100, -1, -5))
            self.CR0 = np.array([[0.003828, 0.003828, 0.0019131, 0.002039, 0.0024986, 0.0021667, 0.0021667],
                                 [0.0014439, 0.0014439, 0.00053787, 0.00065613, 0.00084114, 0.00057793, 0.00057793],
                                 [0.00065613, 0.00065613, 0.00047112, 0.0004921, 0.00054359, 0.00049782, 0.00049782],
                                 [0.00043488, 0.00043488, 0.00034714, 0.00035667, 0.00038338, 0.00035286, 0.00035286],
                                 [0.0003109, 0.0003109, 0.00026894, 0.00027084, 0.00028038, 0.00027657, 0.00027657],
                                 [0.00025368, 0.00025368, 0.00022888, 0.00022888, 0.00023651, 0.0002346, 0.0002346]])
            self.DR0 = np.array([[0.0022507, 0.0022507, 0.0013924, 0.0014248, 0.0019264, 0.0015335, 0.0015335],
                                 [0.0014343, 0.0014343, 0.00066566, 0.00069237, 0.00084114, 0.00072098, 0.00072098],
                                 [0.00064468, 0.00064468, 0.00048256, 0.000494, 0.0005455, 0.00050354, 0.00050354],
                                 [0.0004406, 0.0004406, 0.00036049, 0.0003643, 0.00038528, 0.00037003, 0.00037003],
                                 [0.00031853, 0.00031853, 0.00027084, 0.00027275, 0.00028229, 0.00027847, 0.00027847],
                                 [0.00025749, 0.00025749, 0.00022888, 0.00023079, 0.00023651, 0.0002327, 0.0002327]])
            self.CR1 = np.array([[0.0033932, 0.0033932, 0.00061035, 0.00048447, 0.00053787, 0.00084114, 0.00084114],
                                 [0.00036812, 0.00036812, 0.000019073, 0.000055313, 0.00015068, 1.91E-06, 1.91E-06],
                                 [0.000070572, 0.000070572, 0.000066757, 0.000047684, 0.000051498, 0.000053406,
                                  0.000053406],
                                 [7.63E-06, 7.63E-06, 0.000080109, 0.000051498, 0.000040054, 0.000061035, 0.000061035],
                                 [0.000022888, 0.000022888, 0.000047684, 0.000049591, 0.00003624, 0.000034332,
                                  0.000034332],
                                 [0.000038147, 0.000038147, 0.000041962, 0.000051498, 0.000034332, 0.00003624,
                                  0.00003624]])
            self.DR1 = np.array([[0.0094891, 0.0094891, 0.0001564, 0.00020027, 0.00037766, 0.00025368, 0.00025368],
                                 [0.0010052, 0.0010052, 0.000017166, 0.000032425, 0.000080109, 0.000034332,
                                  0.000034332],
                                 [0.000015259, 0.000015259, 0.000038147, 0.000034332, 0.00002861, 0.000043869,
                                  0.000043869],
                                 [0.00010109, 0.00010109, 0.000045776, 0.000041962, 0.000043869, 0.000049591,
                                  0.000049591],
                                 [0.000070572, 0.000070572, 0.000043869, 0.000040054, 0.000043869, 0.000059128,
                                  0.000059128],
                                 [0.000051498, 0.000051498, 0.000041962, 0.000038147, 0.000041962, 0.000055313,
                                  0.000055313]])
            self.CR2 = np.array([[0.0046368, 0.0046368, 0.0012398, 0.0001049, 0.00019073, 0.00013733, 0.00013733],
                                 [0.0014572, 0.0014572, 0.001997, 0.000020981, 0.00030708, 0.00002861, 0.00002861],
                                 [0.00034523, 0.00034523, 0.0001545, 0.00021744, 0.00029373, 0.00040054, 0.00040054],
                                 [0.00032806, 0.00032806, 0.00013733, 0.00016594, 0.0002346, 0.0002327, 0.0002327],
                                 [0.00027466, 0.00027466, 0.00016975, 0.00015259, 0.00021172, 0.00026321, 0.00026321],
                                 [0.00019073, 0.00019073, 0.0001049, 0.000076294, 0.00014305, 0.00014114, 0.00014114]])
            self.DR2 = np.array([[0.0090008, 0.0090008, 0.00019455, 0.00029182, 0.00053406, 0.00050735, 0.00050735],
                                 [0.0011597, 0.0011597, 0.0003109, 0.00039482, 0.00049973, 0.00050735, 0.00050735],
                                 [0.00040817, 0.00040817, 0.00038719, 0.00027466, 0.00035286, 0.00036049, 0.00036049],
                                 [0.0001545, 0.0001545, 0.00022888, 0.00017548, 0.00019646, 0.00021553, 0.00021553],
                                 [0.00018692, 0.00018692, 0.00017166, 0.00016403, 0.00016594, 0.00013351, 0.00013351],
                                 [0.00014877, 0.00014877, 0.000099182, 0.00012207, 0.00011444, 0.000068665,
                                  0.000068665]])
            self.RC1Coef = 0.971191881
            self.RC2Coef = 0.997944249
            self.RCSocs = np.array([0, 10, 30, 50, 70, 90, 100])
        elif self.project.__eq__('Lavida'):
            self.cellNum = 96
            self.probeNum = 32
            self.Q = 106
            self.staticCurrPar = 0.05 * self.Q  # current threshold for steady candidate
            self.compenCurrPar = 0.1 * self.Q
            self.ModuEdge = np.array(range(0, 97, 6))
            self.socDbRes = 1  # resolution of SOC value on dashboard
            self.PrbEdge = np.array([3] * self.probeNum)
            self.OCVols = np.array([[4.2336, 4.1796, 4.1099, 4.0546, 3.9942, 3.9381, 3.8838, 3.8308, 3.7819, 3.7412,
                                     3.7084, 3.6810, 3.6529, 3.6318, 3.6154, 3.5993, 3.5817, 3.5588, 3.5139, 3.4340,
                                     3.3011],
                                    [4.2307, 4.1394, 4.0736, 4.0135, 3.9583, 3.9062, 3.8569, 3.8104, 3.7687, 3.7273,
                                     3.6826, 3.6564, 3.6391, 3.6243, 3.6113, 3.5981, 3.5831, 3.5579, 3.5162, 3.4627,
                                     3.2680],
                                    [4.2261, 4.1376, 4.0739, 4.0149, 3.9599, 3.9080, 3.8587, 3.8126, 3.7711, 3.7326,
                                     3.6857, 3.6591, 3.6418, 3.6276, 3.6146, 3.6012, 3.5858, 3.5580, 3.5186, 3.4708,
                                     3.4133],
                                    [4.2392, 4.1378, 4.0745, 4.0157, 3.9609, 3.9092, 3.8597, 3.8137, 3.7727, 3.7360,
                                     3.6890, 3.6618, 3.6443, 3.6301, 3.6169, 3.6036, 3.5873, 3.5585, 3.5200, 3.4718,
                                     3.4209],
                                    [4.2115, 4.1236, 4.0613, 4.0048, 3.9520, 3.9015, 3.8520, 3.8091, 3.7701, 3.7367,
                                     3.6934, 3.6653, 3.6482, 3.6342, 3.6213, 3.6080, 3.5911, 3.5638, 3.5281, 3.4820,
                                     3.4359],
                                    [4.2108, 4.1232, 4.0605, 4.0040, 3.9509, 3.9004, 3.8521, 3.8071, 3.7677, 3.7345,
                                     3.6922, 3.6658, 3.6491, 3.6351, 3.6220, 3.6079, 3.5837, 3.5549, 3.5174, 3.4710,
                                     3.4291]])
            self.Temp = np.array([-25, -10, 0, 10, 23, 40])
            self.OCSocs = np.array(range(100, -1, -5))

        elif self.project.__eq__('MEB55'):
            self.cellNum = 96
            self.probeNum = 16
        return self.project

    def GetChardataByVin(self, vin, searchStartTime, searchEndTime):
        """
        get potential data related with charging cycles

        :param vin:
        :param searchStartTime:
        :param searchEndTime:
        :return self.CharData: pandas dataframe of data with Interested fields
        """
        self.CharData = pd.DataFrame([])

        # data container
        vinDataTemp = []
        # charging related fields
        interestedFields = self.InterestedFields

        # time periods in two table
        searchStartTimeV1 = str(
            min(datetime.datetime.strptime(searchStartTime, '%Y-%m-%d %H:%M:%S'), self.TableSplitTime))
        searchEndTimeV1 = str(min(datetime.datetime.strptime(searchEndTime, '%Y-%m-%d %H:%M:%S'), self.TableSplitTime))
        searchStartTimeV2 = str(max(datetime.datetime.strptime(searchStartTime, '%Y-%m-%d %H:%M:%S'),
                                    self.TableSplitTime + datetime.timedelta(0, 1)))
        searchEndTimeV2 = str(max(datetime.datetime.strptime(searchEndTime, '%Y-%m-%d %H:%M:%S'),
                                  self.TableSplitTime + datetime.timedelta(0, 1)))

        # Get charge data in V1 Table
        if searchStartTimeV1.__le__(searchEndTimeV1):
            sql = "SELECT DISTINCT(*) FROM (" \
                  + "(SELECT " + interestedFields \
                  + " FROM " + self.ClickhouseTableV1 \
                  + " WHERE deviceid = '" + vin + "' AND chargingstatus LIKE 'CHARGING_STOPPED%' AND uploadtime >= '" + searchStartTimeV1 + "' AND uploadtime <= '" + searchEndTimeV1 + "')" \
                  + " UNION ALL " \
                  + "(SELECT " + interestedFields + " FROM " \
                  + "(SELECT accmiles FROM " + self.ClickhouseTableV1 \
                  + " WHERE deviceid = '" + vin + "' AND chargingstatus LIKE 'CHARGING_STOPPED%' AND uploadtime >= '" + searchStartTimeV1 + "' AND uploadtime <= '" + searchEndTimeV1 + "'" \
                  + " GROUP BY accmiles) " \
                  + "INNER JOIN " \
                  + "(SELECT " + interestedFields + " FROM " \
                  + self.ClickhouseTableV1 \
                  + " WHERE deviceid = '" + vin + "' AND uploadtime >= '" + searchStartTimeV1 + "' AND uploadtime <= '" + searchEndTimeV1 + "')" \
                  + " USING accmiles)" \
                  + ") ORDER BY uploadtime"
            vinDataTemp.extend(self.client.execute(sql))
        # Get charge data in V2 Table
        if searchStartTimeV2.__le__(searchEndTimeV2):
            sql = "SELECT DISTINCT(*) FROM (" \
                  + "(SELECT " + interestedFields \
                  + " FROM " + self.ClickhouseTableV2 \
                  + " WHERE deviceid = '" + vin + "' AND chargingstatus LIKE 'CHARGING_STOPPED%' AND uploadtime >= '" + searchStartTimeV2 + "' AND uploadtime <= '" + searchEndTimeV2 + "')" \
                  + " UNION ALL " \
                  + "(SELECT " + interestedFields + " FROM " \
                  + "(SELECT accmiles FROM " + self.ClickhouseTableV2 \
                  + " WHERE deviceid = '" + vin + "' AND chargingstatus LIKE 'CHARGING_STOPPED%' AND uploadtime >= '" + searchStartTimeV2 + "' AND uploadtime <= '" + searchEndTimeV2 + "'" \
                  + " GROUP BY accmiles) " \
                  + "INNER JOIN " \
                  + "(SELECT " + interestedFields + " FROM " \
                  + self.ClickhouseTableV2 \
                  + " WHERE deviceid = '" + vin + "' AND uploadtime >= '" + searchStartTimeV2 + "' AND uploadtime <= '" + searchEndTimeV2 + "')" \
                  + " USING accmiles)" \
                  + ") ORDER BY uploadtime"
            vinDataTemp.extend(self.client.execute(sql))
            self.CharData = pd.DataFrame(vinDataTemp)
        return self.CharData

    def GetChargeCycIndexByMileage(self, vinDataTemp):
        """
        get frame indexes where charging cycles begin and end

        :param vinDataTemp: potential data related with charging cycles
        :return self.CharFcycIdxsE: list of frame indexes
        """

        self.CharFcycIdxsS.clear()
        self.CharFcycIdxsE.clear()

        # Reset the mileage value for frames with invalid mileage sig
        # Get shift subtract of mileage vector
        if vinDataTemp.empty:
            return self.CharFcycIdxsS, self.CharFcycIdxsE

        # delete invalid value 999999.9
        vinMile = np.array(vinDataTemp.iloc[:, self.MileIdx]).astype(np.float)
        vinMile[vinMile == 999999.9] = 0
        deltaMileNp = (vinMile[1:].astype(np.float)
                       - vinMile[0:-1].astype(np.float))

        mileSplIdxs = np.intersect1d(np.array(np.where(deltaMileNp > 0)).flatten(),
                                     np.array(np.where(vinMile != 0)).flatten())
        self.CharFcycIdxsS = [0]
        self.CharFcycIdxsS.extend((mileSplIdxs + 1).tolist())
        self.CharFcycIdxsE = (mileSplIdxs + 1).tolist()
        self.CharFcycIdxsE.append(len(vinDataTemp))

        charIdxs = np.array(np.where(vinDataTemp[self.CharStatIdx] == 'CHARGING_STOPPED')).flatten()

        charPureDate = np.array(vinDataTemp)[charIdxs, self.UtIdx]

        charPureDura = (charPureDate[1:] - charPureDate[0:-1]).astype(np.timedelta64)

        charSplIdxs = np.array(np.where(charPureDura > np.timedelta64(self.charDiscDuraPar * 10 ** 6))).flatten()

        self.CharFcycIdxsS.extend((charIdxs[charSplIdxs] + 1).flatten().tolist())
        self.CharFcycIdxsE.extend(charIdxs[charSplIdxs + 1].flatten().tolist())
        self.CharFcycIdxsS = np.sort(np.array(self.CharFcycIdxsS)).tolist()
        self.CharFcycIdxsE = np.sort(np.array(self.CharFcycIdxsE)).tolist()
        return self.CharFcycIdxsS, self.CharFcycIdxsE

    def GetOcVolAndOcSoc(self, dataDf):
        """
        return soc with known temperature and open circuit voltages of each cell
        :param dataDf:
        :return:ocVols, ocSocs
        """
        cellT = self.GetCellTandPackT(np.array(dataDf), self.PrbTempIdx)
        ocVols = self.UpckDataFromStrArr(np.array(dataDf), self.CellVolIdx, self.cellNum, 5, 0)
        try:
            ocSocs = self.GetSocFromOCV(ocVols, cellT)
        except ValueError:
            ocSocs = np.array([])
        return ocVols, ocSocs

    def GetStatInfo(self, dataDf, dbSocLim, dire=-1):
        """
        steady status judgement
        :param dataDf:
        :param dbSocLim:
        :param dire:
        :return:
        """

        def GetErrorAh(dataDfTmp, idxSTmp, direTmp, iTmp):
            """
            calculate possible error ampere hour involved between the beginning of charging and the steady moment
            :param dataDfTmp:
            :param idxSTmp:
            :param direTmp:
            :param iTmp:
            :return:statOcVols, statOcSocs, statErrAh
            """
            if direTmp == -1:
                errorData = dataDfTmp.iloc[iTmp:idxSTmp + 1, :]
                errorI = np.array(dataDfTmp.iloc[iTmp:idxSTmp, self.CurrIdx])
            else:
                errorData = dataDfTmp.iloc[idxSTmp:iTmp + 1, :]
                errorI = np.array(dataDfTmp.iloc[idxSTmp:iTmp, self.CurrIdx])
            errorDura = np.array((pd.to_datetime(errorData[self.UtIdx]) -
                                  pd.to_datetime(errorData[self.UtIdx].shift(1))).dt.seconds)
            errorDuraJumpIdxs = np.where(errorDura > self.sampContiDuraPar + self.sampContiDuraThrPar)
            errorDuraJumpIdxs = np.array(errorDuraJumpIdxs).flatten()
            try:
                errorSocJump = (np.array(errorData.iloc[errorDuraJumpIdxs, self.DbSocIdx]).astype(np.float)
                                - np.array(errorData.iloc[errorDuraJumpIdxs - 1, self.DbSocIdx])
                                .astype(np.float))
                errorSocKeepIdxs = np.array(np.where(errorSocJump < self.socDbRes)).flatten()
                errorSoc100 = np.array(np.where(np.array(errorData.iloc[errorDuraJumpIdxs, self.DbSocIdx])
                                                .astype(np.float) == 100)).flatten()
                errorSocNorJump = np.intersect1d(np.array(np.where(errorSocJump <= self.socDbRes)).flatten()
                                                 , errorSoc100)
                errorDura[errorDuraJumpIdxs[np.unique(
                    np.concatenate((errorSocKeepIdxs, errorSocNorJump))).flatten()]] = self.sampContiDuraPar
                errorDura = errorDura[1:len(errorDura)]
            except IndexError:
                errorDura = errorDura[1:len(errorDura)]
            errorAhTmp = np.sum(np.abs(np.multiply(errorDura, errorI))) / 3600
            return errorAhTmp

        statOcVols = np.array([])
        statOcSocs = np.array([])
        statErrAh = -1
        flag = ''
        date = ''
        tempStr = ''
        lpDura = 0
        if dire == -1:
            idxS = len(dataDf) - 1
            idxE = max(-1, idxS - 60)
        else:
            dire = 1
            idxS = 0
            idxE = min(len(dataDf), idxS + 60)
        for i in range(idxS, idxE, dire):
            if statOcSocs.size != 0:
                break
            if (abs(dataDf.iloc[i, self.DbSocIdx] - dbSocLim) < self.socDbRes
                    or (abs(dataDf.iloc[i, self.DbSocIdx] - dbSocLim) <= self.socDbRes)
                    and max(dataDf.iloc[i, self.DbSocIdx], dbSocLim) == 100):
                if (i != 0 and abs(
                        dataDf.iloc[i, self.DbSocIdx] - dataDf.iloc[i - 1, self.DbSocIdx]) < self.socDbRes and
                        (dataDf.iloc[i, self.UtIdx] - dataDf.iloc[i - 1, self.UtIdx]).seconds > self.staticDiscDuraPar):
                    if dire == 1 and flag != 'LP':
                        flag = 'LP'
                        date = dataDf.iloc[i, self.UtIdx]
                        tempStr = dataDf.iloc[i, self.PrbTempIdx]
                        lpDura = (dataDf.iloc[i, self.UtIdx] - dataDf.iloc[i - 1, self.UtIdx]).seconds / 3600
                    if (abs(dataDf.iloc[i, self.CurrIdx]) < self.staticCurrPar and statOcSocs.size == 0
                            and 0 < float(dataDf.iloc[i, self.MileIdx]) < 999999):
                        statOcVols, statOcSocs = self.GetOcVolAndOcSoc(dataDf.iloc[i, :])
                        statErrAh = GetErrorAh(dataDf, idxS, dire, i)

                if statOcSocs.size != 0:
                    break

                ucharPcsDate = dataDf[self.UtIdx]
                ucharPcsDateThr = (dataDf.iloc[i, self.UtIdx] + dire *
                                   datetime.timedelta(0, (self.sampContiDuraPar - self.sampContiDuraThrPar)
                                                      * self.staticFrmNumPar, 0))
                try:
                    if dire == 1:
                        ucharPcsIdx = (list((ucharPcsDate - ucharPcsDateThr) > datetime.timedelta(0, 0, 0)).index(
                            True) - len(ucharPcsDate))
                    else:
                        ucharPcsIdx = (list((ucharPcsDate - ucharPcsDateThr) > datetime.timedelta(0, 0, 0)).index(
                            True) - len(ucharPcsDate) - 1)
                except ValueError:
                    ucharPcsIdx = idxS - dire

                cellVolTemp, volStd, currMax = self.GetStdVol(np.array(dataDf.iloc[range(i - len(ucharPcsDate),
                                                                                         ucharPcsIdx, dire),
                                                                       :]), self.CurrIdx, self.CellVolIdx)
                if (not volStd.size == 0) and (0 < np.max(volStd) < self.staticVolStdPar):
                    if currMax < self.staticCurrPar and statOcSocs.size == 0:
                        statOcVols, statOcSocs = self.GetOcVolAndOcSoc(dataDf.iloc[max(ucharPcsIdx + dire, i), :])
                        statErrAh = GetErrorAh(dataDf, idxS, dire, i)
                        if dire == 1 and flag != 'LP':
                            flag = 'Normal'
                            date = dataDf.iloc[i, self.UtIdx]
                            tempStr = dataDf.iloc[i, self.PrbTempIdx]

            else:
                break
        if dire == -1:
            return statOcVols, statOcSocs, statErrAh
        else:
            return statOcVols, statOcSocs, statErrAh, flag, str(date), '[' + tempStr.replace(',', ';') + ']', lpDura

    def GetPureChardepth(self, vinDataDf, charFcycIdxsSLst, charFcycIdxsELst):
        if vinDataDf.empty:
            return self.CharInfoList
        self.vin = vinDataDf.iloc[0, self.VinIdx]
        projStr = self.GetProjectParamByVin(self.vin)
        accSoc = 0
        charMileS = 0
        charMileE = 0
        charSocS = 0
        charSocE = 0
        for charFcycIdxS, charFcycIdxE in zip(charFcycIdxsSLst, charFcycIdxsELst):
            # Split out the full charge cycle data(data with same mileage and contains at least one continuous charge
            # cycle)
            charFcycData = pd.DataFrame(vinDataDf.iloc[charFcycIdxS:charFcycIdxE, :])

            if charFcycData.empty:
                continue
            charMile = mode(np.array(charFcycData.iloc[:, self.MileIdx]).astype(np.float))[0][0]
            if charMileS == 0 and 0 < charMile < 999999:
                charMileS = charMile
                charSocS = accSoc
            if 0 < charMile < 999999:
                charMileE = charMile
                charSocE = accSoc
            try:
                charPcycIdxS = list(charFcycData[self.CharStatIdx].str.contains('CHARGING_STOPPED')).index(True)
                charPcycIdxE = len(charFcycData) - list(charFcycData[self.CharStatIdx].str.contains('CHARGING_STOPPED')
                                                        )[-1:-len(charFcycData) - 1:-1].index(True)
            except ValueError:
                charPcycIdxS = len(charFcycData)
                charPcycIdxE = 0
                continue
            # accumulate charge SOC
            accSoc += (max(int(charFcycData.iloc[min(charPcycIdxE, len(charFcycData) - 1), self.DbSocIdx]),
                           int(charFcycData.iloc[charPcycIdxE - 1, self.DbSocIdx])) -
                       min(int(charFcycData.iloc[max(charPcycIdxS - 1, 0), self.DbSocIdx]),
                           int(charFcycData.iloc[charPcycIdxS, self.DbSocIdx])))
        return [self.vin, charSocS, charSocE, charMileS, charMileE]

    def GetChargeCycInfo(self, vinDataDf, charFcycIdxsSLst, charFcycIdxsELst):
        """
        get charge cycle infomation of specific vin in specific time range

        :param charFcycIdxsSLst:
        :param vinDataDf: potential data related with charging cycles
        :param charFcycIdxsELst: frame indexes where charging cycles begin and end
        :return self.CharInfoList: list features of each charging cycle [vin, charge start
        time, charge end time,  dashboard start soc, dashboard end soc, dashboard charge depth, calculated start soc,
        calculated end soc, calculated charge depth, before charge status, after charge status, charge integrated
        ampere, AC/DC, charge temperature feature, charge current feature, charge SOH] is expected
        :return self.SocJumpAbnData: dataframe abnormal soc jump data during charging
        """

        # return is Charge data container is empty
        self.CharInfoList.clear()
        if vinDataDf.empty:
            return self.CharInfoList

        # Initialising

        tempListRow = []
        accSoc = 0

        self.vin = vinDataDf.iloc[0, self.VinIdx]
        projStr = self.GetProjectParamByVin(self.vin)
        # has been switched to the project intrinsic parameters
        # # get the cellNum and probeNum appeared most frequently
        # self.cellNum = np.argmax(np.bincount(vinDataTemp.iloc[:, 11].apply(lambda x: self.DefaultInvalidInt(x))))
        # self.probeNum = np.argmax(np.bincount(vinDataTemp.iloc[:, 12].apply(lambda x: self.DefaultInvalidInt(x))))

        # Go through each charge cycle
        for charFcycIdxS, charFcycIdxE in zip(charFcycIdxsSLst, charFcycIdxsELst):
            # Initialise the temporal variables of charge features
            currLst = []
            duraLst = []
            charCycDura = 0
            fullCharHitFlg = False
            fullCharVol = -1
            charMile = 0
            charCurrAbnStr = ""
            charCycIntAh = 0
            charUcCycIntAh = 0
            charNCycIntAh = 0
            charNCycDura = 0
            charUcCycDura = 0
            ocVolSArr = np.array([])
            ocSocSArr = np.array([])
            ocVolEArr = np.array([])
            ocSocEArr = np.array([])
            depolarVolSArr = np.array([])
            depolarVolEArr = np.array([])
            depolarSocSArr = np.array([])
            depolarSocEArr = np.array([])
            cellOhmRS = np.array([])
            cellOhmRE = np.array([])
            cellOhmREDepol = np.array([])
            IS0 = -1
            IS1 = -1
            IE0 = -1
            IE1 = -1
            errorAhStatS = 0
            errorAhStatE = 0
            socAbnDscStr = ""
            abnDscDtStr = ""
            socAbnIncStr = ""
            abnIncDrStr = ""
            abnIncIStr = ""
            abnDscIstr = ""
            abnIncDSocStr = ""
            abnDscDsocStr = ""
            charTempSArr = np.array([])
            charTempEArr = np.array([])
            depolarcellTEArr = np.array([])
            charTempDifArr = np.array([])
            charMxTempDif = 0
            charMeanTempDif = 0
            charStdTempDif = 0
            cMStr = 'AC'
            cellRc = np.array([])
            cellOhm = np.array([])
            cellPR = np.array([])
            lpDuraE = 0

            # Split out the full charge cycle data(data with same mileage and contains at least one continuous charge
            # cycle)
            charFcycData = pd.DataFrame(vinDataDf.iloc[charFcycIdxS:charFcycIdxE, :])

            if charFcycData.empty:
                continue

            charMile = charFcycData.iloc[0, self.MileIdx]

            # Get the first frame index in the full charge cycle where the charging status changes from non-charge to
            # charge_stopped
            # Get the last frame index in the full charge cycle where the charging status changes from charge_stopped
            # to non-charge
            try:
                charPcycIdxS = list(charFcycData[self.CharStatIdx].str.contains('CHARGING_STOPPED')).index(True)
                charPcycIdxE = len(charFcycData) - list(charFcycData[self.CharStatIdx].str.contains('CHARGING_STOPPED')
                                                        )[-1:-len(charFcycData) - 1:-1].index(True)
            except ValueError:
                charPcycIdxS = len(charFcycData)
                charPcycIdxE = 0
                continue

            # Get potential charge data in which the data begins which charge_stopped status and end with charge_stopped
            # status
            charPcycData = charFcycData.iloc[charPcycIdxS:charPcycIdxE, :]
            if charPcycData.empty:
                continue

            # internal resistance calculation (RC)
            if (charPcycIdxE < len(charFcycData) - 1 and (
                    pd.to_datetime(charFcycData.iloc[charPcycIdxE + 1, self.UtIdx]) -
                    pd.to_datetime(charFcycData.iloc[charPcycIdxE, self.UtIdx])).seconds <
                    self.sampContiDuraPar + self.sampContiDuraThrPar):
                cellOhmRE, IE0, IE1 = self.GetDynR(np.array(charFcycData.iloc[charPcycIdxE - 1:charPcycIdxE + 1, :]),
                                                   self.CurrIdx, self.CellVolIdx)
                cellOhmRE = cellOhmRE.flatten()
            if (charPcycIdxS > 0 and ((pd.to_datetime(charFcycData.iloc[charPcycIdxS, self.UtIdx]) -
                                       pd.to_datetime(charFcycData.iloc[charPcycIdxS - 1, self.UtIdx])).seconds <
                                      self.sampContiDuraPar + self.sampContiDuraThrPar or charFcycData.iloc[
                                          charPcycIdxS, self.DbSocIdx]
                                      == charFcycData.iloc[charPcycIdxS - 1, self.DbSocIdx])):
                cellOhmRS, IS0, IS1 = self.GetDynR(np.array(charFcycData.iloc[charPcycIdxS - 1:charPcycIdxS + 1, :]),
                                                   self.CurrIdx, self.CellVolIdx)
                cellOhmRS = cellOhmRS.flatten()

                # cell voltage depolarization
                try:
                    deltat = np.array((pd.to_datetime(charFcycData.iloc[charPcycIdxS:charPcycIdxS + 5, self.UtIdx]) -
                                       pd.to_datetime(charFcycData.iloc[charPcycIdxS:charPcycIdxS + 5, self.UtIdx])
                                       .shift(1)).dt.seconds)
                    if ((self.sampContiDuraPar - self.sampContiDuraThrPar < deltat[1:]).all() and
                            (deltat[1:] < self.sampContiDuraPar + self.sampContiDuraThrPar).all()):
                        currs = np.array(charFcycData.iloc[charPcycIdxS - 1:charPcycIdxE, self.CurrIdx]
                                         ).astype(np.float)
                        cellVols = self.UpckDataFromStrArr(np.array(
                            charFcycData.iloc[charPcycIdxS - 1:charPcycIdxS + 5, :]),
                            self.CellVolIdx, self.cellNum, 5, 0)
                        if np.std(currs[1:]) < 0.5 and cellVols.size / self.cellNum > 5:
                            cellVols0 = np.mean(cellVols[1:4, :], axis=0)
                            cellVols1 = np.mean(cellVols[2:5, :], axis=0)
                            cellVols2 = np.mean(cellVols[3:6, :], axis=0)
                            if ((cellVols1 - cellVols0 > 0).all() and
                                    ((cellVols2 - cellVols1) / (cellVols1 - cellVols0) < 0.99).all() and
                                    ((cellVols2 - cellVols1) / (cellVols1 - cellVols0) > 0.01).all()):
                                cellRcEq = np.power((cellVols2 - cellVols1) / (cellVols1 - cellVols0)
                                                    , 1 / (np.mean(deltat[1:]) / 0.1))
                                cellRc = cellRcEq * 0.1 / (1 - cellRcEq)
                                cellOhmPrR2 = -(cellVols2 - cellVols[0, :]) / (np.mean(currs[3:6]) - currs[0])
                                cellOhmPrR1 = -(cellVols0 - cellVols[0, :]) / (np.mean(currs[1:4]) - currs[0])
                                cellPR = (cellOhmPrR2 - cellOhmPrR1) / (
                                        -np.e ** (-np.mean(deltat[1:]) * 3.5 / cellRc) + np.e ** (-np.mean(deltat[1:]) * 1.5 / cellRc))
                                cellOhm = cellOhmPrR2 - (1 - np.e ** (-np.mean(deltat[1:]) * 3.5 / cellRc)) * cellPR
                                cellOhmPR = cellPR + cellOhm
                                cellDrVIEq = (cellOhmPR * 0.1 * np.mean(currs[1:])) / (cellRc + 0.1)
                                cellDv = ((-(cellVols1 - cellVols0) - (np.power(cellRcEq, np.mean(deltat[1:]) / 0.1) - 1) /
                                           (cellRcEq - 1) * cellDrVIEq) / (np.power(cellRcEq, np.mean(deltat[1:]) / 0.1) - 1))
                                depolarVolSArr = cellVols0 + cellDv
                                cellT = self.GetCellTandPackT(np.array(charFcycData.iloc[charPcycIdxS:charPcycIdxS + 5, :]),
                                                              self.PrbTempIdx)
                                depolarSocSArr = self.GetSocFromOCV(depolarVolSArr, np.mean(cellT, axis=0))
                except ValueError or IndexError:
                    pass

            # get the charge status vector of potential charge data
            # find the frame indexes with charge_stopped status(indexes in Potential charge data arrays)
            # change the status charge_stopped to 1
            # change the status non-charge to 0
            charPcycCharStat = charPcycData[self.CharStatIdx].map(lambda x: {'CHARGING_STOPPED': 1}.setdefault(x, 0))
            if np.sum(charPcycCharStat) < 1:
                continue

            # find the frame indexes at which the charge status changes from charge_stopped to non-charge and vice-versa
            charPcycStepIdxs = [0]
            CharPcycStepFlg = (charPcycCharStat - charPcycCharStat.shift(1) != 0)
            charPcycStepIdxs.extend((np.array(np.where(CharPcycStepFlg[1:].__eq__(True))) + 1).flatten().tolist())
            charPcycStepIdxs.append(len(charPcycCharStat))

            # accumulate charge SOC
            accSoc += (max(int(charFcycData.iloc[min(charPcycIdxE, len(charFcycData) - 1), self.DbSocIdx]),
                           int(charFcycData.iloc[charPcycIdxE - 1, self.DbSocIdx])) -
                       min(int(charFcycData.iloc[max(charPcycIdxS - 1, 0), self.DbSocIdx]),
                           int(charFcycData.iloc[charPcycIdxS, self.DbSocIdx])))

            if (max(int(charFcycData.iloc[min(charPcycIdxE, len(charFcycData) - 1), self.DbSocIdx]),
                    int(charFcycData.iloc[charPcycIdxE - 1, self.DbSocIdx])) == 100):
                fullCharHitFlg = True
                fullCharVol = self.UpckDataFromStrArr(np.array(charFcycData.iloc[charPcycIdxE - 1, :]),
                                                      self.CellVolIdx, self.cellNum, 5, 0)

            try:
                ocVolSArr, ocSocSArr, errorAhStatS = \
                    self.GetStatInfo(charFcycData.iloc[0:charPcycIdxS + 1, :], charFcycData.iloc[charPcycIdxS,
                                                                                                 self.DbSocIdx], -1)

            except IndexError:
                continue

            try:
                ocVolEArr, ocSocEArr, errorAhStatE, flag, dateStatE, tempStatE, lpDuraE = \
                    self.GetStatInfo(charFcycData.iloc[charPcycIdxE - 1:, :], charFcycData.iloc[charPcycIdxE - 1,
                                                                                                self.DbSocIdx], 1)
                if flag.__eq__('LP'):
                    dateStatELim = datetime.datetime.strftime(datetime.datetime.strptime(dateStatE, '%Y-%m-%d %H:%M:%S')
                                                              + datetime.timedelta(0, 5 * 60), '%Y-%m-%d %H:%M:%S')
                    sql = "(SELECT " + self.InterestedFields + " FROM " \
                          + self.ClickhouseTableV1 \
                          + " WHERE deviceid = '" + self.vin + "' AND uploadtime >= '" + dateStatE + "'" \
                          + " ORDER BY uploadtime LIMIT 100)"
                    vinDataTemp = pd.DataFrame(self.client.execute(sql))
                    sql = "(SELECT " + self.InterestedFields + " FROM " \
                          + self.ClickhouseTableV2 \
                          + " WHERE deviceid = '" + self.vin + "' AND uploadtime >= '" + dateStatE + "'" \
                          + " ORDER BY uploadtime LIMIT 100)"
                    vinDataTemp = vinDataTemp.append(pd.DataFrame(self.client.execute(sql)), ignore_index=True)
                    vinDataTemp = vinDataTemp.iloc[0:min(100, len(vinDataTemp)), :]
                    if vinDataTemp.empty:
                        continue
                    socTemp = vinDataTemp[self.DbSocIdx]
                    try:
                        duraStatE0 = (pd.to_datetime(vinDataTemp[self.UtIdx]) -
                                      pd.to_datetime(vinDataTemp[self.UtIdx]).shift(1)).dt.seconds
                        hintStatE0 = duraStatE0 < self.sampContiDuraPar + self.sampContiDuraThrPar
                        hintStatE1 = abs(socTemp - socTemp.iloc[0]) < 10
                        duraStatE1 = (pd.to_datetime(vinDataTemp[self.UtIdx]) -
                                      pd.to_datetime(vinDataTemp.iloc[0, self.UtIdx])).dt.seconds
                        hintStatE2 = duraStatE1 < self.staticDiscDuraPar * 6
                        tempStatE0 = pd.DataFrame([])
                        tempStatE0[0] = vinDataTemp[self.MxTIdx].astype(np.float)
                        tempStatE0[1] = vinDataTemp[self.MiTIdx].astype(np.float)
                        tempStatE = tempStatE0.mean(axis=1)
                        hintStatE3 = abs(tempStatE - tempStatE.iloc[0]) < 5
                        idxStatE0 = np.array(vinDataTemp[hintStatE0 & hintStatE1 & hintStatE2 & hintStatE3].index)
                        idxStatE1 = idxStatE0 - 1
                        candiDataArr0 = np.array(vinDataTemp)[idxStatE0, :]
                        candiDataArr1 = np.array(vinDataTemp)[idxStatE1, :]

                        if candiDataArr0.size / len(self.InterestedFLst) > 5:
                            cellVols0, avahint0 = self.UpckDataFromStrArr(candiDataArr0, self.CellVolIdx,
                                                                          self.cellNum, 5, 0, 1)
                            cellVols1, avahint1 = self.UpckDataFromStrArr(candiDataArr1, self.CellVolIdx,
                                                                          self.cellNum, 5, 0, 1)
                            avahint = np.logical_and(avahint0, avahint1)
                            dv = cellVols0[avahint1[avahint0]] - cellVols1[avahint0[avahint1]]
                            currTemp0 = candiDataArr0[avahint, self.CurrIdx]
                            currTemp1 = candiDataArr1[avahint, self.CurrIdx]
                            dI = np.reshape(np.repeat(currTemp1 - currTemp0, self.cellNum), [int(dv.size/self.cellNum),
                                                                                             self.cellNum])
                            ohmREBArr = np.divide(dv[currTemp1 - currTemp0 != 0, :], dI[currTemp1 - currTemp0 != 0, :])
                            q1 = np.percentile(np.mean(ohmREBArr, axis=1), 25)
                            q3 = np.percentile(np.mean(ohmREBArr, axis=1), 75)
                            if ohmREBArr[np.logical_and(np.mean(ohmREBArr, axis=1) > q1,
                                                                     np.mean(ohmREBArr, axis=1) < q3), :].size > 0:
                                cellOhmREDepol = np.mean(ohmREBArr[np.logical_and(np.mean(ohmREBArr, axis=1) > q1,
                                                                         np.mean(ohmREBArr, axis=1) < q3), :], axis=0)
                                depolarVolEArr = cellVols1[0, :] + currTemp1[0] * cellOhmREDepol
                                depolarcellTEArr = self.GetCellTandPackT(candiDataArr1, self.PrbTempIdx)
                                depolarSocEArr = self.GetSocFromOCV(depolarVolEArr, np.mean(depolarcellTEArr, axis=0))
                    except ValueError or IndexError:
                        pass

            except IndexError:
                continue

            # charging Ah integration
            for i in range(0, len(charPcycStepIdxs) - 1):
                # Get pieces of data with same charge status
                charCycPcsData = charPcycData.iloc[charPcycStepIdxs[i]:charPcycStepIdxs[i + 1], :]
                charCycPcsStat = charCycPcsData.iloc[0, self.CharStatIdx]
                if charCycPcsStat == 'CHARGING_STOPPED':
                    # calculate the shift subtract of upload time vector in continuous charge pieces
                    charCycPcsDate = charCycPcsData[self.UtIdx]
                    charCycPcsDura = np.array((pd.to_datetime(charCycPcsDate) - pd.to_datetime(charCycPcsDate).shift(
                        1)).dt.seconds)
                    # define the missing time period within the continuous charging pieces as uncertain duration
                    charUcIdx = np.array(
                        np.where(charCycPcsDura > self.sampContiDuraPar + self.sampContiDuraThrPar))
                    # sum all the uncertain time duration
                    charUcCycDura += np.sum(charCycPcsDura[charUcIdx] - self.sampContiDuraPar)
                    # calculate the charging periods
                    if charPcycStepIdxs[i + 1] == len(charPcycData) and charPcycIdxE == len(charFcycData):
                        charCycPcsDura = np.append(charCycPcsDura[1:len(charCycPcsDura)], self.sampContiDuraPar)
                    elif charPcycStepIdxs[i + 1] == len(charPcycData) and charPcycIdxE < len(charFcycData):
                        charCycPcsDura = np.append(charCycPcsDura[1:len(charCycPcsDura)], min(self.sampContiDuraPar, (
                                charFcycData.iloc[charPcycIdxE, self.UtIdx] -
                                charFcycData.iloc[charPcycIdxE - 1, self.UtIdx]).seconds))
                    else:
                        charCycPcsDura = np.append(charCycPcsDura[1:len(charCycPcsDura)], min(self.sampContiDuraPar, (
                                charPcycData.iloc[charPcycStepIdxs[i + 1], self.UtIdx] -
                                charPcycData.iloc[charPcycStepIdxs[i + 1] - 1, self.UtIdx]).seconds))
                    # calculate the integral ampere value
                    charCycPcsI = np.array(charCycPcsData[self.CurrIdx]).astype(np.float)
                    charCycIntAh += np.sum(np.multiply(charCycPcsI, charCycPcsDura)) / 3600

                    # abnormal SOC jump during charging
                    charCycPcsSoc = np.array(charCycPcsData[self.DbSocIdx]).astype(np.float)
                    charCycPcsSocStep = charCycPcsSoc[1:len(charCycPcsSoc)] - charCycPcsSoc[0:-1]
                    SocAbnDscIdxs = np.where(charCycPcsSocStep < 0)
                    SocAbnIncIdxs = np.where(charCycPcsSocStep > 1)
                    try:
                        if charCycPcsDura[SocAbnDscIdxs].size > 0:
                            abnDscDtStr = abnDscDtStr + np.str(charCycPcsDura[SocAbnDscIdxs])
                            abnDscDsocStr = abnDscDsocStr + np.str(charCycPcsSocStep[SocAbnDscIdxs])
                            self.SocJumpAbnData = self.SocJumpAbnData.append(charCycPcsData)
                            allDatetime = np.array(charCycPcsDate)
                            socAbnDscStr = socAbnDscStr + "," + ",".join(allDatetime[SocAbnDscIdxs].astype(np.str))
                            abnDscIstr = abnDscIstr + "," + np.str(charCycPcsI[SocAbnDscIdxs])
                    except ValueError and IndexError:
                        print(0)

                    try:
                        if charCycPcsDura[SocAbnIncIdxs].size > 0:
                            self.SocJumpAbnData = self.SocJumpAbnData.append(charCycPcsData)
                            abnIncDrStr = abnIncDrStr + np.str(charCycPcsDura[SocAbnIncIdxs])
                            abnIncDSocStr = abnIncDSocStr + np.str(charCycPcsSocStep[SocAbnIncIdxs])
                            allDatetime = np.array(charCycPcsDate)
                            socAbnIncStr = socAbnIncStr + "," + ",".join(allDatetime[SocAbnIncIdxs].astype(np.str))
                            abnIncIStr = abnIncIStr + "," + np.str(charCycPcsI[SocAbnIncIdxs])
                    except ValueError and IndexError:
                        print(0)

                    # possible uncertain integrated ampere hour
                    try:
                        charUcCycPcsI = charCycPcsI[charUcIdx] - charCycPcsI[charUcIdx - 1]
                        charUcCycIntAh += np.sum(np.multiply(charCycPcsDura[charUcIdx], charUcCycPcsI)) / 3600
                    except IndexError:
                        charUcCycIntAh += 0
                    # accumulate the charging periods
                    charCycDura += np.sum(charCycPcsDura)

                    maxTemp = np.max(np.array(charCycPcsData.iloc[:, self.MxTIdx]).astype(np.float))
                    maxCurr = np.max(-charCycPcsI)

                    if maxCurr > self.ACCurrThr:
                        cMStr = 'DC'
                    elif maxTemp > self.CurrLimTempThr and cMStr != 'DC':
                        cMStr = 'Unknown High Temp Charging'
                    elif maxTemp > self.CurrLimTempThr and cMStr == 'DC':
                        cMStr = 'DC + High Temp Charging'

                    # current change hist bin
                    currLst.extend(charCycPcsI.tolist())
                    duraLst.extend(np.array((pd.to_datetime(charCycPcsDate) - pd.to_datetime(
                        charFcycData.iloc[0, self.UtIdx])).dt.seconds).tolist())
                else:
                    # Calculate the non charge status duration and the possible non charge status Ah
                    charNCycDura += (charPcycData.iloc[charPcycStepIdxs[i + 1], self.UtIdx] -
                                     charPcycData.iloc[charPcycStepIdxs[i], self.UtIdx]).seconds + \
                                    (charPcycData.iloc[charPcycStepIdxs[i], self.UtIdx] -
                                     charPcycData.iloc[charPcycStepIdxs[i] - 1, self.UtIdx]).seconds \
                                    - charCycPcsDura[-1]
                    charNCycPcsDura = np.array([(charPcycData.iloc[charPcycStepIdxs[i], self.UtIdx] - charPcycData.iloc[
                        charPcycStepIdxs[i] - 1, self.UtIdx]).seconds - charCycPcsDura[-1]])
                    charNCycPcsDuraTemp = np.array(
                        (pd.to_datetime(charPcycData.iloc[charPcycStepIdxs[i]:charPcycStepIdxs[
                            i + 1], self.UtIdx]) - pd.to_datetime(
                            charPcycData.iloc[charPcycStepIdxs[i]:charPcycStepIdxs[i + 1], self.UtIdx])
                         .shift(1)).dt.seconds)
                    charNCycPcsDura = np.append(charNCycPcsDura, charNCycPcsDuraTemp[1:len(charNCycPcsDuraTemp)])
                    charNCycPcsDura[-1] = (charNCycPcsDura[-1] + (charPcycData.iloc[charPcycStepIdxs[i + 1], self.UtIdx]
                                                                  - charPcycData.iloc[
                                                                      charPcycStepIdxs[i + 1] - 1, self.UtIdx]).seconds)
                    charNCycPcsI = np.array(charPcycData.iloc[charPcycStepIdxs[i]:charPcycStepIdxs[i + 1],
                                            self.CurrIdx])
                    charNCycIntAh += np.sum(np.abs(np.multiply(charNCycPcsI, charNCycPcsDura))) / 3600

            # current interpolation and differential and hist bin
            if np.array(duraLst).size < 2:
                continue

            charTempSArr = self.UpckDataFromStrArr(np.array(charFcycData.iloc[charPcycIdxS, :]), self.PrbTempIdx,
                                                   self.probeNum, 85, -40)

            charTempEArr = self.UpckDataFromStrArr(np.array(charFcycData.iloc[charPcycIdxE - 1, :]), self.PrbTempIdx,
                                                   self.probeNum, 85, -40)

            if charTempSArr.size > 0 and charTempEArr.size > 0:
                charTempDifArr = (charTempEArr - charTempSArr) / charCycDura * 60 * 60
                charMxTempDif = np.max(charTempDifArr)
                charMeanTempDif = np.mean(charTempDifArr)
                charStdTempDif = np.std(charTempDifArr)

            # TODO: need more info for current consistency judgement
            finterp = interpolate.interp1d(np.array(duraLst), np.array(currLst), kind='linear')
            currIntTmp = finterp(range(np.min(np.array(duraLst)), np.max(np.array(duraLst)), 1)).flatten()
            currMean = np.mean(currIntTmp)
            currMax = np.max(currIntTmp)
            currMin = np.min(currIntTmp)
            currStd = np.std(currIntTmp)

            CurrJumpTemp = currIntTmp[1:] - currIntTmp[0:-1]
            if CurrJumpTemp.size > 0:
                currJumpMean = np.mean(np.round(CurrJumpTemp, 1))
                currJumpStd = np.std(np.round(CurrJumpTemp, 1))
            else:
                currJumpMean = 0
                currJumpStd = -1

            JumpIdx = np.sort(np.unique(np.hstack((np.array(np.where(CurrJumpTemp > currJumpMean + currJumpStd * 2)
                                                            ).flatten(), np.array(np.where(CurrJumpTemp < currJumpMean -
                                                                                           currJumpStd * 2)).flatten()))))

            tempListRow.clear()
            tempListRow.append(self.vin)
            tempListRow.append(cMStr)
            tempListRow.append(fullCharHitFlg)
            # tempListRow.append(currJumpMean)
            # tempListRow.append(currJumpStd)
            tempListRow.extend([currMin, currMax, currMean, currStd, currJumpMean, currJumpStd])
            tempListRow.append(JumpIdx.__str__())
            tempListRow.append(charMile)
            tempListRow.append(accSoc)
            tempListRow.append(str(charFcycData.iloc[charPcycIdxS, self.UtIdx]))
            tempListRow.append(str(charFcycData.iloc[charPcycIdxE - 1, self.UtIdx]))
            tempListRow.append(charCycDura / 60 / 60)
            tempListRow.append(-charCycIntAh)
            tempListRow.append(self.User2BMSSoc(charFcycData.iloc[charPcycIdxS, self.DbSocIdx]))
            tempListRow.append(self.User2BMSSoc(charFcycData.iloc[charPcycIdxE - 1, self.DbSocIdx]))
            tempListRow.append(self.GetPackSoc(projStr, ocSocSArr))
            tempListRow.append(self.GetPackSoc(projStr, depolarSocSArr))
            tempListRow.append(self.GetPackSoc(projStr, ocSocEArr))
            tempListRow.append(self.GetPackSoc(projStr, depolarSocEArr))
            tempListRow.append(errorAhStatS)
            tempListRow.append(errorAhStatE)

            # delta pack soc
            if (self.GetPackSoc(projStr, ocSocEArr) != -1 and self.GetPackSoc(projStr, ocSocSArr) != -1 and
                    (ocSocEArr - ocSocSArr > 50).all()):
                tempListRow.append(self.GetPackSoc(projStr, ocSocEArr) - self.GetPackSoc(projStr, ocSocSArr))
                sohs = - charCycIntAh / (ocSocEArr - ocSocSArr) * 100
                packsoh1 = - charCycIntAh / (
                        self.GetPackSoc(projStr, ocSocEArr) - self.GetPackSoc(projStr, ocSocSArr)) * 100
                packsoh2 = np.min(np.multiply(ocSocSArr / 100, sohs)) + (-charCycIntAh) + np.min(
                    np.multiply(1 - ocSocEArr / 100, sohs))
                tempListRow.append(np.min(sohs))
                tempListRow.append(sohs.__str__())
                tempListRow.append(packsoh1)
                tempListRow.append(packsoh2)
            else:
                tempListRow.append(-1)
                tempListRow.append(-1)
                tempListRow.append('[]')
                tempListRow.append(-1)
                tempListRow.append(-1)

            # delta pack soc
            if (self.GetPackSoc(projStr, ocSocEArr) != -1 and self.GetPackSoc(projStr, depolarSocSArr) != -1 and
                    (ocSocEArr - depolarSocSArr > 50).all()):
                tempListRow.append(self.GetPackSoc(projStr, ocSocEArr) - self.GetPackSoc(projStr, depolarSocSArr))
                sohs = - charCycIntAh / (ocSocEArr - depolarSocSArr) * 100
                packsoh1 = - charCycIntAh / (
                        self.GetPackSoc(projStr, ocSocEArr) - self.GetPackSoc(projStr, depolarSocSArr)) * 100
                packsoh2 = np.min(np.multiply(depolarSocSArr / 100, sohs)) + (-charCycIntAh) + np.min(
                    np.multiply(1 - ocSocEArr / 100, sohs))
                tempListRow.append(np.min(sohs))
                tempListRow.append(sohs.__str__())
                tempListRow.append(packsoh1)
                tempListRow.append(packsoh2)
            else:
                tempListRow.append(-1)
                tempListRow.append(-1)
                tempListRow.append('[]')
                tempListRow.append(-1)
                tempListRow.append(-1)

            # delta pack soc
            if (self.GetPackSoc(projStr, depolarSocEArr) != -1 and self.GetPackSoc(projStr, depolarSocSArr) != -1 and
                    (depolarSocEArr - depolarSocSArr > 50).all()):
                tempListRow.append(self.GetPackSoc(projStr, depolarSocEArr) - self.GetPackSoc(projStr, depolarSocSArr))
                sohs = - charCycIntAh / (depolarSocEArr - depolarSocSArr) * 100
                packsoh1 = - charCycIntAh / (
                        self.GetPackSoc(projStr, depolarSocEArr) - self.GetPackSoc(projStr, depolarSocSArr)) * 100
                packsoh2 = np.min(np.multiply(depolarSocSArr / 100, sohs)) + (-charCycIntAh) + np.min(
                    np.multiply(1 - depolarSocEArr / 100, sohs))
                tempListRow.append(np.min(sohs))
                tempListRow.append(sohs.__str__())
                tempListRow.append(packsoh1)
                tempListRow.append(packsoh2)
            else:
                tempListRow.append(-1)
                tempListRow.append(-1)
                tempListRow.append('[]')
                tempListRow.append(-1)
                tempListRow.append(-1)

            # if fullCharHitFlg == True and self.GetPackSoc(proj, charCycCalSocS) != -1:
            #     packsoh3 = np.min(np.multiply(charCycCalSocS / 100, sohs)) + (-charCycIntAh)
            #     tempListRow.append(packsoh3)
            # else:
            #     tempListRow.append(-1)
            tempListRow.append(fullCharVol.__str__())
            tempListRow.append(ocVolSArr.__str__())
            tempListRow.append(depolarVolSArr.__str__())
            tempListRow.append(depolarVolEArr.__str__())
            tempListRow.append(ocVolEArr.__str__())
            tempListRow.append(charNCycDura)
            tempListRow.append(charUcCycDura)
            tempListRow.append(ocSocSArr.__str__())
            tempListRow.append(depolarSocSArr.__str__())
            tempListRow.append(depolarSocEArr.__str__())
            tempListRow.append(ocSocEArr.__str__())
            tempListRow.append(socAbnDscStr)
            tempListRow.append(abnDscDtStr)
            tempListRow.append(abnDscDsocStr)
            tempListRow.append(abnDscIstr)
            tempListRow.append(socAbnIncStr)
            tempListRow.append(abnIncDrStr)
            tempListRow.append(abnIncDSocStr)
            tempListRow.append(abnIncIStr)
            tempListRow.append(cellRc.__str__())
            tempListRow.append(cellPR.__str__())
            tempListRow.append(cellOhm.__str__())
            tempListRow.append(cellOhmRS.__str__())
            tempListRow.append(IS0)
            tempListRow.append(IS1)
            if cellOhmRS.size > 0:
                tempListRow.append(np.mean(cellOhmRS))
                tempListRow.append(np.std(cellOhmRS))
            else:
                tempListRow.append(-1)
                tempListRow.append(-1)
            tempListRow.append(cellOhmRE.__str__())
            tempListRow.append(IE0)
            tempListRow.append(IE1)
            if cellOhmRE.size > 0:
                tempListRow.append(np.mean(cellOhmRE))
                tempListRow.append(np.std(cellOhmRE))
            else:
                tempListRow.append(-1)
                tempListRow.append(-1)
            if cellOhmREDepol.size > 0:
                tempListRow.append(cellOhmREDepol.__str__())
            else:
                tempListRow.append(-1)
            tempListRow.append(charTempSArr.__str__())
            tempListRow.append(charTempEArr.__str__())
            tempListRow.append(charTempDifArr.__str__())
            tempListRow.append(charMxTempDif)
            tempListRow.append(charMeanTempDif)
            tempListRow.append(charStdTempDif)
            tempListRow.append(depolarcellTEArr.__str__())
            if depolarcellTEArr.size > 0:
                tempListRow.append(np.mean(depolarcellTEArr))
                tempListRow.append(np.std(depolarcellTEArr))
            else:
                tempListRow.append(-1)
                tempListRow.append(-1)
            tempListRow.append(lpDuraE)

            self.CharInfoList.append(tempListRow[::])

        return self.CharInfoList, self.SocJumpAbnData


def MEBCharSocJumpAnalysis():
    searchSTimeTemp = '2019-01-01 00:00:00'
    searchETimeTemp = '2021-05-13 00:00:00'
    ca = CharCycleAnalysis()

    vinInfo82 = ca.GetVinListForSpecificProject(ca.ClickhouseTableV2, 'MEB82', searchSTimeTemp, searchETimeTemp, [])
    vinInfo55 = ca.GetVinListForSpecificProject(ca.ClickhouseTableV2, 'MEB55', searchSTimeTemp, searchETimeTemp, [])

    vinListTemp = vinInfo82[0]
    vinListTemp.extend(vinInfo55[0])

    for i in range(57, 70):
        vin = vinListTemp[i]
        print(vin + "START" + str(datetime.datetime.now()))
        vinDataTemp = ca.GetChardataByVin(vin, searchSTimeTemp, searchETimeTemp)

        charFcycIdxsETemp = ca.GetChargeCycIndexByMileage(vinDataTemp)
        charInfoListTemp, abnData = ca.GetChargeCycInfo(vinDataTemp, charFcycIdxsETemp)
        print(vin + "END" + str(datetime.datetime.now()))

    pd.DataFrame(charInfoListTemp).to_excel(r"D:\WorkSpace\Python\MEBcycinfo.xlsx")
    pd.DataFrame(abnData).to_excel(r"D:\WorkSpace\Python\MEBSOCabndata.xlsx")


def main():
    # configuration

    print('end')


if __name__ == "__main__":
    searchSTime = '2019-01-01 00:00:00'
    searchETime = '2021-05-13 00:00:00'
    ca = CharCycleAnalysis()
    # proj = 'Passat'
    # vinList = ['LSVCY6C44LN018223']

    # TicToc.tic()
    # meb82List = ca.GetVinListForSpecificProject(ca.ClickhouseTableV2, proj, searchSTime, searchETime)
    # TicToc.toc('get vin info')
    #
    # vinProjectInfo = ca.GetVinListForSpecificProject(ca.ClickhouseTableV2, 'Tiguan', searchSTime, searchETime, 1)
    # vinList = ['LSVCZ6C45KN025919','LSVCY6C44LN018223', 'LSVCZ6C42KN038675', 'LSVCZ6C46KN033222', 'LSVUZ60T1J2218763']
    # vinList = ['LSVCZ6C42KN038675']
    # proj = 'Lavida'
    # # vinList = ['LSVUY60T9L2069718']
    # vinInfo = pd.read_excel(r"D:\WorkSpace\passat\Vinlist.xlsx")
    # vinInfo = pd.read_excel(r"D:\WorkSpace\passat\里程和地点.xlsx", sheet_name='Sheet1', header=None, index_col=None)
    #
    # vinList = vinInfo[0].to_list()
    vinList = ['LSVUZ60T9K2052073']
    charInfoList = []
    # charDepthInfoList = []
    # for idx in range(0, len(vinList)):
    #     vin = vinList[idx]
    #     vinData = ca.GetChardataByVin(vin, searchSTime, searchETime)
    #     if vinData.empty:
    #         continue
    #     charFcycIdxsS, charFcycIdxsE = ca.GetChargeCycIndexByMileage(vinData)
    #     charDepthInfo = ca.GetPureChardepth(vinData, charFcycIdxsS, charFcycIdxsE)
    #     charDepthInfoList.append(charDepthInfo[::])
    # pd.DataFrame(charDepthInfoList).to_excel("D:\\WorkSpace\\tempData\\chardepthinfo.xlsx")
    for idx in range(0, 1):
        vin = vinList[idx]
        print(vin + "START" + str(datetime.datetime.now()))
        TicToc.tic()
        vinData = ca.GetChardataByVin(vin, searchSTime, searchETime)
        TicToc.toc('get vin char data')
        # pd.DataFrame(vinData).to_excel("D:\\WorkSpace\\tempData\\" + vin + "_chardata" +
        #                                str(datetime.datetime.now()).split(' ')[0] + ".xlsx")
        if vinData.empty:
            continue
        TicToc.tic()
        charFcycIdxsS, charFcycIdxsE = ca.GetChargeCycIndexByMileage(vinData)
        TicToc.toc('split char')
        charInfoListTemp, _ = ca.GetChargeCycInfo(vinData, charFcycIdxsS, charFcycIdxsE)
        print(vin + "END" + str(datetime.datetime.now()))
        charInfoList.extend(charInfoListTemp)
    pd.DataFrame(charInfoList).to_excel("D:\\WorkSpace\\tempData\\" + ca.project + "_cycinfo" +
                                        str(datetime.datetime.now()).split(' ')[0] + ".xlsx")
    # print('end')
