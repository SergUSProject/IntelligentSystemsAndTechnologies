#%%
# Датасет https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data

import os
import sys
import numpy as np
import pandas as pd

try:
    task = open('task.csv', mode='w')
except FileExistsError as e:
    print(e)
    sys.exit()
# Модифицируем немного входной файл, добавив в каждую строку id фильма, так как сейчас он относится к блоку строк
with open('./kaggle/combined_data_1.txt') as file:
    for line in file:
        line = line.strip()
        if line.endswith(':'):
            id_movie = line.replace(':', '')
        else:
            task.write(f"{id_movie},{line}\n")
task.close()
# Читаем пандой csv и берем первые 15000 строк
ds = pd.read_csv('task.csv', header=None, delimiter=',', names=['id_movie', 'id_user', 'rating', 'date'])
ds = ds.dropna()
ds = ds.head(15000)
print(ds)
# ВЫбираем уникальных пользователей и уникальные фильмы
unique_users = ds['id_user'].unique()
unique_movies = ds['id_movie'].unique()
print(unique_users)
print(unique_movies)
# Составляем матрицу в которой будет указано какие фильмы пользователь посмотрел (оценка не 0) по всем фильмам.
rate_matrix = np.zeros((len(unique_users), len(unique_movies)))

for index,item in enumerate(unique_users):
    tmp_ds = ds.loc[ds['id_user'] == item]
    number = tmp_ds.shape[0]
    for idx in range(number):
        k = list(tmp_ds['id_movie'])[idx]
        rate_matrix[index][k-1] = list(tmp_ds['rating'])[idx]

print(rate_matrix[:5])

# Используем SVD разложение
from scipy.linalg import svd 
U, s, V = svd(rate_matrix)

U = U[:2]
V = V[:2]

# Берем второго пользователя
user = rate_matrix[1]
print(user)

# по формулам  переводим пользователя в представлени сниженной размерности
lowdim = np.dot(user, V.transpose())

# Производим обратную трансформацию в исходный вектор оценок фильмов
inversed_transformation = np.dot(lowdim, V)

# вычисляем индекс непросмотренного пользователем фильма, который имеет наибольшую оценку
print("Вектор оценок пользователя 2: ", inversed_transformation)
maximum = 0
idx = 0
for index,item in enumerate(user):
    if item == 0 and inversed_transformation[index] > maximum:
        maximum = inversed_transformation[index]
        idx = index

print('Рекомендуемый фильм для пользователя 2: ', idx)

# Новый пользоватль, который посмотрел уже фильмы, но SVD разложение проводим без него
from scipy.linalg import svd 
U, s, V = svd(rate_matrix)

U = U[:3]
V = V[:3]

user = np.array((0,3,4,0,5,0,0,1))

lowdim = np.dot(user, V.transpose())
inversed_transformation = np.dot(lowdim, V)
print("Вектор оценок нового пользователя:", inversed_transformation)
maximum = 0
idx = 0
for index,item in enumerate(user):
    if item == 0 and inversed_transformation[index] > maximum:
        maximum = inversed_transformation[index]
        idx = index

print('Рекомендуемый фильм нового пользователя 2: ', idx)

os.system("rm task.csv")


# %%
