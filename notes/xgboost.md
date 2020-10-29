xgboost.train()和xgboost.XGBClassifier().fit()的区别

# 1
xgm = xgb.XGBClassifier()
xgm.fit(X_train, y_train)   
y_pred = xgm.predict(X_train)  

# 2
param = {'max_depth':2, 'eta':1, 'silent':1, 'objective':'binary:logistic' }
num_round = 2
bst = xgb.train(param, dtrain, num_round)
preds = bst.predict(dtest)