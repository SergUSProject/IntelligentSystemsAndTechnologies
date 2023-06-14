import math
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").getOrCreate()

# 3.1

import pandas as pd
columns = ['number','full_name','some_value','state', 'short_name', 'type', 'district', 'area', 'full_address', 'contact_number', 'some_value_2', 'state_2', 'latitude', 'longitude', 'point']
df = pd.read_csv('https://raw.githubusercontent.com/SergUSProject/IntelligentSystemsAndTechnologies/main/HomeWork/spark/data/places.csv', header=None, names=columns)

y_data = df[['latitude', 'longitude']]

df = spark.createDataFrame(df)
data_rdd = df.rdd

lat2 = 55.751244
lng2 = 37.618423
def Gaversinus(lat1, lng1, lat2, lng2):
  R = 6371
  lat = (lat2 - lat1) * (math.pi / 180)
  lng = (lng2 - lng1) * (math.pi / 180)
  rez = math.sin(lat / 2) * math.sin(lat / 2) + math.cos(lat1 * (math.pi / 180)) * math.cos(lat2 * (math.pi / 180)) * math.sin(lng / 2) * math.sin(lng / 2);
  d = 2 * R * math.atan2(math.sqrt(rez), math.sqrt(1-rez));
  return d

data_map_rdd = data_rdd.map(lambda x: Gaversinus(x.latitude, x.longitude, lat2, lng2))

#3.1.1

data_map_rdd.take(10)

def pair_wise(lat1, lng1):
  dists = []
  for y in y_data.values:
    dists.append(Gaversinus(lat1, lng1, y[0], y[1]))
  return dists

data_map_rdd = data_rdd.map(lambda x: pair_wise(x.latitude, x.longitude))
data_map_rdd = data_map_rdd.zipWithIndex()

data_map_rdd_indexes = data_map_rdd.flatMap(lambda x: [(x[1], w, x[0][w]) for w in range(len(x[0]))])

#3.1.2

data_map_rdd_indexes.take(20) 

data_map_rdd_indexes = data_map_rdd_indexes.filter(lambda x: x[0] != x[1])

data_rdd = data_rdd.zipWithIndex()

#3.1.3

count = 1
for d in data_map_rdd_sorted_descending.take(10):
  name1 = data_rdd.filter(lambda x: x[1] == d[0]).first()[0][1]
  name2 = data_rdd.filter(lambda x: x[1] == d[1]).first()[0][1]
  print(count, ' - ', name1, ' <-> ', name2)
  count += 1
count = 1
for d in data_map_rdd_sorted_ascending.take(10):
  name1 = data_rdd.filter(lambda x: x[1] == d[0]).first()[0][1]
  name2 = data_rdd.filter(lambda x: x[1] == d[1]).first()[0][1]
  print(count, ' - ', name1, ' <-> ', name2)
  count += 1

#3.2
import pandas as pd
import gzip
import json

def parse(path):
  g = gzip.open(path, 'rb')
  for l in g:
    yield json.loads(l)

def getDF(path):
  i = 0
  df = {}
  for d in parse(path):
    df[i] = d
    i += 1
  return pd.DataFrame.from_dict(df, orient='index')

df = getDF('Software_5.json.gz')
df = df[['overall', 'asin', 'reviewerName', 'reviewText', 'summary']]

df = df.dropna()

spark_df = spark.createDataFrame(df)
data_rdd = spark_df.rdd

from operator import add
def to_list(a):
    return [a]

def append(a, b):
    a.append(b)
    return a

def extend(a, b):
    a.extend(b)
    return a

avg_values = data_rdd.map(lambda x: (x.asin, x.overall)).combineByKey(to_list, append, extend).map(lambda x: (x[0], sum(x[1])/len(x[1])))

#3.2.1

print(mean(avg_values[1]))

#3.2.2

avg_values.take(10) 

#3.2.3

avg_values_less_3 = avg_values.filter(lambda x: x[1] < 3)
avg_values_less_3.takeOrdered(num = 10, key = lambda x: x[1]) 

#3.2.4

new_df = avg_values_less_3.toDF(["asin", "overall"])
print(new_df.show(truncate=False))

#3.3

!wget --no-check-certificate https://jmcauley.ucsd.edu/data/amazon_v2/categoryFilesSmall/Movies_and_TV_5.json.gz

import pandas as pd
import gzip
import json

def parse(path):
  g = gzip.open(path, 'rb')
  for l in g:
    yield json.loads(l)

def getDF(path):
  i = 0
  df = {}
  for d in parse(path):
    df[i] = d
    i += 1
    if i == 250000:
      break
  return pd.DataFrame.from_dict(df, orient='index')

df = getDF('Movies_and_TV_5.json.gz')
df = df[['overall', 'asin', 'reviewerName', 'reviewText', 'summary']]

df = df.dropna()

spark_df = spark.createDataFrame(df)
data_rdd = spark_df.rdd

def to_list(a):
    return [a]

def append(a, b):
    a.append(b)
    return a

def extend(a, b):
    a.extend(b)
    return a

movie_overalls = data_rdd.map(lambda x: (x.asin, x.overall)).combineByKey(to_list, append, extend)

#3.3.1

movie_overalls.first()

y_data = movie_overalls.map(lambda x: x[1]).collect()

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def cos_sims(overall):
  sims = []
  for y in y_data:
    if len(y) == len(overall):
      y = np.array(y)
      overall = np.array(overall)
      sims.append(cosine_similarity(y.reshape(1, -1), overall.reshape(1, -1)))
    else:
      sims.append(0)
  return sims

cos_sim_rdd = movie_overalls.map(lambda x: (x[0], cos_sims(x[1])))

#3.3.2

cos_sim_rdd.collect()[589] 

!wget --no-check-certificate https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_v2/metaFiles2/meta_Movies_and_TV.json.gz
import pandas as pd
import gzip
import json

def parse(path):
  g = gzip.open(path, 'rb')
  for l in g:
    yield json.loads(l)

def getDF(path):
  i = 0
  df = {}
  for d in parse(path):
    df[i] = d
    i += 1
  return pd.DataFrame.from_dict(df, orient='index')

df = getDF('meta_Movies_and_TV.json.gz')
df_titles = df[['title', 'asin']]

sp_df_titles = spark.createDataFrame(df_titles)
titles_rdd = sp_df_titles.rdd

titles_rdd = titles_rdd.map(lambda x: (x[1], x[0]))
titles_rdd.first()

#3.3.3

cos_sim_rdd_with_titles = cos_sim_rdd.join(titles_rdd)
cos_sim_rdd_with_titles.first() 

cos_sim = cos_sim_rdd_with_titles.zipWithIndex()
cos_sim.first()

cos_sim_indexes_sorted = cos_sim_indexes.sortBy(lambda x: x[2], ascending=False)
cos_sim_indexes_sorted.take(20)

top_10 = cos_sim_indexes_sorted.take(10)
count = 0

#3.3.4

for y in top_10:
  title1 = cos_sim.filter(lambda x: x[1] == y[0]).collect()[0][0][1][1]
  title2 = cos_sim.filter(lambda x: x[1] == y[1]).collect()[0][0][1][1]
  print(count, " - ", title1, " ~~~ ", title2)
  count += 1
