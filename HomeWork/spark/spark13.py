#Spark RDD API - Task 3
from pyspark.sql import SparkSession
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.linalg.distributed import IndexedRow, IndexedRowMatrix

# spark start
spark = SparkSession.builder.appName("MovieSimilarity").getOrCreate()

# load csv
data = spark.read.csv("./data/ratings.csv", header=True)  

# To RDD format
ratings_rdd = data.rdd.map(lambda x: (int(x[0]), int(x[1]), float(x[2])))

# RDD only with film ratings
movie_ratings = ratings_rdd.map(lambda x: (x[1], x[2]))

def cosine_similarity(vec1, vec2):
    dot_product = vec1.dot(vec2)
    norm1 = vec1.norm(2)
    norm2 = vec2.norm(2)
    similarity = dot_product / (norm1 * norm2)
    return similarity

# GROUP BY ratings
movie_ratings_grouped = movie_ratings.groupByKey()

target_movie_id = 589
target_ratings = movie_ratings_grouped.filter(lambda x: x[0] == target_movie_id).flatMap(lambda x: x[1])

target_vector = Vectors.dense(target_ratings.collect())
indexed_ratings = movie_ratings_grouped.map(lambda x: IndexedRow(x[0], Vectors.dense(list(x[1]))))
indexed_ratings_matrix = IndexedRowMatrix(indexed_ratings)

similarities = indexed_ratings_matrix.rows.map(lambda x: (x.index, cosine_similarity(target_vector, Vectors.dense(x.vector.toArray()))))

# TOP 10 similar
top_similar_movies = similarities.sortBy(lambda x: -x[1]).take(10)
for movie_id, similarity in top_similar_movies:
    print(f"{target_movie_id} - {movie_id}: {similarity}")