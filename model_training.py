# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 16:26:21 2023

@author: noyha
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
from sklearn.model_selection import train_test_split,cross_val_score,KFold,cross_val_predict
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder,MaxAbsScaler, StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNetCV
from numpy import arange
from sklearn.model_selection import GridSearchCV

file_name = "output_all_students_Train_v10.xlsx"
dataframe = pd.read_excel(file_name)

from madlan_data_prep import prepare_data
DataFrame= prepare_data(dataframe)
# Find the maximum and minimum values in the column
max_valueA = DataFrame['Area'].max()
min_valueA = DataFrame['Area'].min()
max_valueN = DataFrame['room_number'].max()
min_valueN = DataFrame['room_number'].min()

# Save the values to a file
with open('values.txt', 'w') as file:
    file.write(f"Max Value: {max_valueA}\n")
    file.write(f"Min Value: {min_valueA}\n")
    file.write(f"Max Value: {max_valueN}\n")
    file.write(f"Min Value: {min_valueN}\n")


X = DataFrame.drop('price',axis=1)
y = DataFrame['price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)
category_columns = ['City','type']
numeric_columns = ['room_number','Area']

encoder = OneHotEncoder()
scaler = MinMaxScaler()

preprocessor = ColumnTransformer(
    transformers=[
        ('onehot', encoder, category_columns),
         ('scaler', scaler, numeric_columns)
     ], remainder='passthrough')

X_train_scaled = preprocessor.fit_transform(X_train)
feature_names = list(preprocessor.get_feature_names_out())
feature_names = [x.split('_')[-1] for x in feature_names]
X_train_scaled = pd.DataFrame(X_train_scaled.toarray(), columns=feature_names)
model = ElasticNet(alpha=0.005, l1_ratio=0.00001, random_state=42)
cv = KFold(n_splits=10)
scores = cross_val_score(estimator=model,
                         X=X_train_scaled,
                         y=y_train,
                         scoring='neg_mean_squared_error',
                         cv=cv)
print(scores.mean())

X_test_scaled = preprocessor.transform(X_test)
X_test_scaled = pd.DataFrame(X_test_scaled.toarray(), columns=feature_names)

model.fit(X_train_scaled, y_train)
y_pred = cross_val_predict(model, X_test_scaled, y_test, cv=10)
mse = mean_squared_error(y_test, y_pred)
print(np.sqrt(mse))

results = pd.concat([
    y_test.reset_index()['price'],
    pd.DataFrame(y_pred, columns=['pred']),
    X_test_scaled
], axis=1)


importance = permutation_importance(model, X_train_scaled, y_train, n_repeats=10, random_state=42)
feature_importances = importance.importances_mean
importance_dict = dict(zip(X_test.columns, feature_importances))
sorted_importances = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
for feature, importance in sorted_importances:
    print(f"{feature}: {importance}")

import pickle
pickle.dump(model, open("trained_model.pkl", "wb"))


