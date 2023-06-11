# Spark RDD API - Task 2
from pyspark.sql import SparkSession
# starting spark
spark = SparkSession.builder.appName("ProductRatings").getOrCreate()
# Loading jsons
ratings_data = spark.read.json("./data/reviews_Electronics_5.json")
products_data = spark.read.json("./data/meta_Electronics.json")

combined_data = ratings_data.join(products_data, "asin")
average_ratings = combined_data.groupBy("title").avg("overall")
# RDD map
product_ratings = average_ratings.rdd.map(lambda x: (x["title"], x["avg(overall)"]))
# rating < 3 and Top 10
low_rated_products = product_ratings.filter(lambda x: x[1] < 3)
top_10_low_rated_products = low_rated_products.takeOrdered(10, key=lambda x: x[1])
# print top 10
for item in top_10_low_rated_products:
    print(item)
# Save results
low_rated_products.saveAsTextFile("./data/results")
#spark stop
spark.stop()