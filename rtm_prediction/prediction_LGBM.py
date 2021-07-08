import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from en_client import en_client

client=en_client()
filepath="D:/01 RTM/rtm/rtm_prediction/data/new/"


def train_LGBM():
    
    filename=filepath+"训练样本_y.csv"
    y = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    filename=filepath+"训练样本_x.csv"
    X = pd.read_csv(filename,encoding="gbk", index_col=0, header=0)
    #index_col=0声明文件第一列为索引，header=0第一行为列名（默认就是，不必重新申明）
    print(X.columns)
    # 导入特征和label
  
    from sklearn.model_selection import train_test_split
    X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)

    import lightgbm as lgb
    from sklearn import metrics
    param = {'boosting_type':'gbdt',
                         'objective' : 'binary', #任务类型
                         'metric' : 'auc', #评估指标
                         'learning_rate' : 0.002, #学习率
                         'max_depth' : 10, #树的最大深度
                         'feature_fraction':0.8, #设置在每次迭代中使用特征的比例
                         'bagging_fraction': 0.9, #样本采样比例
                         'bagging_freq': 8, #bagging的次数
                         'lambda_l1': 0.6, #L1正则
                         'lambda_l2': 0, #L2正则
        }

    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_test_s, label=y_test_s)

    model = lgb.train(param,train_data,valid_sets=[train_data,valid_data],num_boost_round = 5000 ,early_stopping_rounds=200,verbose_eval=25)
    y_pred = model.predict(X_test_s)
    y_pred1 = [1 if x>=0.5 else 0 for x in y_pred]
    print('Light GBM 准确率:', metrics.accuracy_score(y_test_s,y_pred1))
    #test[['Attrition']].to_csv('submit_lgb.csv')

    ##计算AUC值
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
    plt.savefig(filepath+"roc_LGBM.jpg")
    plt.show()

    #验证集样本验证
    filename=filepath+"valid_data/验证样本_y.csv"
    y_valid = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    filename=filepath+"valid_data/验证样本_x.csv"
    x_valid = pd.read_csv(filename,encoding="gbk", index_col=0, header=0)
    valid_data = lgb.Dataset(x_valid, label=y_valid)
    y_pred_v = model.predict(x_valid)
    y_pred_v1 = [1 if x>=0.5 else 0 for x in y_pred_v]
    print('LGBM_smote[验证集] 准确率:', metrics.accuracy_score(y_valid,y_pred_v1))
    fpr, tpr, thresholds = roc_curve(y_valid, y_pred_v, pos_label=1)
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
    plt.savefig(filepath+"roc_LGBM(vaid).jpg")
    plt.show()

def LGBM_pre():
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

    print(ss.isnull().sum())#检查是否有空值
    print('处理后：')
    print("样本总数: {}".format(ss.shape[0]))
    print("报警个数: {}".format(ss[ss.Label == 1].shape[0]))
    print("未报警个数: {}".format(ss[ss.Label == 0].shape[0]))
    
    # 分割特征和Target
    x2=ss[['VIN','region','province']]#label特征
    x1=ss.drop(labels=['Label',"user_type",'Integrity','VIN','region','province'],axis=1)
    y=pd.DataFrame(ss['Label'])
    del ss

    #归一化
    # 最大最小值归一化 将数值映射到 [-1, 1]之间
    from sklearn.preprocessing import MinMaxScaler
    scaler=MinMaxScaler()
    scaler.fit(x1)
    X1 = pd.DataFrame(scaler.transform(x1))
    X1.columns = x1.columns
    y.columns = ['Label']
    X=pd.concat([X1, x2], axis=1)


    X.to_csv(filepath+'训练样本_x_LGBM.csv',encoding="gbk")
    y.to_csv(filepath+'训练样本_y_LGBM.csv',encoding="gbk")

def train_LGBM1():
    #'VIN','region','province'采用category特诊，不进行onehot编码
    filename=filepath+"训练样本_y_LGBM.csv"
    y = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    filename=filepath+"训练样本_x_LGBM.csv"
    X = pd.read_csv(filename,encoding="gbk", index_col=0, header=0)
    #index_col=0声明文件第一列为索引，header=0第一行为列名（默认就是，不必重新申明）
    print(X.columns)
    # 导入特征和label
    cat_cols=['VIN','region','province']
    X[cat_cols] = X[cat_cols].astype('category')
  
    from sklearn.model_selection import train_test_split
    X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)

    import lightgbm as lgb
    from sklearn import metrics
    param = {'boosting_type':'gbdt',
                         'objective' : 'binary', #任务类型
                         'metric' : 'auc', #评估指标
                         'learning_rate' : 0.002, #学习率
                         'max_depth' : 10, #树的最大深度
                         'feature_fraction':0.8, #设置在每次迭代中使用特征的比例
                         'bagging_fraction': 0.9, #样本采样比例
                         'bagging_freq': 8, #bagging的次数
                         'lambda_l1': 0.6, #L1正则
                         'lambda_l2': 0, #L2正则
        }

    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_test_s, label=y_test_s)

    model = lgb.train(param,
                    train_data,
                    valid_sets=[train_data,valid_data],
                    num_boost_round = 5000 ,
                    early_stopping_rounds=200,
                    verbose_eval=25, 
                    categorical_feature=[59,60,61])
    y_pred = model.predict(X_test_s)
    y_pred1 = [1 if x>=0.5 else 0 for x in y_pred]
    print('Light GBM 准确率:', metrics.accuracy_score(y_test_s,y_pred1))
    #test[['Attrition']].to_csv('submit_lgb.csv')


    ##计算AUC值
    '''
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
    plt.savefig(filepath+"roc_LGBM1.jpg")
    plt.show()
    '''
    
   
    importance_split = model.feature_importance(importance_type='split')
    importance_gain = model.feature_importance(importance_type='gain')
    feature_name = model.feature_name()
    feature_importance = pd.DataFrame({'feature_name':feature_name,
                                    'importance_split':importance_split,'importance_gain':importance_gain} )
    feature_importance.to_csv(filepath+'feature_importance_LGBM.csv',index=False)

def train_LGBM_smote():
    #采用 smote后的样本进行训练
    filename=filepath+"smote/训练样本_y.csv"
    y = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    filename=filepath+"smote/训练样本_x.csv"
    X = pd.read_csv(filename,encoding="gbk", index_col=0, header=0)
    #index_col=0声明文件第一列为索引，header=0第一行为列名（默认就是，不必重新申明）
    print(X.columns)
    # 导入特征和label

    from sklearn.model_selection import train_test_split
    X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)
    
    import lightgbm as lgb
    from sklearn import metrics
    param = {'boosting_type':'gbdt',
                         'objective' : 'binary', #任务类型
                         'metric' : 'auc', #评估指标
                         'learning_rate' : 0.002, #学习率
                         'max_depth' : 10, #树的最大深度
                         'feature_fraction':0.8, #设置在每次迭代中使用特征的比例
                         'bagging_fraction': 0.9, #样本采样比例
                         'bagging_freq': 8, #bagging的次数
                         'lambda_l1': 0.6, #L1正则
                         'lambda_l2': 0, #L2正则
        }

    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_test_s, label=y_test_s)

    model = lgb.train(param,train_data,valid_sets=[train_data,valid_data],num_boost_round = 5000 ,early_stopping_rounds=200,verbose_eval=25)
    y_pred = model.predict(X_test_s)
    y_pred1 = [1 if x>=0.5 else 0 for x in y_pred]
    print('Light GBM_smote 准确率:', metrics.accuracy_score(y_test_s,y_pred1))

    ##计算AUC值
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
    plt.savefig(filepath+"smote/roc_LGBM_somte.jpg")
    plt.show()

    #验证集样本验证
    filename=filepath+"valid_data/验证样本_y.csv"
    y_valid = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    filename=filepath+"valid_data/验证样本_x.csv"
    x_valid = pd.read_csv(filename,encoding="gbk", index_col=0, header=0)
    valid_data = lgb.Dataset(x_valid, label=y_valid)
    y_pred_v = model.predict(x_valid)
    y_pred_v1 = [1 if x>=0.5 else 0 for x in y_pred_v]
    print('LGBM_smote[验证集] 准确率:', metrics.accuracy_score(y_valid,y_pred_v1))
    fpr, tpr, thresholds = roc_curve(y_valid, y_pred_v, pos_label=1)
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
    plt.savefig(filepath+"smote/roc_LGBM_somte(vaid).jpg")
    plt.show()

train_LGBM()
#train_LGBM_smote()
a=1