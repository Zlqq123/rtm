import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from en_client import en_client
from vin import myself
client=en_client()
vin=myself()


sql="desc ods.rtm_details"
title=pd.DataFrame(client.execute(sql))
sql="SELECT * from ods.rtm_details WHERE deviceid=='"+vin+"' AND uploadtime between '2020/09/01 00:00:00' AND '2020/12/31 23:59:59' order by uploadtime "
aus=client.execute(sql)
df = pd.DataFrame(aus)
# 重命名列命
df.columns=title[0]
print(df.columns)
# 删除指定列
df.drop(['deviceid','devicetype','drivermotorsn','emnum','cocessys2','vocesd2','cocesd2','cel1num2','sbofsn2','cfnum2','celv2','cocessystemp2'],axis=1,inplace=True)
#print(df.dtypes)
# 类型转化
df[['vehiclespeed','accmiles','ir','accpedtrav','brakepedstat','emctltemp','emspeed','emtq','emtemp','emvolt','emctlcut', \
    'cs','fc','lg','lat','mxvsysno','mxvcelno','mxcelvt','mivsysno','mivcelno','micelvt','mxtsysno','mxtpno','mxtemp','mitsysno','mitpno','mitemp', \
    'cocessys1','vocesd1','cocesd1','cel1num1','sbofsn1','cfnum1']] = df[['vehiclespeed','accmiles','ir','accpedtrav','brakepedstat', \
    'emctltemp','emspeed','emtq','emtemp','emvolt','emctlcut','cs','fc','lg','lat','mxvsysno','mxvcelno','mxcelvt','mivsysno','mivcelno','micelvt','mxtsysno', \
    'mxtpno','mxtemp','mitsysno','mitpno','mitemp','cocessys1','vocesd1','cocesd1','cel1num1','sbofsn1','cfnum1']].apply(pd.to_numeric)

#print(df.dtypes)
df.to_csv('test.csv')

#散点图
#电机转矩转速分布
df1=df[['emspeed','emtq']]
print(df1.shape)
df1 = df1[ (df1['emspeed']!=0) & (df1['emtq']!=0)]
print(df1.shape)

g = sns.jointplot(x ='emspeed', y='emtq', data=df1,
                  kind = 'kde', color = 'k', stat_func= sci.pearsonr,
                  shade_lowest = False)
#添加散点图
g.plot_joint(plt.scatter, c = 'w', s = 30, linewidth = 1, marker='+')

def p4():
    g = sns.JointGrid(x ='emspeed', y='emtq', data=df1)
    g = g.plot_joint(sns.kdeplot, cmap = 'Reds_r')     #绘制密度图
    plt.grid(linestyle = '--')
    g.plot_marginals(sns.kdeplot, shade = True, color = 'r') #绘制x,y轴密度图
    plt.show()

def p1():
    plt.scatter(df1['emspeed'], df1['emtq'],marker='.')
    plt.show()

def p2():# 用Seaborn画散点图
    #import scipy.stats as sci
    sns.jointplot(x='emspeed', y='emtq', #设置xy轴
                data = df1,  #设置数据
                color = 'b', #设置颜色
                s = 10, linewidth = 1,#设置散点大小、及宽度(只针对scatter), #edgecolor = 'w'边缘颜色 #stat_func=sci.pearsonr,计算两个变量之间的相关系数
                kind = 'scatter',#设置类型：'scatter','reg','resid','kde','hex'#stat_func=<function pearsonr>,
                space = 0.1, #设置散点图和布局图的间距
                size = 8, #图表大小(自动调整为正方形))
                ratio = 5, #散点图与布局图高度比，整型
                marginal_kws = dict(bins=15, rug =True), #设置柱状图箱数，是否设置rug
                )
    plt.show()

def p3():
    sns.jointplot(x='emspeed', y='emtq', #设置xy轴，显示columns名称
                data = df1,  #设置数据
                color = 'b', #设置颜色
                #stat_func=sci.pearsonr,计算两个变量之间的相关系数
                kind = 'hex',#设置类型：'scatter','reg','resid','kde','hex'
                space = 0.1, #设置散点图和布局图的间距
                size = 8, #图表大小(自动调整为正方形))
                ratio = 5, #散点图与布局图高度比，整型
                )
    plt.show()


a=1
#折线图




#直方图




#条形图



#箱线图


#饼图


#热力图


#蜘蛛图

#二元变量分布

#成对关系