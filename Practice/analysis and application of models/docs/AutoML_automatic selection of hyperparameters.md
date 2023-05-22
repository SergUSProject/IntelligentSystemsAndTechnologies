## AutoML (автоматический подбор гиперпараметров)

Усовик С.В. (usovik@mirea.ru)

### Содержание 

- Требования
- Подбор гиперпараметров при помощи ScikitLearn и joblib
- Подбор гиперпараметров при помощи Apache Spark
- Подбор гиперпараметров при помощи Hyperopt
- Рекомендации

### Требования

Для работы необходима установка следующего ПО:

- Jupyter
- Python 3.7+
- Spark 2+

### Подбор гиперпараметров при помощи ScikitLearn и joblib

В [notebook](../notebooks/AutoML_sklearn_joblib.ipynb) приведен пример подбора гиперпараметров при помощи возможностей фреймворка ScikitLearn. В примере решается задача выбора лучшей модели для прогнозирования цены на мобильный телефон в зависимости от его характеристик. Данные для построения модели размещены [здесь](../data/train.csv). 

В ходе решения задачи определяется пространство перебираемых гиперпараметров:

```
space = {
  "n_estimators": stats.randint(50, 150),
  "criterion": ["gini", "entropy"],
  "min_samples_leaf": stats.randint(1, 20),
  "min_samples_split": stats.uniform(0, 1)
}
```

Классификатором выступает модель случайного леса `model = RandomForestClassifier()`.

Подбор гиперпараметров производится при помощи метода `RandomizedSearchCV()`:

```
search = RandomizedSearchCV(
  estimator=model,
  param_distributions=space,
  n_iter=n_evals,
  n_jobs=1,
  cv=2,
  verbose=2
)
search.fit(X_scaled, y)
```

При помощи пакетов `joblib` и `joblibspark` возможно выполнить подбор гиперпараметров на кластере путем подключения фреймворка Spark (`register_spark()`) и определения степени параллелизма: `parallelism = 16`

```
with parallel_backend("spark", n_jobs=parallelism):
    search = RandomizedSearchCV(
        estimator=model,
        param_distributions=space,
        n_iter=n_evals,
        cv=2,
        verbose=2
    )
search.fit(X_scaled, y)
```

### Подбор гиперпараметров при помощи Apache Spark

Пример демонстрации работы методов фреймворка Spark для подбора гиперпараметров на кластере приведен в [notebook](../notebooks/AutoML_TrainTestSplit_LR.ipynb) для [набора данных](../data/sample_linear_regression_data.txt).

Первоначально задается сетка параметров для перебора гиперпараметров:

```
paramGrid = (ParamGridBuilder()
    .addGrid(lr.regParam, [0.1, 0.01]) 
    .addGrid(lr.fitIntercept, [False, True])
    .addGrid(lr.elasticNetParam, [0.0, 0.5, 1.0])
    .build())
```

В данном случае в качестве гиперпараметра используется разбивка набора данных на обучающую и тестовую для применения модели линейной регрессии с степенью параллелизма 2 :

```
tvs = TrainValidationSplit(estimator=lr,
                 estimatorParamMaps=paramGrid,
                 evaluator=RegressionEvaluator(),
                 # 80% of the data will be used for training, 20% for validation.
                 trainRatio=0.8,
                 parallelism=2)
```

Итоговая модель — это модель с комбинацией параметров которые показали себя лучше всего.

```
model.transform(test).select("features", "label", "prediction")
```

### Подбор гиперпараметров при помощи Hyperopt

Работа методов пакета Hyperopt демонстрируется для [датасета](../data/train.csv) статистики цен на мобильные телефоны на примере [notebook](../data/AutoML_Hyperopt.ipynb).

Первоначально задается сетка параметров для перебора гиперпараметров:

```
space = {
    "n_estimators": hp.choice("n_estimators", [100, 200, 300, 400,500,600]),
    "max_depth": hp.quniform("max_depth", 1, 15, 1),
    "criterion": hp.choice("criterion", ["gini", "entropy"]),
}
```

Далее происходит настройка гиперпарамметров:

```
def hyperparameter_tuning(params):
    if 'max_depth' in params.keys():
        params['max_depth'] = int(params['max_depth'])
    clf = RandomForestClassifier(**params, n_jobs=-1)
    acc = cross_val_score(clf, X_scaled, y, scoring="accuracy").mean()
    return {"loss": -acc, "status": STATUS_OK}
```

Далее происходит инициализация объекта испытания:

```
trials = Trials()

best = fmin(
    fn=hyperparameter_tuning,
    space = space, 
    algo=tpe.suggest, 
    max_evals=100, 
    trials=trials
)
```

В notebook приведены примеры использования пакета Hyperopt на кластере с использованием фреймворка Spark.



### Рекомендации
