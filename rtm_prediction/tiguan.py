import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from en_client import en_client
#from genarl_func import time_cost,mail_sender

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
All data with warmingsignal Tiguan -------ods.rtm_reissue_history>>------en.rtm_tiguan

'''
client=en_client()
filepath="D:/21python/rtm/rtm_prediction/new/"


def tiguan_warming_detective():
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
        " FROM ods.rtm_reissue_history WHERE deviceid IN (SELECT deviceid FROM en.vehicle_vin WHERE project like 'Tiguan%') " \
        " AND uploadtime BETWEEN '2019-06-01 00:00:00' AND '2020-05-31 23:59:59' group by deviceid "

    #" FROM ods.rtm_reissue_history INNER JOIN en.vehicle_vin ON ods.rtm_reissue_history.deviceid=en.vehicle_vin.deviceid WHERE en.vehicle_vin.project like 'Tiguan%' group by deviceid "
    aus=client.execute(sql)
    df = pd.DataFrame(aus)
    df.to_csv('tiguan_warning.csv')


# clickhouse中tiguan表预处理
# ods.rtm_reissue_history>>------en.rtm_tiguan  [2019-06-01 2020-5-31]
def pre_ana_tiguan():
    sql="CREATE TABLE IF NOT EXISTS en.rtm_tiguan " \
            "(deviceid String, uploadtime DateTime,d_time Int, vehicle_s UInt8, vehicle_s_c Int8, charg_s UInt8, charg_s_c Int8, " \
            " vehiclespeed Float32, accmiles Float32, soc UInt8, soc_c Int8, operationmode String, " \
            " totalvolt Float64, totalcurrent Float64, BMS_pow Float32, charg_mode String, " \
            " ir UInt32, accpedtrav UInt8, brakepedstat UInt8," \
            " emstat String, emctltemp Int32, emtemp Int32, emspeed Float32, emtq Float32, em_me_pow Float32, " \
            " emvolt Float32, emctlcut Float32, em_el_pow Float32, em_eff Float32, cocesprotemp1 Array(Int8), " \
            " tdfwn UInt8, celohwn UInt8, vedtovwn UInt8, vedtuvwn UInt8, lsocwn UInt8, celovwn UInt8, celuvwn UInt8, " \
            " hsocwn UInt8, jpsocwn UInt8, cesysumwn UInt8, celpoorwn UInt8, inswn UInt8, dctpwn UInt8, bksyswn UInt8, " \
            " dcstwn UInt8, emctempwn UInt8, hvlockwn UInt8, emtempwn UInt8, vesoc UInt8, mxal UInt8, count_wn UInt8 " \
            ") ENGINE = MergeTree() ORDER BY (deviceid, uploadtime )"
    aus=client.execute(sql)
    sql="desc en.rtm_tiguan"
    aus=client.execute(sql)
    print(aus)
    print(len(aus))

    sql="INSERT INTO en.rtm_tiguan " \
        "SELECT deviceid, uploadtime,cast(runningDifference(uploadtime),'Int'), vehicle_s, runningDifference(vehicle_s), charg_s, runningDifference(charg_s), " \
        "cast(vehiclespeed,'Float32'), cast(accmiles,'Float32'), socp, runningDifference(socp), operationmode, " \
        "totalvolt, totalcurrent, totalcurrent*totalvolt/1000 AS P, multiIf(P<-2,'mode3_2',P>=-2 and P<0,'mode2','discharging'), " \
        "cast(ir,'UInt32'), if(accped<0,0,accped), if(brakeped<0,0,brakeped), " \
        "emstat, cast(emctltemp,'Int32'),cast(emtemp,'Int32'), sp, tq, sp*tq/9550 as me_pow, em_v, em_i, em_v*em_i/1000 as el_pow, " \
        "multiIf(emstat=='CLOSED' or el_pow*me_pow==0,0,emstat=='CONSUMING_POWER',me_pow/el_pow,emstat=='GENERATING_POWER',el_pow/me_pow,100), temp_list, " \
        "wn01, wn02, wn03, wn04, wn05, wn06, wn07, wn08, wn09, wn10, wn11, wn12, wn13, wn14, wn15, wn16, wn17, wn18, wn19, if(wn_r<0,0,wn_r), " \
        "(wn01 + wn02 + wn03 + wn04 + wn05 + wn06 + wn07 + wn08 + wn09 + wn10 + wn11 + wn12 + wn13 + wn14 + wn15 + wn16 + wn17 + wn18 + wn19) " \
        "FROM ( SELECT deviceid, uploadtime, if(vehiclestatus=='STARTED',1,0) AS vehicle_s, if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, " \
        "vehiclespeed, accmiles, if(soc<0,0,soc) AS socp, operationmode, totalvolt, totalcurrent, " \
        "ir, cast(accpedtrav,'Int32') AS accped, CAST(brakepedstat,'Int32') AS brakeped, " \
        "emstat, emctltemp, emtemp, cast(emspeed,'Float32') AS sp, cast(emtq,'Float32') AS tq, " \
        "cast(emvolt,'Float32') AS em_v, cast(emctlcut,'Float32') AS em_i, " \
        "cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list, " \
        "if(tdfwn=='true',1,0) as wn01, if(celohwn=='true',1,0) as wn02, if(vedtovwn=='true',1,0) as wn03, if(vedtuvwn=='true',1,0) as wn04, if(lsocwn=='true',1,0) as wn05, " \
        "if(celovwn=='true',1,0) as wn06, if(celuvwn=='true',1,0) as wn07, if(hsocwn=='true',1,0) as wn08, if(jpsocwn=='true',1,0) as wn09, if(cesysumwn=='true',1,0) as wn10, " \
        "if(celpoorwn=='true',1,0) as wn11, if(inswn=='true',1,0) as wn12, if(dctpwn=='true',1,0) as wn13, if(bksyswn=='true',1,0) as wn14, if(dcstwn=='true',1,0) as wn15, " \
        "if(emctempwn=='true',1,0) as wn16, if(hvlockwn=='true',1,0) as wn17, if(emtempwn=='true',1,0) as wn18, if(vesoc=='true',1,0)as wn19, cast(mxal,'Int8') as wn_r  " \
        "FROM ods.rtm_reissue_history " \
        "WHERE vehiclestatus!='ERROR' and chargingstatus!='INVALID' and chargingstatus!='ERROR' and cocesprotemp1!='NULL' " \
        "AND uploadtime BETWEEN '2018-01-01 00:00:00' AND '2020-12-31 23:59:59' AND deviceid IN (SELECT deviceid FROM en.vehicle_vin WHERE project like 'Tiguan%') " \
        "ORDER BY deviceid,uploadtime ) "
    print(sql)
    aus=client.execute(sql)
    sql="SELECT COUNT(deviceid) from en.rtm_tiguan"
    aus=client.execute(sql)
    print(aus)
    sql="SELECT COUNT(DISTINCT deviceid) from en.rtm_tiguan"
    aus=client.execute(sql)
    print(aus)
    sql="SELECT * from en.rtm_tiguan limit 10"
    aus=client.execute(sql)
    df = pd.DataFrame(aus)
    sql="desc en.rtm_tiguan"
    title=pd.DataFrame(client.execute(sql))
    df.columns=title[0]
    df.to_csv('rtm_tiguan.csv')

# 提取报警于非报警样本，时间从2019-06-01~~2020-05-31
# VIN码与报警的日期，作为特征提取的输入
def tiguan_sample():
    import datetime
    
    #提取训练集
    #提取所有的非报警样本， 
    sql="SELECT c0, c1, c2, c3 FROM " \
    "(SELECT deviceid as c0, toDate(uploadtime) as c1, sum(bksyswn) as c2, max(accmiles) as c3 " \
    "FROM en.rtm_tiguan WHERE uploadtime BETWEEN '2019-06-01 00:00:00' AND '2020-05-31 23:59:59' " \
    "GROUP BY deviceid,toDate(uploadtime) ORDER BY deviceid, toDate(uploadtime)) " \
    " WHERE c3>200 AND c2==0 "# 删除里程小于200km
    aus=client.execute(sql)
    print(len(aus))
    df = pd.DataFrame(aus)
    df = df.sample(n=60000)  #随机采样
    print(df.shape)
    df.columns=['VIN','target date','bksyswn','mileage']
    df['start']=df['target date']-datetime.timedelta(days=31)
    df['end']=df['target date']-datetime.timedelta(days=1)
    df.to_csv(filepath + 'train_sample_no_warning.csv')

    #提取所有的报警样本
    sql="SELECT c0, c1,c2,c3 FROM " \
    "(SELECT deviceid as c0, toDate(uploadtime) as c1, sum(bksyswn) as c2, max(accmiles) as c3 " \
    "FROM en.rtm_tiguan WHERE bksyswn>0 AND uploadtime BETWEEN '2019-06-01 00:00:00' AND '2020-09-30 23:59:59' " \
    "GROUP BY deviceid,toDate(uploadtime) ORDER BY deviceid, toDate(uploadtime)) " \
    " WHERE c3>200 "# 删除里程小于200km
    aus=client.execute(sql)
    df = pd.DataFrame(aus)
    df.columns=['VIN','target date','bksyswn','mileage']
    df['start']=df['target date']-datetime.timedelta(days=31)
    df['end']=df['target date']-datetime.timedelta(days=1)
    df.to_csv(filepath + 'train_sample_warning.csv')
    '''
    #测试集暂时不单独提取，rtm_tiguan

    #提取测试集
    #no报警
    sql="SELECT c0, c1, c2, c3 FROM " \
    "(SELECT deviceid as c0, toDate(uploadtime) as c1, sum(bksyswn) as c2, max(accmiles) as c3 " \
    "FROM en.rtm_tiguan WHERE uploadtime BETWEEN '2020-06-01 00:00:00' AND '2020-09-30 23:59:59' " \
    "GROUP BY deviceid,toDate(uploadtime) ORDER BY deviceid, toDate(uploadtime)) " \
    " WHERE c3>200 AND c2==0 "# 删除里程小于200km
    aus=client.execute(sql)
    print(len(aus))
    df = pd.DataFrame(aus)
    df = df.sample(n=60000)
    df.columns=['VIN','target date','bksyswn','mileage']
    df['start']=df['target date']-datetime.timedelta(days=31)
    df['end']=df['target date']-datetime.timedelta(days=1)
    df.to_csv(filepath + 'test_sample_no_warning.csv')

    #报警
    sql="SELECT c0, c1,c2, c3 FROM " \
    "(SELECT deviceid as c0, toDate(uploadtime) as c1, sum(bksyswn) as c2,max(accmiles) as c3 " \
    "FROM en.rtm_tiguan WHERE bksyswn>0 AND uploadtime BETWEEN '2020-06-01 00:00:00' AND '2020-09-30 23:59:59' " \
    "GROUP BY deviceid,toDate(uploadtime) ORDER BY deviceid, toDate(uploadtime)) " \
    " WHERE c3>200 "# 删除里程小于200km
    aus=client.execute(sql)
    print(len(aus))
    df = pd.DataFrame(aus)
    df.columns=['VIN','target date','bksyswn','mileage']
    df['start']=df['target date']-datetime.timedelta(days=31)
    df['end']=df['target date']-datetime.timedelta(days=1)
    df.to_csv(filepath + 'test_sample_warning.csv')
    '''


# 获取样本特征值，获得完整训练数据
#@time_cost
def feature_ex(filename,t_name):
    from rtm_hist.RTM_ana import feature_extract
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
    fe.columns=['VIN','Label','week_num', 'region','province','user_type','acc_mileage','ir','mile','daily mile (mean)','driving time', \
        'v (mean)','v 99%','v 50%','EV %','FV %','acc pedal(mean)','acc pedal(99%)','acc pedal(50%)','dec pedal(mean)','dec pedal(99%)','dec pedal(50%)', \
        'BMS discharge temp max','BMS discharge temp min','BMS discharge temp mean','BMS discharge power max','BMS discharge power mean','cell discharge temp max','cell discharge temp min','cell discharge temp diff max','cell discharge temp diff mean',\
        'E-motor speed max','E-motor speed mean','E-motor torque+ max','E-motor torque+ mean','E-motor torque- max','E-motor torque- mean',\
        'E-motor torque- percentage','E-motor temp mean','E-motor temp 99%','E-motor temp 50%','E-motor temp 1%','LE temp mean','LE temp 99%','LE temp 50%','LE temp 1%',\
        'BMS charge temp max','BMS discharge temp min','BMS charge temp mean','BMS charge power max','BMS charge power mean','cell charge temp max','cell charge temp min','cell charge temp diff max','cell charge temp diff mean',\
        'charge times','mode2 percentage','mode3 percentage','charge start SOC mean','charge start SOC 50%','charge end SOC mean','charge end SOC 50%','mean(ΔSOC)','sum(ΔSOC)','Integrity']

    print("样本个数: {}".format(fe.shape[0]))
    print("特征个数: {}".format(fe.shape[1]))
    print("Label == 1: {}".format(fe[fe.Label == 1].shape[0]))
    print("Label == 0: {}".format(fe[fe.Label == 0].shape[0]))
    print("特征不完整的样本数: {}".format(fe[fe.Integrity == 1].shape[0]))

    fe.to_csv(t_name,encoding="gbk",index=False)



# 训练数据预处理及感知
def pre1():

    filename=filepath+'train_feature_no_warming.csv'
    s1=pd.read_csv(filename,encoding="gbk")    #s1=pd.read_csv(filename,encoding="gbk",index_col=0,header=0)
    filename=filepath+'train_feature_warming.csv'
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
    
    des=s1.describe()
    des.to_csv(filepath+"no_warming_f_describe.csv",encoding="gbk")
    des=s2.describe()
    des.to_csv(filepath+"warming_f_describe.csv",encoding="gbk")

    a=[2]
    a.extend(range(6,64))

    for i in a:
        plt.rcParams['font.sans-serif']=['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus']=False
        plt.style.use('ggplot')

        plt.figure(figsize=(10,5))#设置画布的尺寸
        plt.title(s1.columns[i],fontsize=14)#标题，并设定字号大小
        plt.boxplot([s1.iloc[:,i],s2.iloc[:,i]],showmeans=True, labels = ['No_warming','Warming'],sym = '*')
        #plt.show()
        plt.savefig(filepath+"pic/"+str(i)+"_"+s1.columns[i]+'.jpg')

    
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
    print("报警个数: {}".format(ss[ss.Label == 1].shape[0]))
    print("未报警个数: {}".format(ss[ss.Label == 0].shape[0]))
    
    # 分割特征和Target
    X=ss.drop(labels=['Label',"user_type",'Integrity'],axis=1)
    y=pd.DataFrame(ss['Label'])
    del ss
    print("特征个数: {}".format(X.shape[1]))

    # corr相关系数函数
    c=X.corr()
    c.to_csv(filepath+'特征值之间的相关系数.csv',encoding="gbk")
    print(c)
    sns.heatmap(c)
    #plt.show()
    plt.savefig(filepath+"corr.jpg")

    #归一化
    # 最大最小值归一化 将数值映射到 [-1, 1]之间
    from sklearn.preprocessing import MinMaxScaler
    scaler=MinMaxScaler()
    scaler.fit(X)
    X1 = pd.DataFrame(scaler.transform(X))
    X1.columns = X.columns
    y.columns = ['Label']
    # 标准归一化
    #from sklearn.preprocessing import StandardScaler
    #scaler = StandardScaler()
    #scaler.fit(X)


    X1.to_csv(filepath+'训练样本_x.csv',encoding="gbk")
    y.to_csv(filepath+'训练样本_y.csv',encoding="gbk")

#pre1()

#@time_cost
def xgb_search_param():
    '''
    网格搜索获得最优参数：
    结果：
    模型最优参数 {'learning_rate': 0.005, 'max_depth': 6}
    最佳模型得分 0.6203925515304519
    '''

    filename=filepath+"训练样本_x.csv"
    X = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    #index_col=0声明文件第一列为索引，header=0第一行为列名（默认就是，不必重新申明）
    print(X.columns)
    # 导入特征和label
    filename=filepath+"训练样本_y.csv"
    y = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)


    from sklearn.model_selection import train_test_split
    X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)


    import xgboost as xgb
    from sklearn import metrics
    from sklearn.model_selection import GridSearchCV
    cv_params= {'max_depth': [3,4,5,6,7,8,9,10], 
                'learning_rate': [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]
                }
    model = xgb.XGBClassifier(#learning_rate=0.1,
                            n_estimators=1000,         # 树的个数--1000棵树建立xgboost
                            #max_depth=6,               # 树的深度
                            min_child_weight = 1,      # 叶子节点最小权重
                            gamma=0.,                  # 惩罚项中叶子结点个数前的参数
                            subsample=0.8,             # 随机选择80%样本建立决策树
                            #colsample_btree=0.8,       # 随机选择80%特征建立决策树
                            objective='binary:logistic ', # 指定目标函数    reg:linear (默认)回归任务  reg:logistic
                            # binary:logistic    二分类任务返回概率值  binary：logitraw   二分类任务返回类别
                            # multi：softmax  num_class=n   多分类任务返回类别   multi：softprob   num_class=n   多分类任务返回概率
                            scale_pos_weight=5,        # 解决样本个数不平衡的问题
                            random_state=27,            # 随机数
                            eval_metric = 'auc'         # 回归任务  rmse:均方根误差(默认)   mae--平均绝对误差
                            # 分类任务  error--错误率（二分类）(默认)    auc--roc曲线下面积  logloss--负对数似然函数（二分类）merror--错误率（多分类）mlogloss--负对数似然函数（多分类）
                            )
    gs = GridSearchCV(model, cv_params, scoring='roc_auc', refit=True, verbose=2, cv=5, n_jobs=1)
    gs.fit(X_train,y_train)

    # 模型最优参数
    print('模型最优参数', gs.best_params_)
    print('最佳模型得分', gs.best_score_)


def trian_coment():
    
    filename=filepath+"训练样本_y.csv"
    y = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    filename=filepath+"训练样本_x.csv"
    X = pd.read_csv(filename,encoding="gbk", index_col=0, header=0)
    #index_col=0声明文件第一列为索引，header=0第一行为列名（默认就是，不必重新申明）
    print(X.columns)
    # 导入特征和label
  

    from sklearn.model_selection import train_test_split
    X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)

    import xgboost as xgb
    from sklearn import metrics
    param = {'boosting_type':'gbdt',
            'objective' : 'binary:logistic', #任务类型'logistic'逻辑   'regression'回归
            'eval_metric' : 'auc',
            'eta' : 0.005,                # 如同学习率   0.001~0.01
            'max_depth' : 6,             # 构建树的深度，越大越容易过拟合
            'colsample_bytree':1,#  列采样， 这个参数默认为1
            'subsample': 0.8,    # 随机采样训练样本行采样
            'subsample_freq': 1,  
            'alpha': 0,      #正则化系数，越大越不容易过拟合
            'lambda': 1,  # 控制模型复杂度的权重值的L2 正则化项参数，参数越大，模型越不容易过拟合
            'scale_pos_weight':5#原始数据集中，负样本（label=0)数量比上正样本（label=1)数量
                }
    train_data = xgb.DMatrix(X_train, label=y_train)
    test_data = xgb.DMatrix(X_test_s, label=y_test_s)
    model = xgb.train(param, train_data, evals=[(train_data, 'train'), (test_data, 'valid')], num_boost_round = 5000, early_stopping_rounds=50, verbose_eval=50)
    y_pred = model.predict(test_data)
    #y_pred =[x for x in y_pred]
    y_pred1 = [1 if x>=0.5 else 0 for x in y_pred]
    #x = pd.DataFrame([y_test_s["Label"].tolist(),y_pred,y_pred1])
    #x.to_csv(filepath+"result.csv",encoding="gbk")
    #print('XGBoost 准确率:', metrics.accuracy_score(y_test_s,y_pred))
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
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.savefig(filepath+"roc.jpg")
    plt.show()
    '''
    xgb.plot_importance(model,max_num_features=20,importance_type='gain')
    plt.savefig(filepath+"importance_gain.jpg")
    plt.show()

    xgb.plot_importance(model,max_num_features=20,importance_type='weight')
    plt.savefig(filepath+"importance_weight.jpg")
    plt.show()

        '''


trian_coment()

tiguan_sample()
filename = filepath + "train_sample_warning.csv"
t_name = filepath + 'train_feature_warming.csv'
feature_ex(filename,t_name)
filename = filepath + "train_sample_no_warning.csv"
t_name = filepath + 'train_feature_no_warming.csv'
feature_ex(filename,t_name)

'''
filename = filepath + "test_sample_no_warning.csv"
t_name = filepath + 'test_feature_no_warming.csv'
feature_ex(filename,t_name)
filename = filepath + "test_sample_warning.csv"
t_name = filepath + 'test_feature_warming.csv'
feature_ex(filename,t_name)
'''
pre1()

xgb_search_param()
mail_sender()

