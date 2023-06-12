#
#Original file is located at
#    https://colab.research.google.com/drive/17OOPWX0-txZoqtyfvWqyLnQGKQE22RNg
#

import numpy as np
from scipy.linalg import svd as sci
user_movie_matrix = np.array(((3,2,1,4,5), (2,2,5,5,1), (0,5,3,0,1), (2,3,5,1,2), (5,1,5,3,1), (3,0,0,1,2), (1,3,4,2,0)))
for i in user_movie_matrix: 
  print(i)

U, s, V = sci(user_movie_matrix)
print("Matrix U: ")
for i in U: 
  print(i)
print("Matrix s: ")
print(s)
print("Matrix V: ")
for i in V: 
  print(i)
U = U[:2]
V = V[:2] 
print("Matrix U: ")
for i in U: 
  print(i)
print("Matrix V: ")
for i in V: 
  print(i)
user_2 = user_movie_matrix[1]
print("user_2: ", user_2)
low = np.dot(user_2, V.transpose())
print("Lower Dimmension:", low)
inversed_transformation = np.dot(low, V)
print("Mark vector 2:", inversed_transformation)
print("Index:", np.argmax(inversed_transformation))
U, s, V = sci(user_movie_matrix)
U = U[:3]
V = V[:3]
new_user = np.array((0,0,3,4,0))
print("New user:", new_user)
low = np.dot(new_user, V.transpose())
print("new_user lower dimmension:", low)
inversed_transformation = np.dot(low, V) 
print("Mark vector new_user:", inversed_transformation) 
max = 0
for i in range(len(new_user)): 
  if new_user[i] == 0 and inversed_transformation[i] > max:
    max = inversed_transformation[i]
    max_i = i 
print("Index film unwatched:", max_i)
