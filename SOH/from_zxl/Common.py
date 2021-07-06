from clickhouse_driver import Client
from sklearn.mixture import GaussianMixture
from sklearn.gaussian_process import GaussianProcessRegressor
import matplotlib.pyplot as plt
from scipy.stats import mode
import pandas as pd
import numpy as np
import datetime
from scipy import interpolate


class CommonProcess:
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

        self.ProjInfo = {"lavida60ah": "(startsWith(deviceid, 'LSVAV') AND substring(deviceid,7,2) = '0E')",
                         "lavida53ah": "(startsWith(deviceid, 'LSVAX') AND substring(deviceid,7,2) = '0E') OR "
                                       "(startsWith(deviceid, 'LSVAY') AND substring(deviceid,7,2) = '0E') OR "
                                       "(startsWith(deviceid, 'LSVAZ') AND substring(deviceid,7,2) = '0E')",
                         "tharu60ah": "(startsWith(deviceid, 'LSVUZ') AND substring(deviceid,7,2) = 'B2')",
                         "tiguanC6": "(startsWith(deviceid, 'LSVUX') AND substring(deviceid,7,2) = '0T') OR "
                                     "(startsWith(deviceid, 'LSVUY') AND substring(deviceid,7,2) = '0T')",
                         "tiguanC5": "(startsWith(deviceid, 'LSVUZ') AND substring(deviceid,7,2) = '0T')",
                         "passatC6": "(startsWith(deviceid, 'LSVCY') AND substring(deviceid,7,2) = 'C4')",
                         "passatC5": "(startsWith(deviceid, 'LSVCZ') AND substring(deviceid,7,2) = 'C4')",
                         "NEO2wd55": "(startsWith(deviceid, 'LSVFA') AND substring(deviceid,7,2) = 'E9')",
                         "ASUVe2wd55": "(startsWith(deviceid, 'LSVUA') AND substring(deviceid,7,2) = 'E4')",
                         "ASUVe2wd82": "(startsWith(deviceid, 'LSVUB') AND substring(deviceid,7,2) = 'E4')",
                         "ASUVe4wd82": "(startsWith(deviceid, 'LSVUC') AND substring(deviceid,7,2) = 'E4')",
                         "LoungeSUVe2wd62": "(startsWith(deviceid, 'LSVUA') AND substring(deviceid,7,2) = 'E5')",
                         "LoungeSUVe2wd82": "(startsWith(deviceid, 'LSVUB') AND substring(deviceid,7,2) = 'E5') OR "
                                            "(startsWith(deviceid, 'LSV2B') AND substring(deviceid,7,2) = 'E5')",
                         "LoungeSUVe4wd82": "(startsWith(deviceid, 'LSVUC') AND substring(deviceid,7,2) = 'E5')",
                         "AudiAplusSUVe2wd62": "(startsWith(deviceid, 'LSVUA') AND substring(deviceid,7,2) = 'G4')",
                         "AudiAplusSUVe2wd82": "(startsWith(deviceid, 'LSVUB') AND substring(deviceid,7,2) = 'G4')",
                         "AudiAplusSUVe4wd82": "(startsWith(deviceid, 'LSVUC') AND substring(deviceid,7,2) = 'G4')"}

        self.Project = ''  # project, e.g. 'Tiguan'
        self.vin = ''  # VIN

        # parameters for charging cycle analysis(part of which are set afterwards)
        self.Q = 0
        self.charDiscDuraPar = 10 * 60  # maximum durable time discontinued duration in seconds
        self.sampContiDuraPar = 28  # sample data continuous duration in seconds
        self.sampContiDuraThrPar = 2  # maximum threshold in seconds for possible continuous sample duration delay
        self.staticFrmNumPar = 1  # minimum amount of frames for steady status judgement
        self.staticDiscDuraPar = 5 * 60  # minimum ignition off duration in seconds for gaining one steady candidate
        self.staticCurrPar = 2  # current threshold for steady candidate
        self.compenCurrPar = 5  # current threshold for depolar compensate
        self.staticVolStdPar = 0.002  # voltage fluctuation standard value threshold for steady candidate
        self.socDbRes = 1  # resolution of SOC value on dashboard
        self.staticCompenDuraPar = 30 * 60  # maximum threshold in seconds for estimating resistance after long parking
        self.ACDCCurrThr = 20  # AC charging current threshold
        self.CharCurrLimTempThr = 50  # temperature threshold caused DC/AC charging fuzzy zone
        # TODO: more parameters

        # module split edge of cell(set afterwards)
        self.ModuEdge = np.array([])
        self.PrbEdge = np.array([])
        self.cellNum = 0  # number of cells in the pack
        self.probeNum = 0  # number of probes in the pack

        # OCV-SOC look-up table for different projects under different temperatures(set afterwards)
        self.OCVols = np.array([])
        self.Temp = np.array([])
        self.OCSocs = np.array([])

        # container
        self.VinInfoForProjectDf = []  # VIN list Info for specific project

    # TODO: filter invalid SOC
    def SOCFilter(self):
        pass

    # TODO: combine methods
    def User2BMSSoc(self, dBSocDf):
        """
        user soc 2 bms soc
        :param dBSocDf:
        :return BMSSOC:
        """
        project = self.Project
        if type(dBSocDf) == pd.Series:
            dBSocDf = dBSocDf.astype(np.float)
            dBSocDf[dBSocDf < 0] = 0
            dBSocDf[dBSocDf > 100] = 100
        else:
            dBSocDf = min(max(float(dBSocDf), 0), 100)
        if project.__contains__('Tiguan') or project.__contains__('Passat'):
            BMSSOC = 24 + (dBSocDf - 1.25) / (100.2 - 1.25) * (95 - 24)
        elif self.Project.startswith('ASUVe') and self.Project.endswith('82'):
            finterp = interpolate.interp1d(np.array(range(100, -1, -10)),
                                           np.array([96, 86.2, 77.3, 68.4, 59.4, 50, 41.6, 32.5, 25.6, 14.5, 4.5]),
                                           kind='linear')
            BMSSOC = finterp(dBSocDf).flatten()
        elif self.Project.__eq__('lavida60ah'):
            BMSSOC = 4 + (dBSocDf - 1.25) / (100.2 - 1.25) * (96 - 4)
        elif self.Project.__eq__('lavida53ah'):
            BMSSOC = 6 + (dBSocDf - 1.25) / (100.2 - 1.25) * (96 - 6)
        else:
            BMSSOC = np.array([np.nan])
        if type(dBSocDf) == pd.Series:
            return BMSSOC
        else:
            return BMSSOC[0]

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

    def UpckDataFromStrDf(self, dataDf, interIdx, expcNum, valH, valL):
        """
        Unpack string with comma

        :param dataDf: dataframe with a column of string vector needs to be split by comma
        :param interIdx: String Vector column index
        :param expcNum: expected number of values in string
        :param valH: upper limit of value
        :param valL: lower limit of value
        :return
        """

        # valid voltage range: 2.5-4.2v
        # valid temperature range: -40-85℃

        if dataDf.__len__() == 0:
            return pd.DataFrame([]), pd.Series(pd.Series(dtype=bool))
        else:
            DataDf = dataDf.reset_index(drop=True)
            Data = dataDf[interIdx]
            if type(Data) == str:
                Data = pd.Series([Data])
        avaIdxsSeri = pd.Series(dtype=bool)
        upckDf = pd.DataFrame([])
        for frm in Data:
            try:
                FrmTemp = pd.DataFrame(frm.split(',')).T.astype(np.float)
            except ValueError:
                avaIdxsSeri = avaIdxsSeri.append(pd.Series([False]), ignore_index=True)
                continue
            if FrmTemp[(FrmTemp < valH) & (FrmTemp > valL)].dropna(axis=1).shape[1] == expcNum:
                upckDf = upckDf.append(FrmTemp, ignore_index=True)
                avaIdxsSeri = avaIdxsSeri.append(pd.Series([True]), ignore_index=True)
            else:
                upckDf = upckDf.append(pd.DataFrame([np.nan] * expcNum), ignore_index=True)
                avaIdxsSeri = avaIdxsSeri.append(pd.Series([False]), ignore_index=True)
        return upckDf, avaIdxsSeri

    def GetSocFromOCV(self, volsArr, TsArr):
        """
        get soc values based on OCV-SOC

        1D interpolation is adopted currently

        :param volsArr: numpy array of voltages
        :param TsArr: numpy array of temperature
        :return: socs: numpy array of corresponding socs

        Attention: temperature over 40 or lower than -25 would be set to nearest value
        """
        # TODO: calibrate np.vstack in configuration
        caliTemp = self.Temp
        caliSoc = self.OCSocs
        xTemp, zSoc = np.meshgrid(caliTemp, caliSoc)
        yVol = self.OCVols
        socsArr = interpolate.griddata(np.vstack((xTemp.flatten(), yVol.T.flatten())).T, zSoc.flatten(),
                                       (TsArr, volsArr), method='linear')
        return socsArr

    # TODO: combine methods
    def GetPackSoc(self, socsArr):
        """
        calculate pack SOC
        :param socsArr:
        :return: round(packsoc, 2)
        """
        if socsArr.size // self.cellNum == 0:
            packSoc = np.nan
        elif socsArr.size // self.cellNum == 1:
            rMin = 30
            if self.Project.__eq__('Tiguan') or self.Project.__eq__('Passat'):
                rMax = 85
            else:
                rMax = 90
            if np.min(socsArr) <= rMin:
                packSoc = np.min(socsArr)
            elif np.min(socsArr) > rMin and np.max(socsArr) >= rMax:
                packSoc = np.max(socsArr)
            else:
                packSoc = round(rMin + (np.min(socsArr) - rMin) * (rMax - rMin) /
                                ((rMax - rMin) - (np.max(socsArr) - np.min(socsArr))), 2)
        else:
            minSocs = np.min(socsArr, axis=1)
            maxSocs = np.max(socsArr, axis=1)
            rMin = 30
            if self.Project.__eq__('Tiguan') or self.Project.__eq__('Passat'):
                rMax = 85
            else:
                rMax = 90
            minHint = (minSocs < rMin).flatten()
            nMinHint = (minSocs >= rMin).flatten()
            maxHint = ((maxSocs >= rMax) & nMinHint).flatten()
            midHint = ((maxSocs < rMax) & nMinHint).flatten()

            packSoc = (np.ones([socsArr.shape[0], 1]) * np.nan).flatten()
            packSoc[minHint] = minSocs[minHint]
            packSoc[maxHint] = maxSocs[maxHint]
            packSoc[midHint] = rMin + (minSocs[midHint] - rMin) * (rMax - rMin) / ((rMax - rMin) - (maxSocs[midHint]
                                                                                                    - minSocs[midHint]))
            packSoc = packSoc.round(2)
        return packSoc

    def GetAveMaxMinT(self, pcsTDf):
        """
        unpack temperature data from an string array of temperatures, and get its average, max, min value
        explore the invalid value of Temperatures

        :param pcsTDf: piece of data in numpy array with all of the fields
        :return TMean: average temperature
        """
        if pcsTDf.__len__() > 1:
            TMean = pcsTDf.mean().mean()
            TMax = pcsTDf.max().max()
            TMin = pcsTDf.min().min()
            TStd = pcsTDf.std().std()
        elif pcsTDf.__len__() == 1:
            TMean = pcsTDf.mean()
            TMax = pcsTDf.max()
            TMin = pcsTDf.min()
            TStd = pcsTDf.std()
        else:
            # Set default as infinity
            TMean = np.nan
            TMax = np.nan
            TMin = np.nan
            TStd = np.nan
        return TMean, TMax, TMin, TStd

    def GetCellTandPackT(self, pcsTDf):
        """
        unpack temperature data from an string array of temperatures, and get cell temperatures and pack temperature
        :param pcsTDf: piece of data in dataframe with all of the fields
        :return cellTArr: cell temperatures for OCV-SOC

        # TODO: pack temperature calculation
        """

        if pcsTDf.__len__() > 0:
            # set upper and lower limit of temperature for OCV-SOC
            pcsTArr = np.array(pcsTDf)
            pcsTArr[pcsTArr > np.max(self.Temp)] = np.max(self.Temp)
            pcsTArr[pcsTArr < np.min(self.Temp)] = np.min(self.Temp)

            prbInd = 0
            cellTArr = pcsTArr[:, prbInd].repeat(self.PrbEdge[prbInd]).reshape(pcsTDf.__len__(),
                                                                               self.PrbEdge[prbInd])
            for prbInd in range(1, self.probeNum):
                cellTArr = np.hstack((cellTArr, pcsTArr[:, prbInd].repeat(self.PrbEdge[prbInd])
                                      .reshape(pcsTDf.__len__(), self.PrbEdge[prbInd])))

        else:
            cellTArr = np.array([])

        return cellTArr

    def GetOhmR(self, dataDf, valH=4.2, valL=2.5):
        """
        calculate resistance by delta v/delta I
        :param dataDf:
        :param IIdx:
        :param volIdx:
        :param valH:
        :param valL:
        :return: calculated resistance (OhmR + (1-e**(-t/RC))*PR)
        """
        if dataDf.__len__() < 2:
            return np.array([]), np.array([]), np.array([])
        else:
            dataDf = dataDf.reset_index(drop=True)
            volsDf, avaHintV = self.UpckDataFromStrDf(dataDf, self.CellVolIdx, self.cellNum, valH, valL)
            dateDf = dataDf[self.UtIdx]
            duraSerR = (pd.to_datetime(dateDf) - pd.to_datetime(dateDf).shift(1)).dt.seconds
            avaHinttR = duraSerR < self.sampContiDuraPar + self.sampContiDuraThrPar
            duraSerF = (pd.to_datetime(dateDf).shift(-1) - pd.to_datetime(dateDf)).dt.seconds
            avaHinttF = duraSerF < self.sampContiDuraPar + self.sampContiDuraThrPar
            avaHintR = np.logical_and(np.logical_and(avaHintV.shift(1), avaHintV),
                                      avaHinttR).astype(bool)
            avaHintF = np.logical_and(np.logical_and(avaHintV.shift(-1),
                                                     avaHintV), avaHinttF).astype(bool)
            IDf = dataDf[self.CurrIdx].astype(np.float)
            IF = np.array(IDf[avaHintF])
            IR = np.array(IDf[avaHintR])

            dIArr = -(IR - IF)
            dVArr = np.array(volsDf[avaHintR[avaHintV]].reset_index(drop=True) - volsDf[avaHintF[avaHintV]]
                             .reset_index(drop=True))
            RArr = (dVArr[abs(dIArr) > 5].T / dIArr[abs(dIArr) > 5]).T
            dBSocDf = dataDf[self.DbSocIdx].astype(np.float)
            dBSocArr = np.array(dBSocDf[avaHintR][abs(dIArr) > 5])
            tempDf, avaHintT = self.UpckDataFromStrDf(dataDf[avaHintR][abs(dIArr) > 5], self.PrbTempIdx,
                                                      self.probeNum, 85, -40)
            cellTArr = self.GetCellTandPackT(tempDf)
            return RArr, IF[abs(dIArr) > 5], IR[abs(dIArr) > 5], dBSocArr, cellTArr

    def GetStdVol(self, DataDf, valH=4.2, valL=2.5):
        """
        get voltage value unpacked and get standard voltage value

        :param valL:
        :param valH:
        :param DataDf: piece of data in numpy array with all of the fields, frames with time gap within 30s is expected
        :param IIdx: current index
        :param volIdx: voltage index
        :return statPPcsVolDataTemp: numpy float array of voltage
        :return volStd: standard value of voltage
        :return IMax: maximum current value among the frames
        """
        DataDf = DataDf.reset_index(drop=True)
        pcsVolsDf, avaHint = self.UpckDataFromStrDf(DataDf, self.CellVolIdx, self.cellNum, valH, valL)
        if pcsVolsDf[avaHint].__len__() == 0:
            return np.array([]), np.array([]), np.nan
        IDf = DataDf[self.CurrIdx][:].astype(np.float)
        IMax = abs(IDf).max()
        date = DataDf[self.UtIdx]
        dura = (pd.to_datetime(date[avaHint].iloc[-1]) - pd.to_datetime(date[avaHint].iloc[0])).seconds

        # TODO: proper time gap is required
        if (pcsVolsDf[avaHint].__len__() > 1 and (self.sampContiDuraPar - self.sampContiDuraThrPar) < dura
                and IMax < self.staticCurrPar):
            volStdDf = pcsVolsDf.std(axis=0)
        else:
            volStdDf = pd.DataFrame([])
        return pcsVolsDf, volStdDf, IMax

    def GetVinListForSpecificProject(self, clickhouseTable, project, searchStartTime, searchEndTime, limitConf=None):
        """
        get vin info of specific project in specific time range, ordered by "accmiles" field(mileage)

        :param clickhouseTable:
        :param project:
        :param searchStartTime:
        :param searchEndTime:
        :param limitConf: set for limit the amount of cars returned, if no limit is desired, use [] instead
        :return VinInfoForProject: list with 4 rows of vin list, latest uploadtime list, earliest uploadtime list and
                                   latest accmile list
        """

        preReq = self.ProjInfo.get(project)
        self.Project = project
        self.BatteryCalibrate()
        if type(preReq) == str:
            sql = ("SELECT " +
                   "deviceid,maxut,minut,accmiles " +
                   "FROM " +
                   "(SELECT " +
                   "deviceid,uploadtime AS maxut,accmiles FROM " +
                   clickhouseTable +
                   " WHERE " + preReq + ") " +

                   "INNER JOIN " +

                   "(SELECT " +
                   "deviceid,max(uploadtime) AS maxut,min(uploadtime) AS minut FROM " +
                   clickhouseTable +
                   " WHERE uploadtime < '" + searchEndTime + "' AND uploadtime >= '" + searchStartTime + "' AND toFloat32OrZero(accmiles) < 999999" +
                   " GROUP BY deviceid HAVING " + preReq + ")" +
                   " USING deviceid,maxut" +
                   " ORDER BY toFloat32OrZero(accmiles) DESC")

            if type(limitConf) == int:
                sql += " LIMIT " + "%s" % limitConf
            vinInfoForProjectTemp = self.client.execute(sql)
            self.VinInfoForProjectDf = pd.DataFrame(vinInfoForProjectTemp)
        return self.VinInfoForProjectDf

    def GetProjectParamByVin(self, vinStr):
        """
        Get project of specific vin
        :param vinStr:
        :return project: project of vin
        """
        self.Project = ''
        if vinStr.startswith('LSVAV') and vinStr[6:8].__eq__('0E'):
            self.Project = 'lavida60ah'
        elif ((vinStr.startswith('LSVAX') and vinStr[6:8].__eq__('0E')) or
              (vinStr.startswith('LSVAY') and vinStr[6:8].__eq__('0E')) or
              (vinStr.startswith('LSVAZ') and vinStr[6:8].__eq__('0E'))):
            self.Project = 'lavida53ah'
        elif vinStr.startswith('LSVUZ') and vinStr[6:8].__eq__('B2'):
            self.Project = 'tharu60ah'
        elif ((vinStr.startswith('LSVUX') and vinStr[6:8].__eq__('0T')) or
              (vinStr.startswith('LSVUY') and vinStr[6:8].__eq__('0T'))):
            self.Project = 'tiguanC6'
        elif vinStr.startswith('LSVUZ') and vinStr[6:8].__eq__('0T'):
            self.Project = 'tiguanC5'
        elif vinStr.startswith('LSVCY') and vinStr[6:8].__eq__('C4'):
            self.Project = 'passatC6'
        elif vinStr.startswith('LSVCZ') and vinStr[6:8].__eq__('C4'):
            self.Project = 'passatC5'
        elif vinStr.startswith('LSVFA') and vinStr[6:8].__eq__('E9'):
            self.Project = 'NEO2wd55'
        elif vinStr.startswith('LSVUA') and vinStr[6:8].__eq__('E4'):
            self.Project = 'ASUVe2wd55'
        elif vinStr.startswith('LSVUB') and vinStr[6:8].__eq__('E4'):
            self.Project = 'ASUVe2wd82'
        elif vinStr.startswith('LSVUC') and vinStr[6:8].__eq__('E4'):
            self.Project = 'ASUVe4wd82'
        elif vinStr.startswith('LSVUA') and vinStr[6:8].__eq__('E5'):
            self.Project = 'LoungeSUVe2wd62'
        elif ((vinStr.startswith('LSVUB') and vinStr[6:8].__eq__('E5')) or
              (vinStr.startswith('LSV2B') and vinStr[6:8].__eq__('E5'))):
            self.Project = 'LoungeSUVe2wd82'
        elif vinStr.startswith('LSVUC') and vinStr[6:8].__eq__('E5'):
            self.Project = 'LoungeSUVe4wd82'
        elif vinStr.startswith('LSVUA') and vinStr[6:8].__eq__('G4'):
            self.Project = 'AudiAplusSUVe2wd62'
        elif vinStr.startswith('LSVUB') and vinStr[6:8].__eq__('G4'):
            self.Project = 'AudiAplusSUVe2wd82'
        elif vinStr.startswith('LSVUC') and vinStr[6:8].__eq__('G4'):
            self.Project = 'AudiAplusSUVe4wd82'
        else:
            self.Project = 'unknown project'
        return self.Project

    def BatteryCalibrate(self):
        if self.Project.__contains__('Tiguan') or self.Project.__contains__('Passat'):
            self.Q = 37
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
        elif self.Project.__eq__('ASUVe2wd82') or self.Project.__eq__('ASUVe4wd82'):
            self.Q = 234
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
        elif self.Project.__eq__('lavida53ah'):
            self.cellNum = 96
            self.probeNum = 32
            self.Q = 106
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

        elif self.Project.__eq__('ASUVe2wd55'):
            self.cellNum = 96
            self.probeNum = 16

    def GetOcVolAndOcSoc(self, dataDf):
        """
        return soc with known temperature and open circuit voltages of each cell
        :param dataDf:
        :return:ocVols, ocSocs
        """
        prbTDf, avaHintT = self.UpckDataFromStrDf(dataDf, self.PrbTempIdx, self.probeNum, 85, -40)
        cellTArr = self.GetCellTandPackT(prbTDf[avaHintT])
        ocVolsDf, avaHintV = self.UpckDataFromStrDf(dataDf, self.CellVolIdx, self.cellNum, 4.2, 2.5)
        ocVolsArr = np.array(ocVolsDf[avaHintT[avaHintV]])
        cellTArr = cellTArr[avaHintV[avaHintT]]
        try:
            ocSocs = self.GetSocFromOCV(ocVolsArr, cellTArr)
        except ValueError:
            ocSocs = np.array([])
        return ocVolsArr, cellTArr, ocSocs

    def GetStatInfo(self, dataDf, dbSocLim, dire=-1):
        """
        steady status judgement
        :param dataDf:
        :param dbSocLim:
        :param dire:
        :return statOcVols, statOcSocs, statErrAh, statFlg, statDate, statTStr, statLPDura,
                for end of charging:
                    {compenEFlg, str(compenEDate), '[' + compenETStr.replace(',', ';') + ']', CompenELPDura} :
        """

        def GetErrorAh(dataDfTmp, idxSTmp, direTmp, iTmp):
            """
            calculate possible error ampere hour involved between the beginning of charging and the steady moment
            :param dataDfTmp:
            :param idxSTmp:
            :param direTmp:
            :param iTmp:
            :return:
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
        statOcTs = np.array([])
        statOcSocs = np.array([])
        statErrAh = np.nan
        compenEFlg = ''
        compenEDate = ''
        compenETStr = ''
        CompenELPDura = np.nan
        statFlg = ''
        statDate = ''
        statLPDura = np.nan
        statTStr = ''

        if dire == -1:
            idxS = len(dataDf) - 1
            idxE = -1
        else:
            dire = 1
            idxS = 0
            idxE = len(dataDf)

        for i in range(idxS, idxE, dire):
            if (abs(dataDf.iloc[i, self.DbSocIdx] - dbSocLim) < self.socDbRes
                    or (abs(dataDf.iloc[i, self.DbSocIdx] - dbSocLim) <= self.socDbRes)
                    and max(dataDf.iloc[i, self.DbSocIdx], dbSocLim) == 100):
                if (i != 0 and abs(
                        dataDf.iloc[i, self.DbSocIdx] - dataDf.iloc[i - 1, self.DbSocIdx]) < self.socDbRes and
                        (dataDf.iloc[i, self.UtIdx] - dataDf.iloc[i - 1, self.UtIdx]).seconds > self.staticDiscDuraPar):
                    if dire == 1 and compenEFlg != 'LP':
                        compenEFlg = 'LP'
                        compenEDate = dataDf.iloc[i, self.UtIdx]
                        compenETStr = dataDf.iloc[i, self.PrbTempIdx]
                        CompenELPDura = (dataDf.iloc[i, self.UtIdx] - dataDf.iloc[i - 1, self.UtIdx]).seconds / 3600
                    if (abs(dataDf.iloc[i, self.CurrIdx]) < self.staticCurrPar
                            and 0 < float(dataDf.iloc[i, self.MileIdx]) < 999999):
                        statOcVols, statOcTs, statOcSocs = self.GetOcVolAndOcSoc(dataDf.iloc[i, :])
                        statErrAh = GetErrorAh(dataDf, idxS, dire, i)
                        statFlg = 'LP'
                        statDate = dataDf.iloc[i, self.UtIdx]
                        statTStr = dataDf.iloc[i, self.PrbTempIdx]
                        statLPDura = (dataDf.iloc[i, self.UtIdx] - dataDf.iloc[i - 1, self.UtIdx]).seconds / 3600
                        break

                ucharPcsDate = pd.to_datetime(dataDf[self.UtIdx])
                ucharPcsDateThr = (pd.to_datetime(dataDf.iloc[i, self.UtIdx]) + dire *
                                   datetime.timedelta(0, (self.sampContiDuraPar + self.sampContiDuraThrPar)
                                                      * self.staticFrmNumPar, 0))
                try:
                    if dire == 1:
                        ucharPcsIdx = list((ucharPcsDate - ucharPcsDateThr) > datetime.timedelta(0, 0, 0)).index(True)
                    else:
                        ucharPcsIdx = list((ucharPcsDate - ucharPcsDateThr) > datetime.timedelta(0, 0, 0)).index(
                            True) - 1

                except ValueError:
                    ucharPcsIdx = idxS - dire

                cellVolTemp, volStd, currMax = self.GetStdVol(dataDf.iloc[range(i, ucharPcsIdx, dire), :])
                if (not volStd.size == 0) and (0 < np.max(volStd) < self.staticVolStdPar):
                    if currMax < self.staticCurrPar and statOcSocs.size == 0:
                        statOcVols, statOcTs, statOcSocs = self.GetOcVolAndOcSoc(dataDf.iloc[max(ucharPcsIdx + dire, i),
                                                                                 :])
                        statErrAh = GetErrorAh(dataDf, idxS, dire, i)
                        statFlg = 'Normal'
                        statDate = dataDf.iloc[i, self.UtIdx]
                        statTStr = dataDf.iloc[i, self.PrbTempIdx]
                        break

            else:
                break
        if dire == -1:
            return statOcVols, statOcTs, statOcSocs, statErrAh, statFlg, statDate, statTStr, statLPDura
        else:
            return statOcVols, statOcTs, statOcSocs, statErrAh, statFlg, statDate, statTStr, statLPDura, \
                   compenEFlg, str(compenEDate), '[' + compenETStr.replace(',', ';') + ']', CompenELPDura

    def GetRC(self, charDataDf):
        cellPRArr = np.array([])
        cellOhmArr = np.array([])
        cellDvArr = np.array([])
        cellTArr = np.array([])
        depolarVolSArr = np.array([])
        depolarSocSArr = np.array([])
        charDataDf.reset_index(drop=True)
        try:
            deltat = (pd.to_datetime(charDataDf.iloc[1:, self.UtIdx])
                      - pd.to_datetime(charDataDf.iloc[1:, self.UtIdx].shift(1))).dt.seconds
            if ((deltat[1:] >= self.sampContiDuraPar - self.sampContiDuraThrPar).all() and
                    (deltat[1:] <= self.sampContiDuraPar + self.sampContiDuraThrPar).all()):
                currs = np.array(charDataDf[self.CurrIdx])
                cellVols, avahintV = self.UpckDataFromStrDf(charDataDf, self.CellVolIdx, self.cellNum, 4.2, 2.5)
                cellVols = np.array(cellVols)
                if currs[1:].std() < 0.5 and sum(avahintV) == 6:
                    cellVols0 = np.mean(cellVols[1:4, :], axis=0)
                    cellVols1 = np.mean(cellVols[2:5, :], axis=0)
                    cellVols2 = np.mean(cellVols[3:6, :], axis=0)
                    if ((cellVols1 - cellVols0 > 0).all() and
                            ((cellVols2 - cellVols1) / (cellVols1 - cellVols0) < 0.99).all() and
                            ((cellVols2 - cellVols1) / (cellVols1 - cellVols0) > 0.01).all()):
                        cellRcEq = np.power((cellVols2 - cellVols1) / (cellVols1 - cellVols0)
                                            , 1 / (deltat[1:].mean() / 0.1))
                        cellRc = cellRcEq * 0.1 / (1 - cellRcEq)
                        cellOhmPrR2 = -(cellVols2 - cellVols[0, :]) / (currs[3:6].mean() - currs[0])
                        cellOhmPrR1 = -(cellVols0 - cellVols[0, :]) / (currs[1:4].mean() - currs[0])
                        cellPRArr = (cellOhmPrR2 - cellOhmPrR1) / (
                                - np.e ** (-deltat[1:].mean() * 3.5 / cellRc) + np.e ** (-deltat[1:].mean() * 1.5 / cellRc))
                        cellOhmArr = cellOhmPrR2 - (1 - np.e ** (-deltat[1:].mean() * 3.5 / cellRc)) * cellPRArr
                        cellOhmPR = cellPRArr + cellOhmArr
                        cellDrVIEq = (cellOhmPR * 0.1 * currs[1:].mean()) / (cellRc + 0.1)
                        cellDvArr = ((-(cellVols1 - cellVols0) -
                                   (np.power(cellRcEq, deltat[1:].mean() / 0.1) - 1) / (cellRcEq - 1) * cellDrVIEq) /
                                  (np.power(cellRcEq, np.mean(deltat[1:]) / 0.1) - 1))
                        depolarVolSArr = cellVols0 + cellDvArr
                        prbT, avahintT = self.UpckDataFromStrDf(charDataDf, self.PrbTempIdx, self.probeNum, 85, -40)
                        cellTArr = self.GetCellTandPackT(prbT[avahintT]).mean(axis=0)
                        depolarSocSArr = self.GetSocFromOCV(depolarVolSArr, cellTArr)
        except ValueError or IndexError:
            pass
        return cellPRArr, cellOhmArr, cellDvArr, cellTArr, depolarVolSArr, depolarSocSArr

    def RemoveAbnVal(self, dataArr):
        # percentile
        pass


if __name__ == "__main__":
    co = CommonProcess()
    searchStartTimeV1 = '2020-01-01 00:00:00'
    searchEndTimeV1 = '2021-06-18 00:00:00'
    vin = 'LSVAY60E2K2010108'
    co.GetProjectParamByVin(vin)
    co.BatteryCalibrate()
    sql = "SELECT DISTINCT(*) FROM (" \
          + "(SELECT " + co.InterestedFields \
          + " FROM " + co.ClickhouseTableV2 \
          + " WHERE deviceid = '" + vin + "' AND chargingstatus LIKE 'CHARGING_STOPPED%' AND uploadtime >= '" + searchStartTimeV1 + "' AND uploadtime <= '" + searchEndTimeV1 + "')" \
          + " UNION ALL " \
          + "(SELECT " + co.InterestedFields + " FROM " \
          + "(SELECT accmiles FROM " + co.ClickhouseTableV2 \
          + " WHERE deviceid = '" + vin + "' AND chargingstatus LIKE 'CHARGING_STOPPED%' AND uploadtime >= '" + searchStartTimeV1 + "' AND uploadtime <= '" + searchEndTimeV1 + "'" \
          + " GROUP BY accmiles) " \
          + "INNER JOIN " \
          + "(SELECT " + co.InterestedFields + " FROM " \
          + co.ClickhouseTableV2 \
          + " WHERE deviceid = '" + vin + "' AND uploadtime >= '" + searchStartTimeV1 + "' AND uploadtime <= '" + searchEndTimeV1 + "')" \
          + " USING accmiles)" \
          + ") ORDER BY uploadtime"
    vinDf = pd.DataFrame(co.client.execute(sql))
    prbT, avahintT = co.UpckDataFromStrDf(vinDf[:][652:654], co.PrbTempIdx, co.probeNum, 85, -40)
    cellV, avahintV = co.UpckDataFromStrDf(vinDf[:][652:654], co.CellVolIdx, co.cellNum, 4.2, 2.5)
    cellT = co.GetCellTandPackT(prbT)
    co.GetOhmR(vinDf[:][652:656])
    co.GetStdVol(vinDf[:][3:5])
    co.GetRC(vinDf.iloc[6:12, :])
    print(1)
