from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").getOrCreate()
spark

sc = spark.sparkContext

#3.2

!wget https://s3.amazonaws.com/tripdata/201902-citibike-tripdata.csv.zip
!unzip 201902-citibike-tripdata.csv.zip

#3.2.1

import pandas as pd
df = pd.read_csv('201902-citibike-tripdata.csv')
df.head()

spark_df = spark.createDataFrame(df)
print(spark_df.printSchema())
print(spark_df.show(truncate=False))

spark_df.groupBy("start s").count().sort("count", ascending=False).show()

spark_df.groupBy("end ").count().sort("count", ascending=False).show() 
!pip install geopandas
import geopandas as gpd
df1 = gpd.read_file("NYC Taxi Zones.geojson")
df1.head()

df1["longitude"] = df1["geometry"].centroid.x
df1["latitude"] = df1["geometry"].centroid.y
df1.head()

spark_df1 = spark.createDataFrame(df1[['location_id', 'zone', 'borough', 'longitude', 'latitude']])
print(spark_df1.printSchema())
print(spark_df1.show(truncate=False))

spark_df1.count()

import numpy as np
station_names = set(np.concatenate((df['start station name'].unique(), df['end station name'].unique())))

station_dict = dict.fromkeys(station_names, '')
print(station_dict)

from pyspark.sql import functions as F
def find_zone(lon1, lat1):
  df_closest = spark_df1[['zone', 'longitude', 'latitude']]
  row = df_closest.withColumn("difference", F.abs(F.col('longitude') - lon1) + F.abs(F.col('latitude') - lat1)).sort("difference", ascending=False).first()
  return row.zone

for name in station_names:
  start = spark_df.filter(spark_df["start station name"]==name).first()
  if start:
    station_dict[name] = find_zone(start[6], start[5])
  else:
    end = spark_df.filter(spark_df["end station name"]==name).first()
    station_dict[name] = find_zone(end[10], end[9])
print(station_dict)

import json
with open("stations_zones.json", "w") as outfile:
    json.dump(station_dict, outfile)

from pyspark.sql.types import StringType
from pyspark.sql.functions import udf

def translate(mapping):
    def translate_(col):
        return mapping.get(col)
    return udf(translate_, StringType())
spark_df = spark_df.withColumn("start zone", translate(station_dict)("start station name"))
spark_df.show(truncate = False)

spark_df = spark_df.withColumn("end zone", translate(station_dict)("end station name"))
spark_df.show(truncate = False)

spark_df.groupBy("start ").count().sort("count", ascending=False).show() 

spark_df.groupBy("end ").count().sort("count", ascending=False).show() 

!pip install plotly-express

df_end_zones = spark_df.groupBy("end ").count().sort("count", ascending=False).toPandas().dropna()

latitudes = []
longitudes = []
for zones in df_end_zones['end zone']:
  latitudes.append(spark_df1.filter(F.col("zone")==zones).first().latitude)
  longitudes.append(spark_df1.filter(F.col("zone")==zones).first().longitude)
df_end_zones['latitude'] = latitudes
df_end_zones['longitude'] = longitudes
df_end_zones.head()

import plotly
data1 = [dict(type='scattergeo', \
              lat = df_end_zones["latitude"], \
              lon = df_end_zones["longitude"], \
              marker = dict(size = 9, autocolorscale=False, colorscale = 'Viridis', color = df_end_zones['count'], colorbar = dict(title='Amount')) \
              )]
layout1 = dict(title='Number of arrivals to zones',
              geo = dict(scope='usa',projection = dict(type ='albers usa'),showland = True,
                    landcolor="rgb(250,250,250)",subunitcolor = "rgb(217,217,217)",
                    countrycolor = "rgb(217,217,217)",countrywidth =0.5, subunitwidth=0.5))
plotly.offline.iplot({
    "data": data1,
    "layout": layout1
})

#3.2.2

import math
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType
def Gaversinus(lat1, lng1, lat2, lng2):
  R = 6371
  lat = (lat2 - lat1) * (math.pi / 180)
  lng = (lng2 - lng1) * (math.pi / 180)
  rez = math.sin(lat / 2) * math.sin(lat / 2) + math.cos(lat1 * (math.pi / 180)) * math.cos(lat2 * (math.pi / 180)) * math.sin(lng / 2) * math.sin(lng / 2);
  d = 2 * R * math.atan2(math.sqrt(rez), math.sqrt(1-rez));
  return d

calc_dist_udf = F.udf(Gaversinus, DoubleType())
spark_df_with_dists = spark_df.filter(F.col("start station name") != F.col("end station name")).withColumn('gs_dist', calc_dist_udf(F.col("start station latitude"), F.col("start station longitude"), F.col("end station latitude"), F.col("end station longitude")))
spark_df_with_dists.show()

spark_df_with_dists.agg(F.min('gs_dist').alias("min_range"), F.max('gs_dist').alias("Мmax_range"), F.avg('gs_dist').alias("Среднее расстояние"), F.median('gs_dist').alias("Медиана"), F.stddev_pop('gs_dist').alias("Стандартное отклонение")).show()

#3.2.3

from pyspark.sql.functions import date_format
spark_df.withColumn("startday", date_format("starttime", "yyyy-MM-dd"))\
.groupBy("start station name", "startday")\
.count()\
.groupBy("start station name")\
.avg("count")\
.show()

spark_df.withColumn("endday", date_format("stoptime", "yyyy-MM-dd"))\
.groupBy("end station name", "endday")\
.count()\
.groupBy("end station name")\
.avg("count")\
.show()

from pyspark.sql import functions as F
start_morning_spark_df = spark_df.withColumn("starttimet", date_format("starttime", 'HH:mm:ss'))\
.filter(F.col("starttimet") >= "06:00:00")\
.filter(F.col("starttimet") <= "11:59:00")\
.groupBy("start station name")\
.count()\
.groupBy("start station name")\
.avg("count")

start_morning_spark_df.show()

from pyspark.sql.functions import date_format
from pyspark.sql import functions as F
end_morning_spark_df = spark_df.withColumn("stoptimet", date_format("stoptime", 'HH:mm:ss'))\
.filter(F.col("stoptimet") >= "06:00:00")\
.filter(F.col("stoptimet") <= "11:59:00")\
.groupBy("end station name")\
.count()\
.groupBy("end station name")\
.avg("count")

end_morning_spark_df.show()

from pyspark.sql import functions as F
start_day_spark_df = spark_df.withColumn("starttimet", date_format("starttime", 'HH:mm:ss'))\
.filter(F.col("starttimet") >= "12:00:00")\
.filter(F.col("starttimet") <= "17:59:00")\
.groupBy("start station name")\
.count()\
.groupBy("start station name")\
.avg("count")

start_day_spark_df.show()

from pyspark.sql.functions import date_format
from pyspark.sql import functions as F
end_day_spark_df = spark_df.withColumn("stoptimet", date_format("stoptime", 'HH:mm:ss'))\
.filter(F.col("stoptimet") >= "12:00:00")\
.filter(F.col("stoptimet") <= "17:59:00")\
.groupBy("end station name")\
.count()\
.groupBy("end station name")\
.avg("count")

end_day_spark_df.show()

from pyspark.sql import functions as F
start_evening_spark_df = spark_df.withColumn("starttimet", date_format("starttime", 'HH:mm:ss'))\
.filter(F.col("starttimet") >= "18:00:00")\
.filter(F.col("starttimet") <= "23:59:00")\
.groupBy("start station name")\
.count()\
.groupBy("start station name")\
.avg("count")

start_evening_spark_df.show()

from pyspark.sql.functions import date_format
from pyspark.sql import functions as F
end_evening_spark_df = spark_df.withColumn("stoptimet", date_format("stoptime", 'HH:mm:ss'))\
.filter(F.col("stoptimet") >= "18:00:00")\
.filter(F.col("stoptimet") <= "23:59:00")\
.groupBy("end station name")\
.count()\
.groupBy("end station name")\
.avg("count")

end_evening_spark_df.show()

from pyspark.sql import functions as F
start_night_spark_df = spark_df.withColumn("starttimet", date_format("starttime", 'HH:mm:ss'))\
.filter(F.col("starttimet") >= "00:00:00")\
.filter(F.col("starttimet") <= "05:59:00")\
.groupBy("start station name")\
.count()\
.groupBy("start station name")\
.avg("count")

start_night_spark_df.show()

from pyspark.sql.functions import date_format
from pyspark.sql import functions as F
end_night_spark_df = spark_df.withColumn("stoptimet", date_format("stoptime", 'HH:mm:ss'))\
.filter(F.col("stoptimet") >= "00:00:00")\
.filter(F.col("stoptimet") <= "05:59:00")\
.groupBy("end station name")\
.count()\
.groupBy("end station name")\
.avg("count")

end_night_spark_df.show()

data_start_day = start_day_spark_df.select("avg(count)").collect()
data_start_day = [l[0] for l in data_start_day]
data_start_morning = start_morning_spark_df.select("avg(count)").collect()
data_start_morning = [l[0] for l in data_start_morning]
data_start_evening = start_evening_spark_df.select("avg(count)").collect()
data_start_evening = [l[0] for l in data_start_evening]
data_start_night = start_night_spark_df.select("avg(count)").collect()
data_start_night = [l[0] for l in data_start_night]
data_end_day = end_day_spark_df.select("avg(count)").collect()
data_end_day = [l[0] for l in data_end_day]
data_end_morning = end_morning_spark_df.select("avg(count)").collect()
data_end_morning = [l[0] for l in data_end_morning]
data_end_evening = end_evening_spark_df.select("avg(count)").collect()
data_end_evening = [l[0] for l in data_end_evening]
data_end_night = end_night_spark_df.select("avg(count)").collect()
data_end_night = [l[0] for l in data_end_night]

from datetime import datetime
time_index = [
    datetime.strptime("06:00:00", '%H:%M:%S').time() for k in range(len(data_start_morning) + len(data_end_morning))
] + \
[
    datetime.strptime("12:00:00", '%H:%M:%S').time() for k in range(len(data_start_day) + len(data_end_day))
] + \
[
    datetime.strptime("18:00:00", '%H:%M:%S').time() for k in range(len(data_start_evening) + len(data_end_evening))
] + \
[
    datetime.strptime("00:00:00", '%H:%M:%S').time() for k in range(len(data_start_night) + len(data_end_night))
]
data = data_start_morning + data_end_morning + data_start_day + data_end_day + data_start_evening + data_end_evening + data_start_night + data_end_night

import folium
import folium.plugins as plugins
m = folium.Map([48., 5.], tiles='stamentoner', zoom_start=6)

hm = plugins.HeatMapWithTime(
    data,
    index=time_index,
    auto_play=True,
    max_opacity=0.3
)

hm.add_to(m)

m
