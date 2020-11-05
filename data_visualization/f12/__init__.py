import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_script import Manager

import pandas as pd

def create_app(test_config=None):
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
        return render_template('overview.html')

    @app.route('/mile')
    def mileage():
        """
        里程与能耗
        """
        return render_template('mileage.html')

    @app.route('/velocity')
    def velocity():
        """
        速度
        """
        return render_template('velocity.html')

    @app.route('/e_motor')
    def e_motor():
        """
        电机
        """
        return render_template('e_motor.html')

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

    return app

