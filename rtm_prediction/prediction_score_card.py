
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

filepath="D:/21python/rtm/rtm_prediction/new/"
#评分卡模型
# https://www.jianshu.com/p/c3fa53c54cca

filename=filepath+'train_feature_no_warming.csv'
s1=pd.read_csv(filename,encoding="gbk")    #s1=pd.read_csv(filename,encoding="gbk",index_col=0,header=0)
filename=filepath+'train_feature_warming.csv'
s2=pd.read_csv(filename,encoding="gbk")
#数据预处理
print("原始非报警样本个数: {}".format(s1.shape))
print("原始报警样本个数: {}".format(s2.shape))
s1 = s1.drop(s1[s1.Integrity == 1].index)
s1 = s1.drop(s1[s1.Label == 1].index)
s2 = s2.drop(s2[s2.Integrity == 1].index)
s2 = s2.drop(s2[s2.Label == 0].index)
ss=s1.append(s2)#合并
ss.index=range(ss.shape[0])#index重置
del s1, s2

print(ss.isnull().sum())#检查是否有空值
print('处理后：')
print("样本总数: {}".format(ss.shape[0]))
print("报警个数: {}".format(ss[ss.Label == 1].shape[0]))
print("未报警个数: {}".format(ss[ss.Label == 0].shape[0]))

#onehot编码
from sklearn.preprocessing import LabelEncoder
label_name = ['VIN','region','province']
for a in label_name:
    le = LabelEncoder()
    le.fit(ss[a])
    ss[a]=le.transform(ss[a])

# 分割特征和Target
x1=ss.drop(labels=['week_num','region','user_type','Integrity'],axis=1)
x2=ss[['week_num','region']]


#数据分箱

import math
x2['bin_week_num'] = pd.cut(ss['week_num'], bins=[-math.inf, 10, 20, 30, 40, 50, math.inf])
x2['bin_region'] = pd.cut(ss['region'], bins=[-math.inf, 0.1, 0.2, 0.4, 0.6, 0.7, 0.9, math.inf])
print(x2)

# 采用等频的方式进行分箱
a=['VIN','province','acc_mileage','ir','mile','daily mile (mean)','driving time','v (mean)', \
    'v 99%','v 50%','EV %','FV %','acc pedal(mean)','acc pedal(99%)','acc pedal(50%)', \
    'dec pedal(mean)','dec pedal(99%)','dec pedal(50%)','BMS discharge temp max','BMS discharge temp min', \
    'BMS discharge temp mean','BMS discharge power max','BMS discharge power mean','cell discharge temp max', \
    'cell discharge temp min','cell discharge temp diff max','cell discharge temp diff mean','E-motor speed max', \
    'E-motor speed mean','E-motor torque+ max','E-motor torque+ mean','E-motor torque- max', \
    'E-motor torque- mean','E-motor torque- percentage','E-motor temp mean','E-motor temp 99%', \
    'E-motor temp 50%','E-motor temp 1%','LE temp mean','LE temp 99%','LE temp 50%','LE temp 1%', \
    'BMS charge temp max','BMS discharge temp min','BMS charge temp mean','BMS charge power max', \
    'BMS charge power mean','cell charge temp max','cell charge temp min','cell charge temp diff max',\
    'cell charge temp diff mean','charge times','mode2 percentage','mode3 percentage','charge start SOC mean', \
    'charge start SOC 50%','charge end SOC mean','charge end SOC 50%','mean(ΔSOC)','sum(ΔSOC)']

for aa in a:
    x2['bin_' + aa]=pd.qcut(ss[aa], q=7,duplicates='drop')

x=pd.concat([x1, x2], axis=1)

del ss,x1,x2

x.to_csv(filepath+'分箱_cridet.csv',encoding="gbk")


# 计算IV，衡量自变量的预测能力,IV的全称是Information Value，中文意思是信息价值
# https://blog.csdn.net/shenxiaoming77/article/details/78771698
def cal_IV(df, feature, target):

    lst = []
    cols = ['Variable', 'Value', 'All', 'Bad']
    for i in range(df[feature].nunique()): # nunique = unique的个数
        val = list(df[feature].unique())[i]
        # 统计feature, feature_value, 这个value的个数，这个value导致target=1的个数
        temp1 = df[df[feature]==val].count()[feature] # 总数
        temp2 = df[(df[feature] == val) & (df[target]==1)].count()[feature] # target=1的个数
        #print(feature, val, temp1, temp2)
        lst.append([feature, val, temp1, temp2])
    # 计算字段
    data = pd.DataFrame(lst, columns=cols)
    data = data[data['Bad']>0]
    data['Share'] = data['All'] / data['All'].sum()
    data['Bad Rate'] = data['Bad'] / data['All'] # 这个value导致bad情况，在这个value个数的比例
    data['Distribution Bad'] = data['Bad'] / data['Bad'].sum() # 这个value导致Bad 在所有Bad中的比例
    data['Distribution Good'] = (data['All'] - data['Bad']) / (data['All'].sum() - data['Bad'].sum())
    data['WOE'] = np.log1p(data['Distribution Bad'] / data['Distribution Good'])
    #data['IV'] = ((data['Distribution Bad'] - data['Distribution Good']) * data['WOE']).sum()
    data['IV'] = (data['Distribution Bad'] - data['Distribution Good']) * data['WOE']
    
    data = data.sort_values(by=['Variable', 'Value'], ascending=True)
    #print(data)
    return data['IV'].sum()



bin_cols = [c for c in x.columns.values if c.startswith('bin_')]
IV_value=pd.DataFrame(columns=['col_name','IV'], index=[])

for col in bin_cols:
    temp_IV = cal_IV(x, col, 'Label')
    print(col, temp_IV)
    IV_value=IV_value.append([{'col_name':col,'IV':temp_IV}],ignore_index = True)

IV_value.to_csv(filepath+'cridet_IV.csv',encoding="gbk")

# WOE的全称是“Weight of Evidence”，即证据权重。WOE是对原始自变量的一种编码形式
def cal_WOE(df, features, target):

    for feature in features:
        df_woe = df.groupby(feature).agg({target:['sum', 'count']})
        # ‘delimiter’.join(seq)，通过指定字符连接序列中元素后生成的新字符串
        df_woe.columns = list(map(''.join, df_woe.columns.values))
        #print(df_woe.columns)
        df_woe = df_woe.reset_index()
        df_woe = df_woe.rename(columns={target+'sum': 'bad', target+'count':'all'})
        #print(df_woe)
        
        df_woe['good'] = df_woe['all'] - df_woe['bad']
        df_woe = df_woe[[feature, 'good', 'bad']]        
        df_woe['bad_rate'] = df_woe['bad'] / df_woe['bad'].sum()
        df_woe['good_rate'] = df_woe['good'] / df_woe['good'].sum()
        print(df_woe['good_rate'])
        # 计算woe
        #df_woe['woe'] = np.log(df_woe['bad_rate'].divide(df_woe['good_rate']))
        df_woe['woe'] = np.log1p(df_woe['bad_rate'] / df_woe['good_rate'])
        #df_woe['woe'] = df_woe['bad_rate'] / df_woe['good_rate']
        # 在后面拼接上 _feature, 比如 _age
        df_woe.columns = [c if c==feature else c+'_'+feature for c in list(df_woe.columns.values)]
        # 拼接
        df = df.merge(df_woe, on=feature, how='left')
    return df


bin_cols = ['bin_driving time','bin_cell discharge temp diff mean','bin_charge end SOC mean', \
    'bin_cell discharge temp diff max','bin_week_num','bin_mile','bin_E-motor speed max', \
    'bin_daily mile (mean)','bin_BMS discharge power max','bin_charge times']


#通过IV值对特征变量进行筛选
# https://blog.csdn.net/sscc_learning/article/details/78591210?utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-2.vipsorttest&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-2.vipsorttest
df_woe = cal_WOE(x, bin_cols, 'Label')

df_woe.describe()

woe_cols = [c for c in list(df_woe.columns.values) if 'woe' in c]
df_woe[woe_cols]
df_woe.to_csv(filepath+'cridet_WOE.csv',encoding="gbk")
print(bin_cols)
feature_cols = [x[4:] for x in bin_cols]


# 得到WOE规则
df_bin_to_woe = pd.DataFrame(columns=['features', 'bin', 'woe'])
for f in feature_cols:
    b = 'bin_' + f
    w = 'woe_bin_' + f
    # 对于每个feature 找到相应的bin和woe字段
    df = df_woe[[w, b]].drop_duplicates()
    df.columns = ['woe', 'bin']
    df['features'] = f
    df = df[['features', 'bin', 'woe']]
    # 按照行的方式进行拼接
    df_bin_to_woe = pd.concat([df_bin_to_woe, df])
print(df_bin_to_woe)

print(df_woe[woe_cols])

df=df_woe[woe_cols]
df.to_csv(filepath+'cridet_WOE1.csv',encoding="gbk")



# 数据集切分
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(df_woe[woe_cols], df_woe['Label'], test_size=0.2, random_state=33)
print('bad rate is', y_train.mean())


from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score

model = LogisticRegression(random_state=33, class_weight='balanced', max_iter=500).fit(x_train, y_train)

y_pred = model.predict(x_test)
print(accuracy_score(y_pred, y_test))
print(roc_auc_score(y_pred, y_test))



a=1