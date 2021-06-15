import pandas as pd
import matplotlib.pyplot as plt

filepath="D:/21python/rtm/prediction_data/20190701_20200531_tiguan_30/"
filename=filepath+"训练样本.csv"
ss=pd.read_csv(filename,encoding="gbk")
# 分割特征和Target
X=ss.drop(labels=['Label',"user_type",'Integrity'],axis=1)
print(X.columns)
y=ss['Label']


from sklearn.model_selection import train_test_split
X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)


import xgboost as xgb
from sklearn import metrics
param = {'boosting_type':'gbdt',
         'objective' : 'binary:logistic', #任务类型   'regression'回归
         'eval_metric' : 'auc',
         #'eta' : 0.01,   # 如同学习率   0.001~0.01
         #'max_depth' : 7,    # 构建树的深度，越大越容易过拟合
         'colsample_bytree':1,# 列采样， 这个参数默认为1   
         'subsample': 0.9,     # 随机采样训练样本 行采样
         'subsample_freq': 1,  
         'alpha': 0.6, #正则化系数，越大越不容易过拟合
         'lambda': 1,  # 控制模型复杂度的权重值的L2 正则化项参数，参数越大，模型越不容易过拟合
         'scale_pos_weight':5 #原始数据集中，负样本（label=0)数量比上正样本（label=1)数量
        }


#train_data = xgb.DMatrix(X_train, label=y_train)
#test_data = xgb.DMatrix(X_test_s, label=y_test_s)
#model = xgb.train(param, train_data, evals=[(train_data, 'train'), (test_data, 'valid')], num_boost_round = 5000, early_stopping_rounds=20, verbose_eval=25)

from sklearn.model_selection import GridSearchCV
cv_params= {'max_depth': [5,7], 'eta': [0.01, 0.005, 0.001, 0.1]}
model = xgb.XGBClassifier(**param)
gs = GridSearchCV(model, cv_params, scoring='roc_auc', refit=True, verbose=2, cv=5, n_jobs=1)
gs.fit(X_train,y_train)
# 模型最优参数
print('模型最优参数', gs.best_params_)
print('最佳模型得分', gs.best_score_)

# 使用LGBM训练
# 使用神经网络， 64个特征 => 分类0-1

"""
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
plt.ylim([0.0, 1.0])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic example')
plt.legend(loc="lower right")
plt.show()
"""