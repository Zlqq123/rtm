
from en_client import en_client
from genarl_func import time_cost
import pandas as pd
import matplotlib.pyplot as plt
client=en_client()
'''
original table
All data(without warmingsignal)----------------------------- ods.rtm_details  
All data with warmingsignal------------------------ods.rtm_reissue_history

2020/03 Data(without warmingsignal)------------------------- en.rtm_vds
2020/06 Data(with warmingsignal)---------------------------- en.rtm_data_june

attachment table:
VIN Usertype Project region province mileage---------------- en.vehicle_vin

pre analyzed tabel:
2020/06 Data(with warmingsignal) after pre analyzing----- en.rtm_data_june-->-->--- en.rtm_6_2th
All data(without warmingsignal) after pre analyzing -------- en.rtm_2th
All data with warmingsignal Tiguan -------------en.rtm_tiguan

'''
filepath="D:/21python/rtm/prediction_data/20190701_20200531_tiguan_30/"

filename=filepath+"no_warming_f.csv"
s1=pd.read_csv(filename,encoding="gbk")
filename=filepath+"warming_f.csv"
s2=pd.read_csv(filename,encoding="gbk")
print(s1.shape)
print(s2.shape)
s1 = s1.drop(s1[s1.Integrity == 1].index)
print(s1.shape)
s1 = s1.drop(s1[s1.Label == 1].index)
print(s1.shape)
s2 = s2.drop(s2[s2.Integrity == 1].index)
print(s2.shape)
s2 = s2.drop(s2[s2.Label == 0].index)
print(s2.shape)
'''
des=s1.describe()
des.to_csv("no_warming_f_describe.csv",encoding="gbk")
des=s2.describe()
des.to_csv("warming_f_describe.csv",encoding="gbk")

for i in range(6,64):
    plt.rcParams['font.sans-serif']=['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus']=False
    plt.style.use('ggplot')

    plt.figure(figsize=(10,5))#设置画布的尺寸
    plt.title(s1.columns[i],fontsize=14)#标题，并设定字号大小
    plt.boxplot([s1.iloc[:,i],s2.iloc[:,i]],showmeans=True, labels = ['No_warming','Warming'],sym = '*')
    #plt.show()
    plt.savefig(filepath+"pic/"+str(i)+"_"+s1.columns[i]+'.jpg')

'''
ss=s1.append(s2)
print(ss.shape)
del s1,s2
#数据预处理
from sklearn.preprocessing import LabelEncoder
label_name = ['VIN','region','province']
for a in label_name:
    le = LabelEncoder()
    le.fit(ss[a])
    ss[a]=le.transform(ss[a])

print(ss.isnull().sum())
print("样本个数: {}".format(ss.shape[0]))
print("特征个数: {}".format(ss.shape[1]))
print("报警个数: {}".format(ss[ss.Label == 1].shape[0]))
print("未报警个数: {}".format(ss[ss.Label == 0].shape[0]))
# 分割特征和Target
X=ss.drop(labels=['Label',"user_type",'Integrity'],axis=1)
y=ss['Label']
'''
ss.to_csv(filepath+'训练样本.csv',encoding="gbk")

# corr相关系数函数
c=X.corr()
c.to_csv(filepath+'特征值之间的相关系数.csv',encoding="gbk")
'''




print("end")


def tiguan_sample():
    import datetime
    #提取所有的非报警样本， 时间从2019-07-01~~2020-05-31
    sql="SELECT c0, c1,c3 FROM " \
    "(SELECT deviceid as c0, toDate(uploadtime) as c1, max(accmiles) as c3 " \
    "FROM en.rtm_tiguan WHERE bksyswn==0 AND uploadtime BETWEEN '2018-01-01 00:00:00' AND '2020-12-31 23:59:59' " \
    "GROUP BY deviceid,toDate(uploadtime) ORDER BY deviceid, toDate(uploadtime)) " \
    " WHERE c3>200 "# 删除里程小于200km
    aus=client.execute(sql)
    print(len(aus))
    df = pd.DataFrame(aus)
    df = df.sample(n=60000)  #随机采样
    print(df.shape)
    df.columns=['VIN','target date','mileage']
    df['start']=df['target date']-datetime.timedelta(days=31)
    df['end']=df['target date']-datetime.timedelta(days=1)
    df.to_csv('D:/21python/rtm/prediction_data/20190701_20200531_tiguan_30/sample_no_warning.csv')

    #提取所有的报警样本
    sql="SELECT c0, c1,c2,c3 FROM " \
    "(SELECT deviceid as c0, toDate(uploadtime) as c1, sum(bksyswn) as c2,max(accmiles) as c3 " \
    "FROM en.rtm_tiguan WHERE bksyswn>0 AND uploadtime BETWEEN '2018-01-01 00:00:00' AND '2020-12-31 23:59:59' " \
    "GROUP BY deviceid,toDate(uploadtime) ORDER BY deviceid, toDate(uploadtime)) " \
    " WHERE c3>200 "# 删除里程小于200km
    aus=client.execute(sql)
    df = pd.DataFrame(aus)
    df.columns=['VIN','target date','bksyswn','mileage']
    df['start']=df['target date']-datetime.timedelta(days=31)
    df['end']=df['target date']-datetime.timedelta(days=1)
    df.to_csv('D:/21python/rtm/prediction_data/20190701_20200531_tiguan_30/sample_warning.csv')

def f1():
    #tiguan 总报警数
    sql=" with if(tdfwn=='true',1,0) as wn01, if(celohwn=='true',1,0) as wn02, if(vedtovwn=='true',1,0) as wn03, " \
        " if(vedtuvwn=='true',1,0) as wn04, if(lsocwn=='true',1,0) as wn05, if(celovwn=='true',1,0) as wn06, " \
        " if(celuvwn=='true',1,0) as wn07, if(hsocwn=='true',1,0) as wn08, if(jpsocwn=='true',1,0) as wn09, " \
        " if(cesysumwn=='true',1,0) as wn10, if(celpoorwn=='true',1,0) as wn11, if(inswn=='true',1,0) as wn12, " \
        " if(dctpwn=='true',1,0) as wn13, if(bksyswn=='true',1,0) as wn14, if(dcstwn=='true',1,0) as wn15, " \
        " if(emctempwn=='true',1,0) as wn16, if(hvlockwn=='true',1,0) as wn17, if(emtempwn=='true',1,0) as wn18, " \
        " if(vesoc=='true',1,0)as wn19 SELECT deviceid, sum(wn01),sum(wn02), " \
        " sum(wn03),sum(wn04), sum(wn05),sum(wn06),sum(wn07),sum(wn08),sum(wn09),sum(wn10), " \
        " sum(wn11),sum(wn12),sum(wn13),sum(wn14),sum(wn15),sum(wn16),sum(wn17),sum(wn18),sum(wn19) " \
        " FROM ods.rtm_reissue_history WHERE deviceid like 'LSVU%' group by deviceid "
    aus=client.execute(sql)
    df = pd.DataFrame(aus)
    df.to_csv('tiguan_warning.csv')

from rtm.RTM_ana import feature_extract

@time_cost
def feature_ex(filename,t_name):
    import datetime
    tb1_name="en.rtm_tiguan"
    fe=pd.DataFrame()
    fin=pd.read_csv(filename,encoding="gbk")
    print(fin.dtypes)
    for __,row in fin.iterrows():
        vin=row['VIN']
        target=row['target date']
        start=row['start']
        end=row['end']
        l1=feature_extract(vin,start,end,target,tb1_name)
        a=l1()
        v=[vin]
        for x in a:
            v.extend(x)
        if 'null' in v:# 判断是否有缺省特征
            v.append(1)
        else:
            v.append(0)
        #print(v)
        fe=fe.append([v],ignore_index=True)
    print(fe.shape)
    fe.columns=['VIN','Label','region','province','user_type','acc_mileage','ir','mile','daily mile (mean)','driving time', \
        'v (mean)','v 99%','v 50%','EV %','FV %','acc pedal(mean)','acc pedal(99%)','acc pedal(50%)','dec pedal(mean)','dec pedal(99%)','dec pedal(50%)', \
        'BMS discharge temp max','BMS discharge temp min','BMS discharge temp mean','BMS discharge power max','BMS discharge power mean','cell discharge temp max','cell discharge temp min','cell discharge temp diff max','cell discharge temp diff mean',\
        'E-motor speed max','E-motor speed mean','E-motor torque+ max','E-motor torque+ mean','E-motor torque- max','E-motor torque- mean',\
        'E-motor torque- percentage','E-motor temp mean','E-motor temp 99%','E-motor temp 50%','E-motor temp 1%','LE temp mean','LE temp 99%','LE temp 50%','LE temp 1%',\
        'BMS charge temp max','BMS discharge temp min','BMS charge temp mean','BMS charge power max','BMS charge power mean','cell charge temp max','cell charge temp min','cell charge temp diff max','cell charge temp diff mean',\
        'charge times','mode2 percentage','mode3 percentage','charge start SOC mean','charge start SOC 50%','charge end SOC mean','charge end SOC 50%','mean(ΔSOC)','sum(ΔSOC)','Integrity']

    fe.to_csv(t_name,encoding="gbk")

'''
tiguan_sample()
filename1="D:/21python/rtm/prediction_data/20190701_20200531_tiguan_30/sample_no_warning.csv"
t_name1='D:/21python/rtm/prediction_data/20190701_20200531_tiguan_30/no_warming_f.csv'
filename2="D:/21python/rtm/prediction_data/20190701_20200531_tiguan_30/sample_warning.csv"
t_name2='D:/21python/rtm/prediction_data/20190701_20200531_tiguan_30/warming_f.csv'
feature_ex(filename1,t_name1)
feature_ex(filename2,t_name2)
'''

