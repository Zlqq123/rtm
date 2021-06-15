import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt 
from imblearn.over_sampling import SMOTE # 过抽样处理库SMOTE
from imblearn.under_sampling import RandomUnderSampler # 欠抽样处理库RandomUnderSampler
#from imblearn.ensemble import EasyEnsemble # 简单集成方法EasyEnsemble

#Synthetic Minority Oversampling Technique(SMOTE)
'''
https://blog.csdn.net/niutingbaby/article/details/96104814
SMOTE（Synthetic Minority Oversampling Technique），合成少数类过采样技术．它是基于随机过采样算法的一种改进方案，由于随机过采样采取简单复制样本的策略来增加少数类样本，这样容易产生模型过拟合的问题，即使得模型学习到的信息过于特别(Specific)而不够泛化(General)，SMOTE算法的基本思想是对少数类样本进行分析并根据少数类样本人工合成新样本添加到数据集中，具体如下图所示，算法流程如下。
(1)对于少数类中每一个样本x，以欧氏距离为标准计算它到少数类样本集中所有样本的距离，得到其k近邻。 
(2)根据样本不平衡比例设置一个采样比例以确定采样倍率N，对于每一个少数类样本x，从其k近邻中随机选择若干个样本，假设选择的近邻为o。 
(3)对于每一个随机选出的近邻o，分别与原样本按照公式o(new)=o+rand(0,1)*(x-o)构建新的样本。
'''

#导入数据文件

filepath="D:/21python/rtm/rtm_prediction/new/"
'''
filename=filepath+'train_feature_no_warming.csv'
s1=pd.read_csv(filename,encoding="gbk")
filename=filepath+'train_feature_warming.csv'
s2=pd.read_csv(filename,encoding="gbk")
s1 = s1.drop(s1[s1.Integrity == 1].index)
s1 = s1.drop(s1[s1.Label == 1].index)
s2 = s2.drop(s2[s2.Integrity == 1].index)
s2 = s2.drop(s2[s2.Label == 0].index)
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
#归一化# 最大最小值归一化 将数值映射到 [-1, 1]之间
from sklearn.preprocessing import MinMaxScaler
scaler=MinMaxScaler()
scaler.fit(X)
X1 = pd.DataFrame(scaler.transform(X))
X1.columns = X.columns
y.columns = ['Label']
X1 = X1.reset_index()
y = y.reset_index()

df = pd.concat([y,X1],axis=1)
'''
filename=filepath+"训练样本_x.csv"
x1 = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
#index_col=0声明文件第一列为索引，header=0第一行为列名（默认就是，不必重新申明）
print(x1.columns)
print(x1.shape)
# 导入特征和label
filename=filepath+"训练样本_y.csv"
y1 = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
print(y1.columns)
print(y1.shape)
x1 = x1.reset_index()
y1 = y1.reset_index()
print(y1.columns)
print(y1.shape)
#reset_index()操作之后新增一列index
x1.drop(labels=['index'],axis=1,inplace=True)
y1.drop(labels=['index'],axis=1,inplace=True)
print(y1.columns)
print(y1.shape)

df = pd.concat([y1,x1],axis=1)
#cancat无法执行的，原因是待合并的两个dataFrame索引并不相同，需要对他们分别重新设置索引：x1 = x1.reset_index()
print(df.columns)
print(df.shape)
groupby_data_orgianl = df.groupby('Label').count() # 对label做分类汇总
print (groupby_data_orgianl) # 打印输出原始数据集样本分类分布

#使用 方法进行过抽样处理
model_smote = SMOTE(random_state=42) # 建立SMOTE模型对象
x_smote_resampled, y_smote_resampled = model_smote.fit_resample(x1,y1) # 输入数据并作过抽样处理
x_smote_resampled = pd.DataFrame(x_smote_resampled, columns=x1.columns) # 将数据转换为数据框并命名列名
y_smote_resampled = pd.DataFrame(y_smote_resampled,columns=['Label']) # 将数据转换为数据框并命名列名
smote_resampled = pd.concat([x_smote_resampled, y_smote_resampled],axis=1) # 按列合并数据框
groupby_data_smote = smote_resampled.groupby('Label').count() # 对label做分类汇总
print (groupby_data_smote) # 打印输出经过SMOTE处理后的数据集样本分类分布

#使用 方法进行过抽样处理
model_smote = SMOTE(random_state=42) # 建立SMOTE模型对象
x_smote_resampled, y_smote_resampled = model_smote.fit_resample(x1,y1) # 输入数据并作过抽样处理
x_smote_resampled = pd.DataFrame(x_smote_resampled, columns=x1.columns) # 将数据转换为数据框并命名列名
y_smote_resampled = pd.DataFrame(y_smote_resampled,columns=['Label']) # 将数据转换为数据框并命名列名
smote_resampled = pd.concat([x_smote_resampled, y_smote_resampled],axis=1) # 按列合并数据框
smote_resampled.to_csv('smote_resample.csv',encoding="gbk")

groupby_data_smote = smote_resampled.groupby('Label').count() # 对label做分类汇总

print (groupby_data_smote) # 打印输出经过SMOTE处理后的数据集样本分类分布

from sklearn.decomposition import PCA 
pca = PCA()                 #pca（n_components）
pca.fit(x_smote_resampled)
print(pca.components_)
print(pca.explained_variance_ratio_)#返回各个成分各自的方差百分比（贡献率）

pca1 = PCA(2)#选取前2个主成分
pca1.fit(x_smote_resampled)
print(pca1.components_)
print(pca1.explained_variance_ratio_)

c=x_smote_resampled.drop(y_smote_resampled[y_smote_resampled.Label == 1].index)
print(c.shape)
s_p=pca1.fit_transform(c)
print(s_p.shape)
c=x_smote_resampled.drop(y_smote_resampled[y_smote_resampled.Label == 0].index)
print(c.shape)
s_n=pca1.fit_transform(c)
print(s_n.shape)

plt.figure(figsize=(6, 4))
p1 = plt.scatter(s_p[:,0],s_p[:,1],s=0.2,c='green')
p2 = plt.scatter(s_n[:,0],s_n[:,1],s=0.2,c='red')
plt.legend([p1, p2], ["no_warming", "warming"], loc='upper left')
plt.gca().get_xaxis().set_visible(False)
plt.gca().get_yaxis().set_visible(False)
plt.savefig("Smote_resampled.jpg")
plt.show()


pca = PCA()                 #pca（n_components）
pca.fit(x1)
print(pca.components_)
print(pca.explained_variance_ratio_)#返回各个成分各自的方差百分比（贡献率）

pca2 = PCA(2)#选取前2个主成分
pca2.fit(x1)
print(pca2.components_)
print(pca2.explained_variance_ratio_)

c=x1.drop(y1[y1.Label == 1].index)
print(c.shape)
o_p=pca2.fit_transform(c)
print(s_p.shape)
c=x1.drop(y1[y1.Label == 0].index)
print(c.shape)
o_n=pca2.fit_transform(c)
print(s_n.shape)

plt.figure(figsize=(6, 4))
p1 = plt.scatter(o_p[:,0],o_p[:,1],s=0.2,c='green')
p2 = plt.scatter(o_n[:,0],o_n[:,1],s=0.2,c='red')
plt.legend([p1, p2], ["no_warming", "warming"], loc='upper left')
plt.gca().get_xaxis().set_visible(False)
plt.gca().get_yaxis().set_visible(False)
plt.savefig("Smote_orginal.jpg")
plt.show()


