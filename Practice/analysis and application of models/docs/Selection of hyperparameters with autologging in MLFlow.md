## Пример. Подбор гиперпараметров модели с автологгированием в MLFlow 

Усовик С.В. (usovik@mirea.ru)


### Содержание

- Требования
- Описание задачи
- Создание конвейера обработки данных
- Подготовка эксперимента для регистрации в MLFlow
- Определение сетки параметров и подбор гиперпараметров
- Логгирование параметров лучшей модели в MLFlow
- Запуск модели при помощи Spark
- Рекомендации


## Требования

Для работы необходима установка следующего ПО:

- Python 3+
- Apache Spark 2.4+
- MLFlow ([инструкция по установке](https://www.mlflow.org/docs/latest/quickstart.html))

## Описание задачи


В данном примере решается задача восстановления зависимости длительности полета самолета от набора различных параметров. Набор данных находится [здесь](../dat/flights-larger.csv). В ходе решения задачи необходимо выбрать наилучшую модель аппроксимации и сохранить ее артифакты в системе версионирования моделей MLFlow.
Исходный код проекта находится [здесь](../projects/flights_pipe_withHP_solution.py). 


## Создание конвейера обработки данных


При решении большинства задач машинного обучения приходится выполнять последовательность типовых операций. Как правило, их объединяют в конвейер преобразований. Операции в конвейере выполняются последовательно и конвейер может многократно выполнятся над исходным набором данных. В нашем примере в конвейере выполняются действия по преобразованию строк в категориальные признаки. Далее выполним кодирование этих признаков. После этого сформируем вектор признаков и подадим его на модель линейной регрессии, как наиболее часто используемой для класа задач восстановления зависимости. Соэдание конвейера осуществляется следующей функцией:

```
def get_pipeline():
    indexer = StringIndexer(inputCol='org', outputCol='org_idx')
    onehot = OneHotEncoder(inputCols=['org_idx'], outputCols=['org_dummy'])
    assembler = VectorAssembler(inputCols=['mile', 'org_dummy'], outputCol='features')
    regression = LinearRegression(featuresCol='features', labelCol='duration')
    
    pipeline = Pipeline(stages=[indexer, onehot, assembler, regression])
    return pipeline
```

## Подготовка эксперимента для регистрации в MLFlow


Для записи артефактов выбора модели необходимо провести инициализацию в MLFlow в качестве клиента, выполнив следующую последовательность команд

```
 client = MlflowClient()
 experiment = client.get_experiment_by_name("Spark_Experiment")
 experiment_id = experiment.experiment_id
 ```

Определим имя, под которым эксперимент будет зарегистрирован в MLFlow.

`run_name = 'Student_Name_flights_pipe_withHP' + ' ' + str(datetime.now())`

Автоматическое логгирование эксперимента производится в блоке операторов:

```
with mlflow.start_run(run_name=run_name, experiment_id=experiment_id):
    ...
```

## Определение сетки параметров и подбор гиперпараметров

Прежде всего необходимо определится с сеткой гиперпараметров, набор которых будет использован для подбора параметров:

```
paramGrid = (ParamGridBuilder()
            .addGrid(regression.fitIntercept, [True, False])
            .addGrid(regression.regParam, [0.001, 0.01, 0.1, 1, 10])
            .addGrid(regression.elasticNetParam, [0, 0.25, 0.5, 0.75, 1])
            .build())
```

В качестве функции подбора параметров выберем `TrainValidationSplit` с указанием уровня параллелизма, как подходящую для выполнения на Spark. Иходный код представлен ниже:

```
tvs = TrainValidationSplit(estimator=inf_pipeline,
                            estimatorParamMaps=paramGrid,
                            evaluator=evaluator,
                            trainRatio=trainRatio,
                            parallelism=2)
        # Run TrainValidationSplit, and choose the best set of parameters.
logger.info("Fitting new inference pipeline ...")
model = tvs.fit(data)
```

В результате будет параллельно производится кросс-валидация с перебором гиперпараметров из `paramGrid` 


## Логгирование параметров лучшей модели в MLFlow


В результате выполнения `model = tvs.fit(data)` будет выполнен выбор лучших параметров модели, которые можно просмотреть:

```
best_regParam = model.bestModel.stages[-1].getRegParam()
best_fitIntercept = model.bestModel.stages[-1].getFitIntercept()
best_elasticNetParam = model.bestModel.stages[-1].getElasticNetParam()
```
Эти параметры заносятся в систему версионирования MLFlow следующей последовательностью операторов:

```
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
```
## Запуск модели при помощи Spark

Перед запуском программы необходимо инициализировать Spark-сессию:

```
spark = SparkSession\
        .builder\
        .appName("Student_Name_flights_pipe_withHP")\
        .getOrCreate()
```
Для запуска приложения при помощи Spark необходимо выполнить команду 

```
spark-submit \
--jars mlflow-spark-1.27.0.jar \
flights_pipe_withHP_solution.py \
--train_artifact "path/to/flights-larger.csv" \
--output_artifact "Student_Name_flights_pipe_withHP"
```
или выполнить [скрипт](../project/flights_pipe_withHP_solution.sh)

## Рекомендации