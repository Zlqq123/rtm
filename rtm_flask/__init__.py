import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_script import Manager
from de_hist import f1

import pandas as pd

path=os.getcwd()
print(path)

# create and configure the app
app = Flask(__name__) #创建Flask 实例

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
manager = Manager(app)



@app.route('/')#创建路由
def over_view():
    """
    主界面
    """
    df1 = pd.read_excel(path+'/rtm_flask/data/vehicle_distribution.xlsx', sheet_name = 0)
    df2 = pd.read_excel(path+'/rtm_flask/data/vehicle_distribution.xlsx', sheet_name = 1)
    col1 = df1.columns
    df_project=df2.pivot_table(index='车型', values=['车辆数目'], aggfunc=sum)

    return render_template('overview.html',col1=col1,df1=df1,df_project=df_project)

@app.route('/overview')
def over_view1():
    """
    主界面
    """
    print('overview')
    df1 = pd.read_excel(path+'/rtm_flask/data/vehicle_distribution.xlsx', sheet_name = 0)
    df2 = pd.read_excel(path+'/rtm_flask/data/vehicle_distribution.xlsx', sheet_name = 1)
    col1 = df1.columns
    df_project=df2.pivot_table(index='车型', values=['车辆数目'], aggfunc=sum)

    return render_template('overview.html',col1=col1,df1=df1,df_project=df_project)

@app.route('/hist_default', methods=['GET', 'POST'])
def hist_default():
    """
    充电
    """
    df=pd.DataFrame(["",'',''])
    col=['A','B','C']
    x=range(len(col))
    
    if request.method == "POST":
        data = request.values
        pro = data['brand']
        date_range =[data['start_date'], data['end_date']]
        region = data['region']
        userType = data['user_type']
        mile_range = [data['start_mile'],data['end_mile']]
        fuc_name = data['fc_name']
        
        df = f1(pro, date_range, region, userType, mile_range,fuc_name)


        #df = pd.DataFrame([[12,13,14,15,16,17],[1,2,3,4,5,6]])
        #df.columns=['A','B','C','D','E','F']
        col=df.columns.tolist()
        x=range(len(col))

    return render_template('hist_default.html',col1=col,df1=df,x=x)


@app.route('/mile')
def daily_mile():
    """
    里程与能耗daily
    """
    return render_template('mile.html')


@app.route('/velocity')
def velocity():
    """
    里程与能耗daily
    """
    return render_template('velocity.html')

@app.route('/battery')
def battery():
    """
    电池工作情况
    """
    return render_template('battery.html')

@app.route('/E_motor')
def e_motor():
    """
    电机工作点
    """
    return render_template('e_motor.html')

@app.route('/charge_overview')
def charge_overview():
    """
    充电
    """
    return render_template('charge_overview.html')

'''
@app.route('/mile')
def daily_mile():
    """
    里程与能耗daily
    """
    df1=pd.read_excel(path+'data/mile.xlsx', sheet_name='consumption')
    columns1 = df1.columns.tolist()
    index1 = df1.index.tolist()
    print(columns1)
    columns1.pop(0)
    print(columns1)
    result1 = []
    data_max1 = 0
    for column in columns1:
        temp = {}
        temp['name'] = column
        temp['type'] = 'bar'
        temp['data'] = df1[column].values.tolist()
        #print('temp=', temp)
        if max(temp['data']) > data_max1:
            data_max1 = max(temp['data'])
        result1.append(temp)
    #print(result)
    return render_template('mile.html', data=result1, columns=columns1, index=index1, data_max=data_max1)
'''





@app.route('/ir')
def ir():
    """
    充电
    """
    return render_template('ir.html')


@app.route('/charge_soc')
def charge_soc():
    """
    充电
    """
    return render_template('charge_soc.html')

@app.route('/charge_time')
def charge_time():
    """
    充电
    """
    return render_template('charge_time.html')

@app.route('/charge_temp')
def charge_temp():
    """
    充电
    """
    return render_template('charge_temp.html')

@app.route('/charge_power')
def charge_power():
    """
    充电
    """
    return render_template('charge_power.html')

@app.route('/get_data')
def get_data():
    return 'hhhhh'

@app.route('/rtm_warm')
def warm_hist():
    """
    充电
    """
    return render_template('warm_hist.html')



@app.route('/warming_pre')
def warming_pre():
    """
    充电
    """
    return render_template('warm_prediction.html')