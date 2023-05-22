spark-submit \
--jars mlflow-spark-1.27.0.jar \
flights_pipe_withHP_solution.py \
--train_artifact "s3a://mlflow-test/data/flights-larger.csv" \
--output_artifact "Student_Name_flights_pipe_withHP"