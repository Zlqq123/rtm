import sys
sys.path.append('./')
import xlsxwriter
import csv
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from genarl_func import print_in_excel,time_cost
from en_client import en_client

client=en_client()

filename="D:/21python/rtm/prediction_data/feature_no_warming.csv"
s1=pd.read_csv(filename,encoding="gbk")
filename="D:/21python/rtm/prediction_data/feature_warming.csv"
s2=pd.read_csv(filename,encoding="gbk")
print(s1.shape)
print(s2.shape)
#s3=s1.sample(n=600)
s3=s1.sample(n=600,random_state=123,axis=0)#随机从rs数据集中抽取2000行数据，并且保证下次抽取时与此次抽取结果一样
print(s3.shape)


ss=s3.append(s2)
print(ss.shape)
del s1,s2,s3#清除变量以释放内存

#数据预处理
from sklearn.preprocessing import LabelEncoder
label_name = ['VIN','region','province','user_type']
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
X=ss.drop(labels=['Nr','Label',"user_type"],axis=1)
y=ss['Label']

# corr相关系数函数
c=X.corr()
c.to_csv('特征值之间的相关系数.csv',encoding="gbk")
#print(c)
#sns.heatmap(c)
#plt.show()

#归一化，标准归一化
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(X)
X = scaler.transform(X)

c=pd.DataFrame(X).corr()
c.to_csv('特征值之间的相关系数1.csv',encoding="gbk")

from sklearn.model_selection import train_test_split
X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)

import xgboost as xgb
from sklearn import metrics
param = {'boosting_type':'gbdt',
         'objective' : 'binary:logistic', #任务类型
         #'objective' : 'regression', #任务类型
         'eval_metric' : 'auc',
         'eta' : 0.01,   # 如同学习率
         'max_depth' : 15,     # 构建树的深度，越大越容易过拟合
         'colsample_bytree':0.8,# 这个参数默认为1，是每个叶子里面h的和至少是多少
    # 对于正负样本不均衡时的0-1分类而言，假设h在0.01附近，min_child_weight为1
    #意味着叶子节点中最少需要包含100个样本。这个参数非常影响结果，
    # 控制叶子节点中二阶导的和的最小值，该参数值越小，越容易过拟合
         'subsample': 0.9,    # 随机采样训练样本
         'subsample_freq': 8,  
         'alpha': 0.6,
         'lambda': 0,  # 控制模型复杂度的权重值的L2 正则化项参数，参数越大，模型越不容易过拟合
        }

train_data = xgb.DMatrix(X_train, label=y_train)
test_data = xgb.DMatrix(X_test_s, label=y_test_s)
model = xgb.train(param, train_data, evals=[(train_data, 'train'), (test_data, 'valid')], num_boost_round = 10000, early_stopping_rounds=200, verbose_eval=25)
y_pred = model.predict(test_data)
y_pred1 = [1 if x>=0.5 else 0 for x in y_pred]
print('XGBoost 预测结果', y_pred1)
print('XGBoost 准确率:', metrics.accuracy_score(y_test_s,y_pred1))

from sklearn.metrics import roc_curve,auc


fpr, tpr, thresholds = roc_curve(y_test_s, y_pred, pos_label=1)

roc_auc = auc(fpr, tpr)  ###计算auc的值

lw = 2
plt.figure(figsize=(8, 5))
plt.plot(fpr, tpr, color='darkorange',
         lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)  ###假正率为横坐标，真正率为纵坐标做曲线
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.grid()
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic example')
plt.legend(loc="lower right")
plt.show()


'''
All data(without warmingsignal)----------------------------- ods.rtm_details  
warmingsignal------------------------ods.rtm_reissue_history
2020/03 Data(without warmingsignal)------------------------- en.rtm_vds
2020/06 Data(with warmingsignal)---------------------------- en.rtm_data_june
2020/06 Data(with warmingsignal) after pre analyzing-------- en.rtm_6_2th
VIN Usertype Project region province mileage---------------- en.vehicle_vin 
'''

tb1_name="en.rtm_6_2th"

def wm_detect(proj):
    if proj=="lavida":
        con=" deviceid like 'LSVA%' "
    elif proj=="tiguan":
        con=" deviceid like 'LSVU%' "
    elif proj=="passat":
        con=" deviceid like 'LSVC%' "
    
    sql="SELECT deviceid,uploadtime,inswn,ir/1000,charg_s,vehicle_s,vehiclespeed,soc,accmiles,BMS_pow,charg_mode,mxal " \
        "FROM en.rtm_6_2th where inswn>0 and "+con+" order by deviceid, uploadtime "
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_inswn.xlsx')
    sql="SELECT deviceid,uploadtime,jpsocwn,charg_s,vehicle_s,vehiclespeed,soc,soc_c,accmiles,mxal " \
        "FROM en.rtm_6_2th where jpsocwn>0 and "+con+" order by deviceid, uploadtime "
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_jpsocwn.xlsx')
    sql="SELECT deviceid,uploadtime,bksyswn,mxal,charg_s,vehicle_s,vehiclespeed,soc,soc_c,accmiles " \
    "FROM en.rtm_6_2th where bksyswn>0 and"+con+" order by deviceid, uploadtime "
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_bksyswn.xlsx')
    
    sql="SELECT deviceid,uploadtime,hvlockwn,mxal,charg_s,vehicle_s,vehiclespeed,soc,soc_c,accmiles " \
        "FROM en.rtm_6_2th where hvlockwn>0 and "+con+" order by deviceid, uploadtime "
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_hvlockwn.xlsx')

def acc_wn(proj):
    if proj=="lavida":
        con=" deviceid like 'LSVA%' "
    elif proj=="tiguan":
        con=" deviceid like 'LSVU%' "
    elif proj=="passat":
        con=" deviceid like 'LSVC%' "
    #查询每辆车max(uploadtime)对应accmiles
    sql="SELECT  deviceid,uploadtime,accmiles from en.rtm_6_2th " \
        "INNER JOIN (SELECT deviceid,min(uploadtime) as x1 from en.rtm_6_2th group by deviceid) as tbx " \
        "ON (tbx.deviceid=en.rtm_6_2th.deviceid and tbx.x1=en.rtm_6_2th.uploadtime ) " \
        "WHERE"+con+" order by deviceid, uploadtime"
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_start_milage.xlsx')
    #查询每辆车min(uploadtime)对应accmiles
    sql="SELECT  deviceid,uploadtime,accmiles from en.rtm_6_2th " \
        "INNER JOIN (SELECT deviceid,max(uploadtime) as x1 from en.rtm_6_2th group by deviceid) as tbx " \
        "ON (tbx.deviceid=en.rtm_6_2th.deviceid and tbx.x1=en.rtm_6_2th.uploadtime ) " \
        "WHERE "+con+" order by deviceid, uploadtime"
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_end_milage.xlsx')
    #查询所有故障
    sql="SELECT deviceid,toDate(uploadtime),sum(celohwn), sum(jpsocwn),sum(inswn),sum(bksyswn),sum(dcstwn),sum(emctempwn),sum(hvlockwn), avg(accmiles) " \
        "FROM en.rtm_6_2th WHERE "+con+" and count_wn>0 group by deviceid,toDate(uploadtime) order by deviceid, toDate(uploadtime) "
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_warming.xlsx')



def pre1():
    '''
    非报警样本筛选
    '''
    import datetime
    filename="D:/03RTM/报警预测/tiguan.csv"
    vin=[]
    s=[]
    e=[]
    rawdata_col_define={}
    with open(filename) as f:
        reader=csv.reader(f)
        header_row=next(reader)
        for index, column_header in enumerate(header_row):
            rawdata_col_define[column_header]=index   # find raw data columns title & index {columst title: colunms index}
        for row in reader:
            vin.append(row[rawdata_col_define['vin']])
            s.append(row[rawdata_col_define['start time']])
            e.append(row[rawdata_col_define['end time']])
    all_sample=[]
    i=0
    delta1=datetime.timedelta(days=5)
    delta2=datetime.timedelta(days=6)
    vl=0


    while i<len(vin):
        start_time=datetime.datetime.strptime(s[i],'%Y/%m/%d').date()
        end_time=datetime.datetime.strptime(e[i],'%Y/%m/%d').date()
        vv=vin[i]
        if vv!=vl:
            os=start_time
        else:
            os=ot+datetime.timedelta(days=1)
        oe=os+delta1
        ot=os+delta2
        vl=vin[i]
        if oe<end_time:
            all_sample.append([vv,os,oe,ot,start_time,end_time])
        else:
            i=i+1

    workbook = xlsxwriter.Workbook('tiguan_sample.xlsx')
    worksheet = workbook.add_worksheet("sheet1")
    for i in range(len(all_sample)):
        for j in range(len(all_sample[0])):
            worksheet.write(i+1,j,all_sample[i][j])
    workbook.close()



from rtm.RTM_ana import feature_extract
@time_cost
def feature_ex(filename,t_name):
    fe=pd.DataFrame()
    fin=pd.read_csv(filename,encoding="gbk")
    print(fin.dtypes)
    for __,row in fin.iterrows():
        vin=row['VIN']
        start=row['start']
        end=row['end']
        target=row['target date']
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

filename1="D:/21python/rtm/prediction_data/tiguan_no_warming.csv"
t_name1='no_warming_f.csv'
filename2="D:/21python/rtm/prediction_data/tiguan_warming.csv"
t_name2='warming_f.csv'
#feature_ex(filename1,t_name1)
#feature_ex(filename2,t_name2)




