import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_script import Manager

import pandas as pd

path="D:/21python/rtm/data_visualization/f12/"


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
    df1 = pd.read_excel(path+'data/vehicle_distribution.xlsx', sheet_name = 0)
    df2 = pd.read_excel(path+'data/vehicle_distribution.xlsx', sheet_name = 1)
    col1 = df1.columns
    df_project=df2.pivot_table(index='车型', values=['车辆数目'], aggfunc=sum)

    return render_template('overview.html',col1=col1,df1=df1,df_project=df_project)

@app.route('/overview')
def over_view1():
    """
    主界面
    """
    df1 = pd.read_excel(path+'data/vehicle_distribution.xlsx', sheet_name = 0)
    df2 = pd.read_excel(path+'data/vehicle_distribution.xlsx', sheet_name = 1)
    col1 = df1.columns
    df_project=df2.pivot_table(index='车型', values=['车辆数目'], aggfunc=sum)

    return render_template('overview.html',col1=col1,df1=df1,df_project=df_project)


@app.route('/mile')
def daily_mile():
    """
    里程与能耗daily
    """
    return render_template('mile.html')

@app.route('/E_motor')
def e_motor():
    """
    里程与能耗daily
    """
    return render_template('e_motor.html')

'''
@app.route('/battery')
def battery():
    """
    电池工作情况
    """
    return render_template('battery.html')

@app.route('/Charge')
def Charge():
    """
    充电
    """
    return render_template('Charge.html')

'''
