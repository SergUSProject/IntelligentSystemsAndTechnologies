import logging
import argparse
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.regression import LinearRegression
from pyspark.ml.tuning import ParamGridBuilder, TrainValidationSplit

from pyspark.ml import Pipeline

import mlflow
from mlflow.tracking import MlflowClient


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def get_data_path(train_artifact_name):
    data_path = train_artifact_name
    return data_path


def get_pipeline():
    indexer = StringIndexer(inputCol='org', outputCol='org_idx')
    onehot = OneHotEncoder(inputCols=['org_idx'], outputCols=['org_dummy'])
    assembler = VectorAssembler(inputCols=['mile', 'org_dummy'], outputCol='features')
    regression = LinearRegression(featuresCol='features', labelCol='duration')
    
    pipeline = Pipeline(stages=[indexer, onehot, assembler, regression])
    return pipeline


def main(args):
    
    # Create Spark Session. Добавьте в название приложения оригинальное имя
    logger.info("Creating Spark Session ...")
    spark = SparkSession\
        .builder\
        .appName("Student_Name_flights_pipe_withHP")\
        .getOrCreate()

    # Load data. Исходные данные для задачи находятся по адресу 's3a://mlflow-test/data/flights-larger.csv'
    logger.info("Loading Data ...")
    train_artifact_name = args.train_artifact
    data_path = get_data_path(train_artifact_name)
    
    data = (spark.read.format('csv')
        .options(header='true', inferSchema='true')
        .load(data_path))
 

    # Prepare MLFlow experiment for logging
    client = MlflowClient()
    experiment = client.get_experiment_by_name("Spark_Experiment")
    experiment_id = experiment.experiment_id
    
    
    # Добавьте в название вашего run имя, по которому его можно будет найти в MLFlow
    run_name = 'Student_Name_flights_pipe_withHP' + ' ' + str(datetime.now())

    with mlflow.start_run(run_name=run_name, experiment_id=experiment_id):
        
        inf_pipeline = get_pipeline()

        regression = inf_pipeline.getStages()[-1]

        paramGrid = (ParamGridBuilder()
            .addGrid(regression.fitIntercept, [True, False])
            .addGrid(regression.regParam, [0.001, 0.01, 0.1, 1, 10])
            .addGrid(regression.elasticNetParam, [0, 0.25, 0.5, 0.75, 1])
            .build())

        evaluator = RegressionEvaluator(labelCol='duration')

        # By default 80% of the data will be used for training, 20% for validation.
        trainRatio = 1 - args.val_frac
        # A TrainValidationSplit requires an Estimator, a set of Estimator ParamMaps, and an Evaluator.
        tvs = TrainValidationSplit(estimator=inf_pipeline,
                            estimatorParamMaps=paramGrid,
                            evaluator=evaluator,
                            trainRatio=trainRatio,
                            parallelism=2)
        # Run TrainValidationSplit, and choose the best set of parameters.
        logger.info("Fitting new inference pipeline ...")
        model = tvs.fit(data)

        # Log params, metrics and model with MLFlow
        
        run_id = mlflow.active_run().info.run_id
        logger.info(f"Logging optimal parameters to MLflow run {run_id} ...")

        best_regParam = model.bestModel.stages[-1].getRegParam()
        best_fitIntercept = model.bestModel.stages[-1].getFitIntercept()
        best_elasticNetParam = model.bestModel.stages[-1].getElasticNetParam()

        logger.info(model.bestModel.stages[-1].explainParam('regParam'))
        logger.info(model.bestModel.stages[-1].explainParam('fitIntercept'))
        logger.info(model.bestModel.stages[-1].explainParam('elasticNetParam'))

        mlflow.log_param('optimal_regParam', best_regParam)
        mlflow.log_param('optimal_fitIntercept', best_fitIntercept)
        mlflow.log_param('optimal_elasticNetParam', best_elasticNetParam)

        logger.info("Scoring the model ...")
        predictions = model.transform(data)
        rmse = evaluator.evaluate(predictions)
        logger.info(f"Logging metrics to MLflow run {run_id} ...")
        mlflow.log_metric("rmse", rmse)
        logger.info(f"Model RMSE: {rmse}")

        logger.info("Saving pipeline ...")
        mlflow.spark.save_model(model, args.output_artifact)

        logger.info("Exporting/logging pipline ...")
        mlflow.spark.log_model(model, args.output_artifact)
        logger.info("Done")

    spark.stop()
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Model (Inference Pipeline) Training")

    #  При запуске используйте 's3a://mlflow-test/data/flights-larger.csv'
    parser.add_argument(
        "--train_artifact", 
        type=str,
        help='Fully qualified name for training artifact/dataset' 
        'Training dataset will be split into train and validation',
        required=True
    )

    parser.add_argument(
        "--val_frac",
        type=float,
        default = 0.2,
        help="Size of the validation split. Fraction of the dataset.",
    )

    # При запуске используйте оригинальное имя 'Student_Name_flights_pipe_withHP'
    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name for the output serialized model (Inference Artifact folder)",
        required=True,
    )

    args = parser.parse_args()

    main(args)

