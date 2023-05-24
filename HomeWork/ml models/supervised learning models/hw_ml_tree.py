#%%
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score
import numpy as np

ds = pd.read_csv('https://raw.githubusercontent.com/SergUSProject/IntelligentSystemsAndTechnologies/main/Practice/datasets/Davis.csv', index_col=0)

ds = ds.dropna()

# Все аналогично linearregression и classification metrics

X = ds[['sex', 'repwt']]
y = ds['height']

encoder = OneHotEncoder()
encoder.fit(X)
X = encoder.transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)


DTC = DecisionTreeClassifier() 
DTC.fit(X_train, y_train)
y_pred = DTC.predict(X_test)
df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
print(accuracy_score(y_test, y_pred))


RFC = RandomForestClassifier() 
RFC.fit(X_train, y_train)
y_pred = RFC.predict(X_test)
df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
print(accuracy_score(y_test, y_pred))

# %%
