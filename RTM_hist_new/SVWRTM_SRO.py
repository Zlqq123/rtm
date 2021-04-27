import sys
sys.path.append(".")

import numpy as np
import pandas as pd




def SRO_fuc_ContinuousVariableHistgram(interval, input_data):
    BL=65536
    wa = np.zeros(len(interval),dtype=int)
    for i in range(0, len(input_data), BL):
        sa=np.sort(input_data[i:i+BL])
        wa+=np.searchsorted(sa,interval)
    
    re=np.diff(wa)

    if show_interval:
        block=interval_str(interval)
        return block,re
    return re

def SRO_fuc_box_hist_inner(inx,strx):
    '''
    内部函数
    输入： inx： np.array一维数组
        strx: str 变量名称
    返回df: pd.dataframe
    数组的最小值，四分位点，最大值，平均值
    '''
    df=pd.DataFrame([np.min(inx),np.percentile(inx,1),np.percentile(inx,25), \
        np.percentile(inx,50),np.percentile(inx,75),np.percentile(inx,99), \
        np.max(inx),np.mean(inx)])
    df.index = ['min','1%percentile','25%percentile','50%percentile','75%percentile','99%percentile','max','mean']
    df.columns=[strx]
    return df

def SRO_fuc_interval_str_inner(interval):
    '''
    内部函数

    interval list--> interval str list
    eg:
    interval_str([1,2,3,4])
    >>>['1~2','2~3','3~4']
    '''
    block=[]
    for i in range(1,len(interval)):
        block.append(str(interval[i-1])+'~'+str(interval[i]))
    return block