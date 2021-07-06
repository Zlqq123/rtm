import numpy as np
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt
from CharCycAnalysis import CharCycleAnalysis

# class LongP(CharCycleAnalysis):
#     def __init__(self):
#         pass


if __name__ == "__main__":
    route = r"D:\WorkSpace\PHEVlongparking"
    files = os.listdir(route)
    lPdf = pd.DataFrame([])
    feats = []
    tp = datetime.datetime.now()
    for f in files:
        fPath = route + '\\' + f
        if os.path.isfile(fPath):
            lPdfTmp = pd.read_csv(fPath, header=None)
            lPdf = pd.concat([lPdf, lPdfTmp], ignore_index=True)
            lPdf = lPdf.drop_duplicates(ignore_index=True)
        dura = np.array(lPdf[2]).astype(np.float) / 3600
        soc = np.array(lPdf[3]).astype(np.float)
        temp = np.array(lPdf[5]).astype(np.float)
        vinList = np.array(lPdf[0])
        uVinList = np.unique(vinList)

        for vin in uVinList:
            featsTmp = []
            vinHint = np.where(vinList.__eq__(vin))
            socTmp = soc[vinHint]
            tempTmp = temp[vinHint]
            duraTmp = dura[vinHint]
            parkT = np.array(vinHint).size
            socMean = np.mean(socTmp[np.where(socTmp > 0)])
            tempMean = np.mean(tempTmp[np.intersect1d(np.array(np.where(214 > tempTmp)).flatten(),
                                                      np.array(np.where(tempTmp > -40)).flatten())])
            duraMean = np.mean(duraTmp)

            tempHPx = np.array(np.intersect1d(np.array(np.where(214 > tempTmp)).flatten(),
                                             np.array(np.where(tempTmp > 42)).flatten())).size / np.array(vinHint).size
            tempHP = min(max(tempHPx, 0.01), 0.99)
            tempHS = -tempHP * np.log2(1 - tempHP) + (1 - tempHP) * np.log2(tempHP)

            socP = np.array(np.where(socTmp == 1)).size / np.array(vinHint).size
            socP = min(max(socP, 0.01), 0.99)
            socS = -socP * np.log2(1 - socP) + (1 - socP) * np.log2(socP)
            duraP = np.array(np.where(duraTmp > 12)).size / np.array(vinHint).size
            duraP = min(max(duraP, 0.01), 0.99)
            duraS = -duraP * np.log2(1 - duraP) + (1 - duraP) * np.log2(duraP)
            tempLPx = np.array(np.where(tempTmp < 8)).size / np.array(vinHint).size
            tempLP = min(max(tempLPx, 0.01), 0.99)
            tempLS = -tempLP * np.log2(1 - tempLP) + (1 - tempLP) * np.log2(tempLP)
            tempPx = np.array(np.intersect1d(np.array(np.where(8 > tempTmp)).flatten(),
                                            np.array(np.where(tempTmp > -40)).flatten())).size / np.array(
                vinHint).size + np.array(np.intersect1d(np.array(np.where(214 > tempTmp)).flatten(),
                                                        np.array(np.where(tempTmp > 42)).flatten())).size / np.array(
                vinHint).size
            tempP = min(max(tempPx, 0.01), 0.99)
            tempS = -tempP * np.log2(1 - tempP) + (1 - tempP) * np.log2(tempP)
            featsTmp.extend([vin, parkT, duraMean, tempMean, socMean, duraP, socP, tempLPx, tempHPx, tempPx, duraS, socS,
                             tempLS, tempHS, tempS])
            feats.append(featsTmp[::])

        # ff[:, 1] = ff[:, 1].astype(np.float) / np.sqrt(
        #     np.dot(ff[:, 1].astype(np.float), ff[:, 1].astype(np.float))) * 100
        # ff[:, 2] = ff[:, 2].astype(np.float) / np.sqrt(
        #     np.dot(ff[:, 2].astype(np.float), ff[:, 2].astype(np.float))) * 100
        # ff[:, 3] = ff[:, 3].astype(np.float) / np.sqrt(
        #     np.dot(ff[:, 3].astype(np.float), ff[:, 3].astype(np.float))) * 100
        # ff[:, 4] = ff[:, 4].astype(np.float) / np.sqrt(
        #     np.dot(ff[:, 4].astype(np.float), ff[:, 4].astype(np.float))) * 100
        pd.DataFrame(feats).to_csv(r"D:\WorkSpace\PHEV_parkfeats_shannon.csv", mode='a', header=None, index=None)

    print((datetime.datetime.now() - tp).seconds)
    print('end')
