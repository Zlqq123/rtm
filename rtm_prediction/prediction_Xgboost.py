
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from en_client import en_client

client=en_client()
filepath="D:/21python/rtm/rtm_prediction/new/"




# 训练数据预处理及感知
def pre1():

    filename=filepath+'train_feature_no_warming.csv'
    s1=pd.read_csv(filename,encoding="gbk")    #s1=pd.read_csv(filename,encoding="gbk",index_col=0,header=0)
    filename=filepath+'train_feature_warming.csv'
    s2=pd.read_csv(filename,encoding="gbk")
    print(s1.shape)
    print(s2.shape)
    s1 = s1.drop(s1[s1.Integrity == 1].index)
    print(s1.shape)
    s1 = s1.drop(s1[s1.Label == 1].index)
    print(s1.shape)
    s2 = s2.drop(s2[s2.Integrity == 1].index)
    print(s2.shape)
    s2 = s2.drop(s2[s2.Label == 0].index)
    print(s2.shape)
    
    des=s1.describe()
    des.to_csv(filepath+"no_warming_f_describe.csv",encoding="gbk")
    des=s2.describe()
    des.to_csv(filepath+"warming_f_describe.csv",encoding="gbk")

    a=[2]
    a.extend(range(6,64))

    for i in a:
        plt.rcParams['font.sans-serif']=['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus']=False
        plt.style.use('ggplot')

        plt.figure(figsize=(10,5))#设置画布的尺寸
        plt.title(s1.columns[i],fontsize=14)#标题，并设定字号大小
        plt.boxplot([s1.iloc[:,i],s2.iloc[:,i]],showmeans=True, labels = ['No_warming','Warming'],sym = '*')
        #plt.show()
        plt.savefig(filepath+"pic/"+str(i)+"_"+s1.columns[i]+'.jpg')

    
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

    # corr相关系数函数
    c=X.corr()
    c.to_csv(filepath+'特征值之间的相关系数.csv',encoding="gbk")
    print(c)
    sns.heatmap(c)
    #plt.show()
    plt.savefig(filepath+"corr.jpg")

    #归一化
    # 最大最小值归一化 将数值映射到 [-1, 1]之间
    from sklearn.preprocessing import MinMaxScaler
    scaler=MinMaxScaler()
    scaler.fit(X)
    X1 = pd.DataFrame(scaler.transform(X))
    X1.columns = X.columns
    y.columns = ['Label']
    # 标准归一化
    #from sklearn.preprocessing import StandardScaler
    #scaler = StandardScaler()
    #scaler.fit(X)


    X1.to_csv(filepath+'训练样本_x.csv',encoding="gbk")
    y.to_csv(filepath+'训练样本_y.csv',encoding="gbk")

#pre1()

#@time_cost
def xgb_search_param():
    '''
    网格搜索获得最优参数：
    结果：
    模型最优参数 {'learning_rate': 0.005, 'max_depth': 6}
    最佳模型得分 0.6203925515304519
    '''

    filename=filepath+"训练样本_x.csv"
    X = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    #index_col=0声明文件第一列为索引，header=0第一行为列名（默认就是，不必重新申明）
    print(X.columns)
    # 导入特征和label
    filename=filepath+"训练样本_y.csv"
    y = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)


    from sklearn.model_selection import train_test_split
    X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)


    import xgboost as xgb
    from sklearn import metrics
    from sklearn.model_selection import GridSearchCV
    cv_params= {'max_depth': [3,4,5,6,7,8,9,10], 
                'learning_rate': [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]
                }
    model = xgb.XGBClassifier(#learning_rate=0.1,
                            n_estimators=1000,         # 树的个数--1000棵树建立xgboost
                            #max_depth=6,               # 树的深度
                            min_child_weight = 1,      # 叶子节点最小权重
                            gamma=0.,                  # 惩罚项中叶子结点个数前的参数
                            subsample=0.8,             # 随机选择80%样本建立决策树
                            #colsample_btree=0.8,       # 随机选择80%特征建立决策树
                            objective='binary:logistic ', # 指定目标函数    reg:linear (默认)回归任务  reg:logistic
                            # binary:logistic    二分类任务返回概率值  binary：logitraw   二分类任务返回类别
                            # multi：softmax  num_class=n   多分类任务返回类别   multi：softprob   num_class=n   多分类任务返回概率
                            scale_pos_weight=5,        # 解决样本个数不平衡的问题
                            random_state=27,            # 随机数
                            eval_metric = 'auc'         # 回归任务  rmse:均方根误差(默认)   mae--平均绝对误差
                            # 分类任务  error--错误率（二分类）(默认)    auc--roc曲线下面积  logloss--负对数似然函数（二分类）merror--错误率（多分类）mlogloss--负对数似然函数（多分类）
                            )
    gs = GridSearchCV(model, cv_params, scoring='roc_auc', refit=True, verbose=2, cv=5, n_jobs=1)
    gs.fit(X_train,y_train)

    # 模型最优参数
    print('模型最优参数', gs.best_params_)
    print('最佳模型得分', gs.best_score_)


def trian_xgboost():
    
    filename=filepath+"训练样本_y.csv"
    y = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    filename=filepath+"训练样本_x.csv"
    X = pd.read_csv(filename,encoding="gbk", index_col=0, header=0)
    #index_col=0声明文件第一列为索引，header=0第一行为列名（默认就是，不必重新申明）
    print(X.columns)
    # 导入特征和label
  

    from sklearn.model_selection import train_test_split
    X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)

    import xgboost as xgb
    from sklearn import metrics
    param = {'boosting_type':'gbdt',
            'objective' : 'binary:logistic', #任务类型'logistic'逻辑   'regression'回归
            'eval_metric' : 'auc',
            'eta' : 0.005,                # 如同学习率   0.001~0.01
            'max_depth' : 6,             # 构建树的深度，越大越容易过拟合
            'colsample_bytree':1,#  列采样， 这个参数默认为1
            'subsample': 0.8,    # 随机采样训练样本行采样
            'subsample_freq': 1,  
            'alpha': 0,      #正则化系数，越大越不容易过拟合
            'lambda': 1,  # 控制模型复杂度的权重值的L2 正则化项参数，参数越大，模型越不容易过拟合
            'scale_pos_weight': 5 #原始数据集中，负样本（label=0)数量比上正样本（label=1)数量
                }
    train_data = xgb.DMatrix(X_train, label=y_train)
    test_data = xgb.DMatrix(X_test_s, label=y_test_s)
    model = xgb.train(param, train_data, evals=[(train_data, 'train'), (test_data, 'valid')], num_boost_round = 5000, early_stopping_rounds=50, verbose_eval=50)
    y_pred = model.predict(test_data)
    #y_pred =[x for x in y_pred]
    y_pred1 = [1 if x>=0.5 else 0 for x in y_pred]
    #x = pd.DataFrame([y_test_s["Label"].tolist(),y_pred,y_pred1])
    #x.to_csv(filepath+"result.csv",encoding="gbk")
    #print('XGBoost 准确率:', metrics.accuracy_score(y_test_s,y_pred))
    print('XGBoost 准确率:', metrics.accuracy_score(y_test_s,y_pred1))

    
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
    plt.savefig(filepath+"roc.jpg")
    plt.show()
    

    
    #model.save_model('xgb_tiguan.model')

    ##计算feature importance

    importance = model.get_score(importance_type='gain', fmap='')
    #gain：（某特征在整个树群作为分裂节点的信息增益之和再除以某特征出现的频次）
    #print(importance)
    tuples = [(k, importance[k]) for k in importance]
    tuples = sorted(tuples, key=lambda x: x[1])
    labels, values = zip(*tuples)
    df_imp = pd.DataFrame([labels, values])
    df_imp2 = pd.DataFrame(df_imp.values.T)
    df_imp2.to_csv('imp_gain.csv')

    importance = model.get_score(importance_type='weight', fmap='')
    #weight：权重（某特征在整个树群节点中出现的次数，出现越多，价值就越高）
    tuples = [(k, importance[k]) for k in importance]
    tuples = sorted(tuples, key=lambda x: x[1])
    labels, values = zip(*tuples)
    df_imp = pd.DataFrame([labels, values])
    df_imp2 = pd.DataFrame(df_imp.values.T)
    df_imp2.to_csv('imp_weight.csv')

    importance = model.get_score(importance_type='cover', fmap='')
    #cover比较复杂，python文档未做解释，其实是指某特征节点样本的二阶导数和再除以某特征出现的 我在xgboost R API文档中找到了部分解释： https://github.com/dmlc/xgboost
    tuples = [(k, importance[k]) for k in importance]
    tuples = sorted(tuples, key=lambda x: x[1])
    labels, values = zip(*tuples)
    df_imp = pd.DataFrame([labels, values])
    df_imp2 = pd.DataFrame(df_imp.values.T)
    df_imp2.to_csv('imp_cover.csv')

    xgb.plot_importance(model,max_num_features=20,importance_type='gain')
    plt.savefig(filepath+"importance_gain.jpg")
    plt.show()

    xgb.plot_importance(model,max_num_features=20,importance_type='weight')
    plt.savefig(filepath+"importance_weight.jpg")
    plt.show()

def pre2_smote():
    filename=filepath+'smote/smote_resample.csv'
    ss = pd.read_csv(filename,encoding="gbk", index_col=0, header=0)
    print(ss.shape)
    print(ss.isnull().sum())
    print("样本个数: {}".format(ss.shape[0]))
    print("报警个数: {}".format(ss[ss.Label == 1].shape[0]))
    print("未报警个数: {}".format(ss[ss.Label == 0].shape[0]))

    #smote重采样过后的数据已经LabelEncoder以及归一化处理
    
    # 分割特征和Target
    X=ss.drop(labels=['Label'],axis=1)
    y=pd.DataFrame(ss['Label'])
    del ss
    print("特征个数: {}".format(X.shape[1]))

    y.columns = ['Label']
  
    X.to_csv(filepath+'smote/训练样本_x.csv',encoding="gbk")
    y.to_csv(filepath+'smote/训练样本_y.csv',encoding="gbk")


def xgb_search_param2():
    '''
    网格搜索获得最优参数：
    模型最优参数 {'learning_rate': 0.05, 'max_depth': 10}
    最佳模型得分 0.9399600326605366

    GridSearchCV的名字其实可以拆分为两部分，GridSearch和CV（Cross Validation），即网格搜索和交叉验证。这两个名字都非常好理解。网格搜索，搜索的是参数，即在指定的参数范围内，按步长依次调整参数，利用调整的参数训练学习器，从所有的参数中找到在验证集上精度最高的参数，这其实是一个训练和比较的过程。
    GridSearchCV可以保证在指定的参数范围内找到精度最高的参数，但是这也是网格搜索的缺陷所在，他要求遍历所有可能参数的组合，在面对大数据集和多参数的情况下，非常耗时。
    '''

    filename=filepath+"smote/训练样本_x.csv"
    X = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    #index_col=0声明文件第一列为索引，header=0第一行为列名（默认就是，不必重新申明）
    print(X.columns)
    # 导入特征和label
    filename=filepath+"smote/训练样本_y.csv"
    y = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)


    from sklearn.model_selection import train_test_split
    X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)


    import xgboost as xgb
    from sklearn import metrics
    from sklearn.model_selection import GridSearchCV
    cv_params= {'max_depth': [3,4,5,6,7,8,9,10], 
                'learning_rate': [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]
                }
    model = xgb.XGBClassifier(#learning_rate=0.1,
                            use_label_encoder=False,   #表示是否用sklearn的LabelEncoder对类别做编码，默认为True，但官方文档建议将其设为False；另外这个类的objective默认为binary:logistic，除此之外其他参数、属性和方法与xgboost.XGBRegressor相同
                            n_estimators=1000,         # 树的个数--1000棵树建立xgboost
                            #max_depth=6,               # 树的深度
                            min_child_weight = 1,      # 叶子节点最小权重
                            gamma=0.,                  # 惩罚项中叶子结点个数前的参数
                            subsample=0.8,             # 随机选择80%样本建立决策树
                            #colsample_btree=0.8,       # 随机选择80%特征建立决策树
                            objective='binary:logistic', # 指定目标函数    reg:linear (默认)回归任务  reg:logistic
                            # binary:logistic    二分类任务返回概率值  binary：logitraw   二分类任务返回类别
                            # multi：softmax  num_class=n   多分类任务返回类别   multi：softprob   num_class=n   多分类任务返回概率
                            scale_pos_weight=1,        # 解决样本个数不平衡的问题
                            random_state=27,            # 随机数
                            eval_metric = 'auc'         # 回归任务  rmse:均方根误差(默认)   mae--平均绝对误差
                            # 分类任务  error--错误率（二分类）(默认)    auc--roc曲线下面积  logloss--负对数似然函数（二分类）merror--错误率（多分类）mlogloss--负对数似然函数（多分类）
                            )
    gs = GridSearchCV(model, cv_params, scoring='roc_auc', refit=True, verbose=3, cv=5, n_jobs=1)
    #class sklearn.model_selection.GridSearchCV(estimator, param_grid, scoring=None, fit_params=None,
    # estimator：所使用的分类器，如estimator=RandomForestClassifier(min_samples_split=100,min_samples_leaf=20,max_depth=8,max_features='sqrt',random_state=10), 并且传入除需要确定最佳的参数之外的其他参数。每一个分类器都需要一个scoring参数，或者score方法。
    #n_jobs=1, iid=True, refit=True, cv=None, verbose=0, pre_dispatch=‘2*n_jobs’, error_score=’raise’, return_train_score=’warn’)
    #cv_params  dict，字典类型，放入参数搜索范围
    # n_jobs int, 并行数，int：个数,-1：跟CPU核数一致, 1:默认值
    # refit : bool,
    # cv 交叉验证参数，默认None，使用三折交叉验证。指定fold数量，默认为3，也可以是yield产生训练/测试数据的生成器。
    # verbose 日志冗长度，int：冗长度，0：不输出训练过程，1：拟合时间和参与拟合的参数数值，2：每次拟合的分数。
    # pre_dispatch=‘2*n_jobs’ 指定总共分发的并行任务数。当n_jobs大于1时，数据将在每个运行点进行复制，这可能导致OOM(Out Of Memory)，而设置pre_dispatch参数，则可以预先划分总共的job数量，使数据最多被复制pre_dispatch次
    # return_train_score  如果“False”，cv_results_属性将不包括训练分数。
    # refit :默认为True,程序将会以交叉验证训练集得到的最佳参数，重新对所有可用的训练集与开发集进行，作为最终用于性能评估的最佳模型参数。即在搜索参数结束后，用最佳参数结果再次fit一遍全部数据集。
    # iid:默认True,为True时，默认为各个样本fold概率分布一致，误差估计为所有样本之和，而非各个fold的平均。


    gs.fit(X_train,y_train.values.ravel())

    # 模型最优参数
    print('模型最优参数', gs.best_params_)
    print('最佳模型得分', gs.best_score_)
    print(gs.grid_scores_)

    '''
    grid.fit()：运行网格搜索
    grid_scores_：给出不同参数情况下的评价结果
    best_params_：描述了已取得最佳结果的参数的组合
    best_score_：成员提供优化过程期间观察到的最好的评分
    '''

'''
RandomizedSearchCV使用方法和类GridSearchCV 很相似，但他不是尝试所有可能的组合，而是通过选择每一个超参数的一个随机值的特定数量的随机组合，这个方法有两个优点：
如果你让随机搜索运行， 比如1000次，它会探索每个超参数的1000个不同的值（而不是像网格搜索那样，只搜索每个超参数的几个值）
你可以方便的通过设定搜索次数，控制超参数搜索的计算量。
RandomizedSearchCV的使用方法其实是和GridSearchCV一致的，但它以随机在参数空间中采样的方式代替了GridSearchCV对于参数的网格搜索，在对于有连续变量的参数时，RandomizedSearchCV会将其当做一个分布进行采样进行这是网格搜索做不到的，它的搜索能力取决于设定的n_iter参数，同样的给出代码。
'''

def train_xgboost2():
    filename=filepath+"smote/训练样本_y.csv"
    y = pd.read_csv(filename, encoding="gbk", index_col=0, header=0)
    filename=filepath+"smote/训练样本_x.csv"
    X = pd.read_csv(filename,encoding="gbk", index_col=0, header=0)
    #index_col=0声明文件第一列为索引，header=0第一行为列名（默认就是，不必重新申明）
    print(X.columns)
    # 导入特征和label
  

    from sklearn.model_selection import train_test_split
    X_train, X_test_s, y_train, y_test_s = train_test_split(X, y, test_size=0.2, random_state=1)

    import xgboost as xgb
    from sklearn import metrics
    param = {'boosting_type':'gbdt',
            'objective' : 'binary:logistic', #任务类型'logistic'逻辑   'regression'回归
            'eval_metric' : 'auc',
            'eta' : 0.05,                # 如同学习率   0.001~0.01
            'max_depth' : 10,             # 构建树的深度，越大越容易过拟合
            'colsample_bytree':1,#  列采样， 这个参数默认为1
            'subsample': 0.8,    # 随机采样训练样本行采样
            'subsample_freq': 1,  
            'alpha': 0,      #正则化系数，越大越不容易过拟合
            'lambda': 1,  # 控制模型复杂度的权重值的L2 正则化项参数，参数越大，模型越不容易过拟合
            #'scale_pos_weight': 5 #原始数据集中，负样本（label=0)数量比上正样本（label=1)数量
                }
    train_data = xgb.DMatrix(X_train, label=y_train)
    test_data = xgb.DMatrix(X_test_s, label=y_test_s)
    model = xgb.train(param, train_data, evals=[(train_data, 'train'), (test_data, 'valid')], num_boost_round = 5000, early_stopping_rounds=25, verbose_eval=50)
    y_pred = model.predict(test_data)
    #y_pred =[x for x in y_pred]
    y_pred1 = [1 if x>=0.5 else 0 for x in y_pred]
    #x = pd.DataFrame([y_test_s["Label"].tolist(),y_pred,y_pred1])
    #x.to_csv(filepath+"result.csv",encoding="gbk")
    #print('XGBoost 准确率:', metrics.accuracy_score(y_test_s,y_pred))
    print('XGBoost 准确率:', metrics.accuracy_score(y_test_s,y_pred1))

    
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
    plt.savefig(filepath+"smote/roc.jpg")
    plt.show()
    

    
    #model.save_model('xgb_tiguan.model')

    ##计算feature importance

    importance = model.get_score(importance_type='gain', fmap='')
    #gain：（某特征在整个树群作为分裂节点的信息增益之和再除以某特征出现的频次）
    #print(importance)
    tuples = [(k, importance[k]) for k in importance]
    tuples = sorted(tuples, key=lambda x: x[1])
    labels, values = zip(*tuples)
    df_imp = pd.DataFrame([labels, values])
    df_imp2 = pd.DataFrame(df_imp.values.T)
    df_imp2.to_csv(filepath+'smote/imp_gain.csv')

    importance = model.get_score(importance_type='weight', fmap='')
    #weight：权重（某特征在整个树群节点中出现的次数，出现越多，价值就越高）
    tuples = [(k, importance[k]) for k in importance]
    tuples = sorted(tuples, key=lambda x: x[1])
    labels, values = zip(*tuples)
    df_imp = pd.DataFrame([labels, values])
    df_imp2 = pd.DataFrame(df_imp.values.T)
    df_imp2.to_csv(filepath+'smote/imp_weight.csv')

    importance = model.get_score(importance_type='cover', fmap='')
    #cover比较复杂，python文档未做解释，其实是指某特征节点样本的二阶导数和再除以某特征出现的 我在xgboost R API文档中找到了部分解释： https://github.com/dmlc/xgboost
    tuples = [(k, importance[k]) for k in importance]
    tuples = sorted(tuples, key=lambda x: x[1])
    labels, values = zip(*tuples)
    df_imp = pd.DataFrame([labels, values])
    df_imp2 = pd.DataFrame(df_imp.values.T)
    df_imp2.to_csv(filepath+'smote/imp_cover.csv')

    xgb.plot_importance(model,max_num_features=20,importance_type='gain')
    plt.savefig(filepath+"smote/importance_gain.jpg")
    plt.show()

    xgb.plot_importance(model,max_num_features=20,importance_type='weight')
    plt.savefig(filepath+"smote/importance_weight.jpg")
    plt.show()




#pre2_smote()
#xgb_search_param2()
train_xgboost2()
a=1
