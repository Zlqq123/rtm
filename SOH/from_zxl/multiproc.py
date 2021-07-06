import datetime
import getopt
import multiprocessing
import sys
import pandas as pd
import os

from CharCycAnalysis import CharCycleAnalysis
from ParamAnalysis import ParamAnalysis


class multiProc(ParamAnalysis):
    def __init__(self):
        super(multiProc, self).__init__()

    def multiAnalysis(self, vL, l, proj, sDate, eDate, ofile, pNo, pNum, sVinNo, lenVin):
        # try:
        searchSTime = sDate
        searchETime = eDate

        charInfoList = []
        count = 0
        for idx in range(sVinNo + pNo, sVinNo + lenVin, pNum):
            vin = vL[idx]
            print(str(pNo) + ': ' + str(count/(lenVin/pNum)*100) + "%")
            print(str(pNo) + ' ' + vin + " START " + str(datetime.datetime.now()))

            vinData = self.GetChardataByVin(vin, searchSTime, searchETime)
            if vinData.empty:
                continue
            charFcycIdxsS, charFcycIdxsE = self.GetChargeCycIndexByMileage(vinData)
            charInfoListTemp, _ = self.GetChargeCycInfo(vinData, charFcycIdxsS, charFcycIdxsE)
            print(str(pNo) + ': ' + str(count/(lenVin/pNum)*100) + "%")
            print(str(pNo) + ' ' + vin + " END " + str(datetime.datetime.now()))
            charInfoList.extend(charInfoListTemp)
            count += 1
            if round(count % 20) == 0:
                # l.acquire()
                pd.DataFrame(charInfoList).to_csv(ofile + "_" + str(pNo) + ".csv", mode='a', header=None, index=None)
                # l.release()
                charInfoList.clear()
        # l.acquire()
        pd.DataFrame(charInfoList).to_csv(ofile + "_" + str(pNo) + ".csv", mode='a', header=None, index=None)
            # l.release()
        # except:
        #     print("！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！error! processid: " + str(pNo) + " vinNo: " + str(idx))
        # finally:
        #     try:
        #         print("！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！end! processid: " + str(pNo) + " vinNo: " + str(idx))
        #         pass
        #     except ValueError:
        #         pass

    def multiAnalysisParm(self, vL, l, proj, sDate, eDate, ofile, pNo, pNum, sVinNo, lenVin):
        try:
            searchSTime = sDate
            searchETime = eDate

            longPInfo = pd.DataFrame([])
            count = 0

            for idx in range(sVinNo + pNo, sVinNo + lenVin, pNum):
                vin = vL[idx]
                print(str(pNo) + ': ' + str(count/(lenVin/pNum)*100) + "%")
                print(str(pNo) + ' ' + vin + " START " + str(datetime.datetime.now()))

                statData, dymData, vinData = self.GetVinData(vin, searchSTime, searchETime)
                if vinData.empty:
                    continue
                # vinData.to_excel(r"D:\WorkSpace\passat\ " + vin + r"_all.xlsx")
                longParkingInfoTmp = self.LongParking(vinData)
                longPInfo = longPInfo.append(longParkingInfoTmp.copy())
                print(str(pNo) + ' ' + vin + " END " + str(datetime.datetime.now()))

                count += 1
                if round(count % 20) == 0:
                    # l.acquire()
                    longPInfo.to_csv(ofile + "_" + str(pNo) + ".csv", mode='a', header=None, index=None, sep=',')
                    longPInfo = pd.DataFrame([])
                    # l.release()
            # l.acquire()
            longPInfo.to_csv(ofile + "_" + str(pNo) + ".csv", mode='a', header=None, index=None, sep=',')
            # l.release()
        except:
            print("！！！！！！！！！！！！！！！！！！！！！！！！！！！error! processid: " + str(pNo) + " vinNo: " + str(idx))
        finally:
            longPInfo.to_csv(ofile + "_" + str(pNo) + ".csv", mode='a', header=None, index=None, sep=',')
            try:
                print("！！！！！！！！！！！！！！！！！！！！！！！！！end! processid: " + str(pNo) + " vinNo: " + str(idx))
                pass
            except ValueError:
                pass


if __name__ == "__main__":
    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'ho:', ["sDate=", "eDate=", "pNum=", "proj=", "sVinNo=", "lenVin="])
    except getopt.GetoptError:
        print()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("multiprocess.py -i <inputfile> -o <outputfile> sDate='startDate' eDate='endDate' pNum=numOfProcess " 
                  "proj='project'")
            sys.exit()
        elif opt == "-i":
            inputfile = arg
        elif opt == "-o":
            outputfile = arg
        elif opt == "--sDate":
            searchSDate = arg
        elif opt == '--eDate':
            searchEDate = arg
        elif opt == '--pNum':
            pNum = int(arg)
        elif opt == '--proj':
            proj = arg
        elif opt == '--sVinNo':
            sVinNo = int(arg)
        elif opt == '--lenVin':
            lenVin = int(arg)

    if proj == 'MEB82':
        vinInfo = pd.read_excel(r"D:\WorkSpace\MEB82\MEB82Vinlist.xlsx")
    elif proj == 'passat':
        vinInfo = pd.read_excel(r"D:\WorkSpace\passat\Vinlist.xlsx")
    elif proj == "lavida":
        vinInfo = pd.read_excel(r"D:\WorkSpace\lavida\Vinlist.xlsx")
    vinList = vinInfo[0].to_list()
    mp = multiProc()
    lock = multiprocessing.Lock()
    pList = []
    for pI in range(0, pNum):
        pList.append(multiprocessing.Process(target=mp.multiAnalysis, args=(vinList[::], lock, proj, searchSDate,
                                                                            searchEDate, outputfile, pI, pNum, sVinNo,
                                                                            lenVin, )))

    for p in pList:
        p.start()

    for p in pList:
        p.join()

