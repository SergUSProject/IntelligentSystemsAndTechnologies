from pyspark.sql import SparkSession, functions, types
import pandas as pd
import geopandas as gpd
import numpy as np
import json
import plotly
import math
from datetime import datetime
import folium
import folium.plugins as plugins

def Gaversinus(lat1, lng1, lat2, lng2): 
  R = 6371 
  lat = (lat2 - lat1) * (math.pi / 180)
  lng = (lng2 - lng1) * (math.pi / 180)
  rez = math.sin(lat / 2) * math.sin(lat / 2) + math.cos(lat1 * (math.pi / 180)) * math.cos(lat2 * (math.pi / 180)) * math.sin(lng / 2) * math.sin(lng / 2)
  d = 2 * R * math.atan2(math.sqrt(rez), math.sqrt(1-rez))
  return d 

def translate(mapping):
    def translate_(col):
        return mapping.get(col)
    return functions.udf(translate_, types.StringType())

spark = SparkSession.builder.master("local[*]").getOrCreate()

df = pd.read_csv('./data/201902-citibike-tripdata.csv')
spark_df = spark.createDataFrame(df)
# ended rides for every station
spark_df.groupBy("end station id").count().sort("count", ascending=False).show()
gdf = gpd.read_file('./data/NYC Taxi Zones.geojson')
gdf["longitude"] = gdf["geometry"].centroid.x
gdf["latitude"] = gdf["geometry"].centroid.y
spark_gdf = spark.createDataFrame(gdf[['location_id', 'zone', 'borough', 'longitude', 'latitude']])
spark_gdf.count()

station_names = set(np.concatenate((df['start station name'].unique(), df['end station name'].unique())))

station_dict = dict.fromkeys(station_names, '')

def find_zone(lon1, lat1): 
  df_closest = spark_gdf[['zone', 'longitude', 'latitude']]
  row = df_closest.withColumn("difference", functions.abs(functions.col('longitude') - lon1) + functions.abs(functions.col('latitude') - lat1)).sort("difference", ascending=False).first()
  return row.zone

for name in station_names: 
  start = spark_df.filter(spark_df["start station name"]==name).first()
  if start: 
    station_dict[name] = find_zone(start[6], start[5])
  else: 
    end = spark_df.filter(spark_df["end station name"]==name).first()
    station_dict[name] = find_zone(end[10], end[9])
print(station_dict)

with open("stations_zones.json", "w") as outfile:
    json.dump(station_dict, outfile)

spark_df = spark_df.withColumn("start zone", translate(station_dict)("start station name"))
spark_df.show(truncate = False)

spark_df = spark_df.withColumn("end zone", translate(station_dict)("end station name"))
spark_df.show(truncate = False)
#count rides for every zone
spark_df.groupBy("start zone").count().sort("count", ascending=False).show() 
#count end rides for every zone
spark_df.groupBy("end zone").count().sort("count", ascending=False).show() 

df_end_zones = spark_df.groupBy("end zone").count().sort("count", ascending=False).toPandas().dropna()

latitudes = []
longitudes = []
for zones in df_end_zones['end zone']:
  latitudes.append(spark_gdf.filter(functions.col("zone")==zones).first().latitude) 
  longitudes.append(spark_gdf.filter(functions.col("zone")==zones).first().longitude) 
df_end_zones['latitude'] = latitudes 
df_end_zones['longitude'] = longitudes 
df_end_zones.head()


data1 = [dict(type='scattergeo', lat = df_end_zones["latitude"], lon = df_end_zones["longitude"], marker = dict(size = 9, autocolorscale=False, colorscale = 'Viridis', color = df_end_zones['count'], colorbar = dict(title='Amount')) )]
layout1 = dict(title='Number of arrivals to zones',geo = dict(scope='usa',projection = dict(type ='albers usa'),showland = True,landcolor="rgb(250,250,250)",subunitcolor = "rgb(217,217,217)",countrycolor = "rgb(217,217,217)",countrywidth =0.5, subunitwidth=0.5))
plotly.offline.iplot({
    "data": data1,
    "layout": layout1
})

calc_dist_udf = functions.udf(Gaversinus, types.DoubleType())
spark_df_with_dists = spark_df.filter(functions.col("start station name") != functions.col("end station name")).withColumn('gs_dist', calc_dist_udf(functions.col("start station latitude"), functions.col("start station longitude"), functions.col("end station latitude"), functions.col("end station longitude")))
spark_df_with_dists.show()

spark_df_with_dists.agg(functions.min('gs_dist').alias("Минимальное расстояние"), functions.max('gs_dist').alias("Максимальное расстояние"), functions.avg('gs_dist').alias("Среднее расстояние"), functions.median('gs_dist').alias("Медиана"), functions.stddev_pop('gs_dist').alias("Стандартное отклонение")).show()

spark_df.withColumn("startday", functions.date_format("starttime", "yyyy-MM-dd")).groupBy("start station name", "startday").count().groupBy("start station name").avg("count").show()

spark_df.withColumn("endday", functions.date_format("stoptime", "yyyy-MM-dd")).groupBy("end station name", "endday").count().groupBy("end station name").avg("count").show()

start_morning_spark_df = spark_df.withColumn("starttimet", functions.date_format("starttime", 'HH:mm:ss')).filter(functions.col("starttimet") >= "06:00:00").filter(functions.col("starttimet") <= "11:59:00").groupBy("start station name").count().groupBy("start station name").avg("count")

start_morning_spark_df.show()

end_morning_spark_df = spark_df.withColumn("stoptimet", functions.date_format("stoptime", 'HH:mm:ss')).filter(functions.col("stoptimet") >= "06:00:00").filter(functions.col("stoptimet") <= "11:59:00").groupBy("end station name").count().groupBy("end station name").avg("count")

end_morning_spark_df.show()

start_day_spark_df = spark_df.withColumn("starttimet", functions.date_format("starttime", 'HH:mm:ss')).filter(functions.col("starttimet") >= "12:00:00").filter(functions.col("starttimet") <= "17:59:00").groupBy("start station name").count().groupBy("start station name").avg("count")

start_day_spark_df.show()

end_day_spark_df = spark_df.withColumn("stoptimet", functions.date_format("stoptime", 'HH:mm:ss')).filter(functions.col("stoptimet") >= "12:00:00").filter(functions.col("stoptimet") <= "17:59:00").groupBy("end station name").count().groupBy("end station name").avg("count")

end_day_spark_df.show()

start_evening_spark_df = spark_df.withColumn("starttimet", functions.date_format("starttime", 'HH:mm:ss')).filter(functions.col("starttimet") >= "18:00:00").filter(functions.col("starttimet") <= "23:59:00").groupBy("start station name").count().groupBy("start station name").avg("count")

start_evening_spark_df.show()

end_evening_spark_df = spark_df.withColumn("stoptimet", functions.date_format("stoptime", 'HH:mm:ss')).filter(functions.col("stoptimet") >= "18:00:00").filter(functions.col("stoptimet") <= "23:59:00").groupBy("end station name").count().groupBy("end station name").avg("count")

end_evening_spark_df.show()

start_night_spark_df = spark_df.withColumn("starttimet", functions.date_format("starttime", 'HH:mm:ss')).filter(functions.col("starttimet") >= "00:00:00").filter(functions.col("starttimet") <= "05:59:00").groupBy("start station name").count().groupBy("start station name").avg("count")

start_night_spark_df.show()

end_night_spark_df = spark_df.withColumn("stoptimet", functions.date_format("stoptime", 'HH:mm:ss')).filter(functions.col("stoptimet") >= "00:00:00").filter(functions.col("stoptimet") <= "05:59:00").groupBy("end station name").count().groupBy("end station name").avg("count")

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

m = folium.Map([48., 5.], tiles='stamentoner', zoom_start=6)

hm = plugins.HeatMapWithTime(
    data,
    index=time_index,
    auto_play=True,
    max_opacity=0.3
)

hm.add_to(m)