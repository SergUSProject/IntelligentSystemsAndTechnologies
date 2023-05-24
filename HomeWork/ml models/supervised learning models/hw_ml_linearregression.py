#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# Подгружаем датасет и задаем в качестве целевой переменной рост, а признаком - вес
ds = pd.read_csv('https://raw.githubusercontent.com/sdukshis/ml-intro/master/datasets/Davis.csv', index_col=0)
print(ds.head())

from sklearn.linear_model import LinearRegression

X = ds[['weight']]
y = ds['height']
X.dropna()
# %%
# Разделяем выборку на обучающую и тестовую в соотношении 80/20
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

#%%
# Обучаем и предсказываем)
regr = LinearRegression()
regr.fit(X_train, y_train)
y_pred = regr.predict(X_test)
# Выводим ошибку и прямую регрессии
df = pd.DataFrame({'Предполагаемо': y_test, 'Результат модели': y_pred})
print(df.head())
from sklearn.metrics import mean_squared_error
print('Среднеквадратичная ошибка:', np.sqrt(mean_squared_error(y_test, y_pred)))

plt.plot(X_test, y_pred, color='red')
plt.title('Вес и рост')
plt.xlabel('Вес')
plt.ylabel('Рост')
plt.scatter(X_test, y_test)
# %%
# Расширим пространство признаков
X = ds[['weight','sex', 'repwt']]
y = ds['height']
X.dropna()
# Так как столбец sex содержит символы, а не числа, стоит воспользоваться энкодером. Судя по статье (https://habr.com/ru/articles/456294/)
# OneHotEncoder выглядит получше чем LabelEncoder
from sklearn.preprocessing import OneHotEncoder
encoder = OneHotEncoder()
encoder.fit(X)
X_enc = encoder.transform(X)

# Разделим выборку по новой, так как данные мы поменяли)
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X_enc, y, test_size=0.20)

# Повторим этапы обучения, проверки и вычисления ошибки уже с новыми данными
regr = LinearRegression()
regr.fit(X_train, y_train)
y_pred = regr.predict(X_test)
df = pd.DataFrame({'Предполагаемо': y_test, 'Результат модели': y_pred})
print(df.head())
from sklearn.metrics import mean_squared_error
print('Среднеквадратичная ошибка:', np.sqrt(mean_squared_error(y_test, y_pred)))

# В результате видно, что ошибка увеличилась. Скорее всего повлияло добавление новых признаков.
# Меньше всего ошибка вышла при использовании только признаков sex и repwt (уменьшение ошибки на 0.5)

# %%
