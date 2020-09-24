import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from genarl_func import print_in_excel
from en_client import en_client
client=en_client()

vin="LSVCY6C45LN047259"
sql="DESC ods.rtm_reissue_history"
aus=client.execute(sql)
print_in_excel(aus,'tt.xlsx')
sql="SELECT * from ods.rtm_details WHERE deviceid=='"+vin+"' "
aus=client.execute(sql)
print_in_excel(aus,vin+'pp.xlsx')



filename="C:/Users/zhanglanqing/Downloads/20200916.csv"

#散点图




#折线图




#直方图




#条形图



#箱线图


#饼图


#热力图


#蜘蛛图

#二元变量分布

#成对关系