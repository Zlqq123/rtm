import datetime
import re
import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator
from itertools import groupby

if __name__ == '__main__':
    month_season_dict = {
        "central_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring",
            "04": "autumn",
            "05": "summer_autumn",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "summer_autumn",
            "10": "autumn",
            "11": "spring",
            "12": "winter"
        },
        "south_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring",
            "04": "autumn",
            "05": "summer",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "summer",
            "10": "autumn",
            "11": "spring",
            "12": "winter"
        },
        "east_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring",
            "04": "autumn",
            "05": "autumn",
            "06": "summer_autumn",
            "07": "summer",
            "08": "summer",
            "09": "summer_autumn",
            "10": "autumn",
            "11": "spring",
            "12": "winter"
        },
        "north_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring_winter",
            "04": "spring",
            "05": "autumn",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "autumn",
            "10": "spring",
            "11": "spring_winter",
            "12": "winter"
        },
        "northeast_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring_winter",
            "04": "spring",
            "05": "autumn",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "autumn",
            "10": "spring",
            "11": "spring_winter",
            "12": "winter"
        },
        "southwest_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring",
            "04": "autumn",
            "05": "summer_autumn",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "summer_autumn",
            "10": "autumn",
            "11": "spring",
            "12": "winter"
        },
        "northwest_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring_winter",
            "04": "spring",
            "05": "autumn",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "autumn",
            "10": "spring",
            "11": "spring_winter",
            "12": "winter"
        },
        "invalid": {
            "01": "invalid",
            "02": "invalid",
            "03": "invalid",
            "04": "invalid",
            "05": "invalid",
            "06": "invalid",
            "07": "invalid",
            "08": "invalid",
            "09": "invalid",
            "10": "invalid",
            "11": "invalid",
            "12": "invalid"
        }
    }
    park_soc_gap = 5
    mxtemp_gap = 5
    mxtsysno_gap = 1
    files = os.listdir(r"D:\WorkSpace\lavidalongparking\result")
    lpInfo = pd.DataFrame([])
    for file in files:
        if re.match(r"new_.", file):
            df = pd.read_csv("D:\\WorkSpace\\lavidalongparking\\result\\" + file)
            lpInfo = lpInfo.append(df.copy())

    lpInfo["Area"] = lpInfo["Region"].apply(
        lambda x:
        "central_china" if x == "华中省份" else
        "south_china" if x == "华南省份" else
        "east_china" if x == "华东省份" else
        "north_china" if x == "华北省份" else
        "northeast_china" if x == "东北省份" else
        "southwest_china" if x == "西南省份" else
        "northwest_china" if x == "西北省份" else
        "invalid"
    )
    for area, values in month_season_dict.items():
        for _, season in values.items():
            final_lpInfo = lpInfo[(lpInfo["Area"] == area) & (lpInfo["Season"] == season)]
            if final_lpInfo.shape[0] != 0:

                park_soc_dist = list(final_lpInfo["U2BSoc"])
                mxtemp_dist = list(final_lpInfo["mxTemp"])
                mxtsysno_dist = list(final_lpInfo["mxTempMno"])

                plt.hist(park_soc_dist, bins=np.arange(0, 105, park_soc_gap), histtype="bar", rwidth=0.8)
                x_major_locator = MultipleLocator(park_soc_gap)
                ax = plt.gca()
                ax.xaxis.set_major_locator(x_major_locator)
                plt.xlim(0, 105)
                plt.xlabel('park_soc')
                plt.ylabel('count')
                plt.savefig(
                    r"D:\project\task_shiyuan\result0607\result\picture\ParkSocDist-{a}-{s}.png".format(a=area,
                                                                                                        s=season))
                plt.close()
                # plt.show()

                plt.hist(mxtemp_dist, bins=np.arange(-20, 60, mxtemp_gap), histtype="bar", rwidth=0.8)
                x_major_locator = MultipleLocator(mxtemp_gap)
                ax = plt.gca()
                ax.xaxis.set_major_locator(x_major_locator)
                plt.xlim(-20, 60)
                plt.xlabel('mxtemp')
                plt.ylabel('count')
                plt.savefig(
                    r"D:\project\task_shiyuan\result0607\result\picture\MaxTempDist-{a}-{s}.png".format(a=area,
                                                                                                        s=season))
                plt.close()
                # plt.show()

                plt.hist(mxtsysno_dist, bins=np.arange(1, 18, mxtsysno_gap), histtype="bar", rwidth=0.8)
                x_major_locator = MultipleLocator(mxtsysno_gap)
                ax = plt.gca()
                ax.xaxis.set_major_locator(x_major_locator)
                plt.xlim(1, 18)
                plt.xlabel('mxtsysno')
                plt.ylabel('count')
                plt.savefig(
                    r"D:\project\task_shiyuan\result0607\result\picture\MaxTempSysNoDist-{a}-{s}.png".format(a=area,
                                                                                                             s=season))
                plt.close()
                # plt.show()

                with open(r"D:\project\task_shiyuan\result0607\result\statistics\statistic_result-{a}-{s}.txt".format(
                        a=area,
                        s=season),
                        "a", encoding='utf-8', newline='') as f:

                    f.write("park_soc:" + "\n")
                    for k, g in groupby(sorted(park_soc_dist), key=lambda x: x // park_soc_gap):
                        park_soc_info = '{}-{}: {}'.format(k * park_soc_gap, (k + 1) * park_soc_gap - 1,
                                                           len(list(g)))
                        # print(start_soc_info)
                        f.write(park_soc_info + "\n")

                    f.write("\n")
                    f.write("mxtemp:" + "\n")
                    for k, g in groupby(sorted(mxtemp_dist), key=lambda x: x // mxtemp_gap):
                        mxtemp_info = '{}-{}: {}'.format(k * mxtemp_gap, (k + 1) * mxtemp_gap - 1, len(list(g)))
                        # print(mxtemp_info)
                        f.write(mxtemp_info + "\n")

                    f.write("\n")
                    f.write("mxtsysno:" + "\n")
                    for k, g in groupby(sorted(mxtsysno_dist), key=lambda x: x // mxtsysno_gap):
                        mxtsysno_info = '{}-{}: {}'.format(k * mxtsysno_gap, (k + 1) * mxtsysno_gap - 1, len(list(g)))
                        # print(mxtsysno_info)
                        f.write(mxtsysno_info + "\n")

                    f.close()


def vinmatch():
    vinInfo = pd.read_excel(r"D:\WorkSpace\lavidalongparking\里程和地点.xlsx", )

    provMatch = pd.read_excel(r"D:\WorkSpace\lavidalongparking\省份.xlsx")
    seasMatch = pd.read_excel(r"D:\WorkSpace\lavidalongparking\月份季节.xlsx")

    files = os.listdir(r"D:\WorkSpace\lavidalongparking\result")
    for filename in files:
        vinResult = pd.read_csv("D:\\WorkSpace\\lavidalongparking\\result\\" + filename, header=None)
        vinResult = vinResult.drop_duplicates()
        vinToMatch = pd.DataFrame(
            columns=("VIN", "Date", "Mile", "mxTemp", "mxTempMno", "mxTempPrbno", "U2BSoc", "C2BSoc"))
        vinToMatch["VIN"] = vinResult[0]
        vinToMatch["Date"] = vinResult[1]
        vinToMatch["Mile"] = vinResult[2]
        vinToMatch["U2BSoc"] = vinResult[3]
        vinToMatch["mxTemp"] = vinResult[5]
        vinToMatch["mxTempMno"] = vinResult[6]
        vinToMatch["mxTempPrbno"] = vinResult[7]
        vinToMatch["C2BSoc"] = vinResult[9]

        vinMatched = vinToMatch.merge(vinInfo)
        vinMatched['Month'] = pd.to_datetime(vinMatched['Date']).dt.month
        vinMatched = vinMatched.merge(provMatch)
        vinMatched = vinMatched.merge(seasMatch)
        vinMatched = vinMatched.drop(['Mileage', 'Month'], axis=1)

        vinMatched.to_csv("D:\\WorkSpace\\lavidalongparking\\result\\new_" + filename, encoding="utf_8_sig", index=None)

    print('end')


def dist(area, season, start_soc_gap=5, mxtemp_gap=5, mxtsysno_gap=1):
    """
    看一下三个统计数据的分布。

    :return:
    """
    month_season_dict = {
        "central_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring",
            "04": "autumn",
            "05": "summer_autumn",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "summer_autumn",
            "10": "autumn",
            "11": "spring",
            "12": "winter"
        },
        "south_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring",
            "04": "autumn",
            "05": "summer",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "summer",
            "10": "autumn",
            "11": "spring",
            "12": "winter"
        },
        "east_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring",
            "04": "autumn",
            "05": "autumn",
            "06": "summer_autumn",
            "07": "summer",
            "08": "summer",
            "09": "summer_autumn",
            "10": "autumn",
            "11": "spring",
            "12": "winter"
        },
        "north_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring_winter",
            "04": "spring",
            "05": "autumn",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "autumn",
            "10": "spring",
            "11": "spring_winter",
            "12": "winter"
        },
        "northeast_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring_winter",
            "04": "spring",
            "05": "autumn",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "autumn",
            "10": "spring",
            "11": "spring_winter",
            "12": "winter"
        },
        "southwest_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring",
            "04": "autumn",
            "05": "summer_autumn",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "summer_autumn",
            "10": "autumn",
            "11": "spring",
            "12": "winter"
        },
        "northwest_china": {
            "01": "winter",
            "02": "winter",
            "03": "spring_winter",
            "04": "spring",
            "05": "autumn",
            "06": "summer",
            "07": "summer",
            "08": "summer",
            "09": "autumn",
            "10": "spring",
            "11": "spring_winter",
            "12": "winter"
        },
        "invalid": {
            "01": "invalid",
            "02": "invalid",
            "03": "invalid",
            "04": "invalid",
            "05": "invalid",
            "06": "invalid",
            "07": "invalid",
            "08": "invalid",
            "09": "invalid",
            "10": "invalid",
            "11": "invalid",
            "12": "invalid"
        }
    }
    df = pd.read_csv(r"D:\WorkSpace\lavidalongparking\result\new_lavida_longparking.txt", delimiter=",")

    df["Month"] = df["Date"].apply(lambda x: x.split("-")[1])
    df["area"] = df["Region"].apply(
        lambda x:
        "central_china" if x == "华中省份" else
        "south_china" if x == "华南省份" else
        "east_china" if x == "华东省份" else
        "north_china" if x == "华北省份" else
        "northeast_china" if x == "东北省份" else
        "southwest_china" if x == "西南省份" else
        "northwest_china" if x == "西北省份" else
        "invalid"
    )
    df["season"] = list(map(lambda x, y: month_season_dict[y][x], df["month"], df["area"]))

    # df.to_csv(r"D:\project\task_shiyuan\a.txt", index=False)
    # print(df)

    final_df = df[(df["area"] == area) & (df["season"] == season)]
    # print(final_df)
    if final_df.shape[0] != 0:

        start_soc_dist = list(final_df["start_soc"])
        mxtemp_dist = list(final_df["mxtemp"])
        mxtsysno_dist = list(final_df["mxtsysno"])

        plt.hist(start_soc_dist, bins=np.arange(0, 105, start_soc_gap), histtype="bar", rwidth=0.8)
        x_major_locator = MultipleLocator(start_soc_gap)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.xlim(0, 105)
        plt.xlabel('start_soc')
        plt.ylabel('count')
        plt.savefig(
            r"D:\project\task_shiyuan\result0607\result\picture\StartSocDist-{a}-{s}.png".format(a=area, s=season))
        plt.close()
        # plt.show()

        plt.hist(mxtemp_dist, bins=np.arange(-20, 60, mxtemp_gap), histtype="bar", rwidth=0.8)
        x_major_locator = MultipleLocator(mxtemp_gap)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.xlim(-20, 60)
        plt.xlabel('mxtemp')
        plt.ylabel('count')
        plt.savefig(
            r"D:\project\task_shiyuan\result0607\result\picture\MaxTempDist-{a}-{s}.png".format(a=area, s=season))
        plt.close()
        # plt.show()

        plt.hist(mxtsysno_dist, bins=np.arange(1, 18, mxtsysno_gap), histtype="bar", rwidth=0.8)
        x_major_locator = MultipleLocator(mxtsysno_gap)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.xlim(1, 18)
        plt.xlabel('mxtsysno')
        plt.ylabel('count')
        plt.savefig(
            r"D:\project\task_shiyuan\result0607\result\picture\MaxTempSysNoDist-{a}-{s}.png".format(a=area, s=season))
        plt.close()
        # plt.show()

        with open(r"D:\project\task_shiyuan\result0607\result\statistics\statistic_result-{a}-{s}.txt".format(a=area,
                                                                                                              s=season),
                  "a", encoding='utf-8', newline='') as f:

            f.write("start_soc:" + "\n")
            for k, g in groupby(sorted(start_soc_dist), key=lambda x: x // start_soc_gap):
                start_soc_info = '{}-{}: {}'.format(k * start_soc_gap, (k + 1) * start_soc_gap - 1, len(list(g)))
                # print(start_soc_info)
                f.write(start_soc_info + "\n")

            f.write("\n")
            f.write("mxtemp:" + "\n")
            for k, g in groupby(sorted(mxtemp_dist), key=lambda x: x // mxtemp_gap):
                mxtemp_info = '{}-{}: {}'.format(k * mxtemp_gap, (k + 1) * mxtemp_gap - 1, len(list(g)))
                # print(mxtemp_info)
                f.write(mxtemp_info + "\n")

            f.write("\n")
            f.write("mxtsysno:" + "\n")
            for k, g in groupby(sorted(mxtsysno_dist), key=lambda x: x // mxtsysno_gap):
                mxtsysno_info = '{}-{}: {}'.format(k * mxtsysno_gap, (k + 1) * mxtsysno_gap - 1, len(list(g)))
                # print(mxtsysno_info)
                f.write(mxtsysno_info + "\n")

            f.close()
