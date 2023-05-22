import pyspark
from pyspark.sql import SparkSession
import pickle
from misc import UrlFeatureExtractor, to_array
import pandas as pd

from pyspark.sql.functions import udf
from pyspark.sql.types import FloatType, StringType




def main(sc):
    sc.addPyFile("misc.py")
    spark = SparkSession(sc)
    
    urls = spark.read.csv("path/to/malicious_phish.csv", header=True, inferSchema=True)
    with open("model.pkl", "rb") as fd:
        model = pickle.load(fd)
    
    @udf(returnType=FloatType())
    def predict_proba(url: str) -> float:
        df = pd.DataFrame(data=[url], columns=["url"])
        pred_proba = model.predict_proba(df)
        return float(pred_proba[0, 1])
    
    sample = urls.sample(fraction=0.01)
    predict_proba = sample.select("url", predict_proba("url").alias("malicious_proba"))
    predict_proba.write.csv("path/to/predict_proba.csv", header="true", mode="overwrite")
    
if __name__ == "__main__":
    main(pyspark.SparkContext(appName="batch-ml"))
