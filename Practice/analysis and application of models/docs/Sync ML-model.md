# Синхронный режим работы ML-моделей

Усовик С.В. (usovik@mirea.ru)

## Содержание:

1. Требования
2. Подготовка данных
3. Подготовка модели
4. Запуск сервиса ML-модели

В практике представлен примерная структура проекта по разработке ML-модели как сервиса. Каталог проекта разделен на три блока: 
- подготовка данных и извлечение признаков,
- построение модели,
- создание сервиса.  


## Требования

Для работы необходима установка следующего ПО:
- Python 3+
- Jupyter
- Uvicorn
- Пакет FastAPI
- Пакет Scikit-learn

## Подготовка данных

Набор данных для работы находится [здесь](../data/titanic.csv).
Блок подготовки данных и извлечения признаков содержится в директориях [data](../sync-ML-model/src/titanic/data/) и [features](../sync-ML-model/src/titanic/features/). В методе [`make_dataset`](../sync-ML-model/src/titanic/data/make_dataset.py) происходит загрузка данных.
Далее целесообразно произвести разведочный анализ данных с целью определения дальнейших действий по предварительной обработке данных и извлечению признаков. Это можно сделать в [notebook](../sync-ML-model/notebook/EDA.ipynb). Извлечение признаков при помощи метода [extract](../sync-ML-model/src/titanic/features/extract.py) удобно пронаблюдать также в notebook. Если в данных встречаются пропуски, то можно применить метод [`fill_embarked`](../sync-ML-model/src/titanic/features/fill.py).
Формирование признаков для обучения модели производится методами [`load_titanic`](../sync-ML-model/src/titanic/data/make_dataset.py) и [`train_test_split`](../sync-ML-model/src/titanic/data/validation.py).

## Подготовка модели

Обучение модели традиционно удобно осуществлять в [notebook](../sync-ML-model/notebook/Baseline.ipynb), используя для этого метод [`make_baseline_model`](../sync-ML-model/src/titanic/models/train.py). После обучния модели её следует сериализовать методами пакета [serialize.py](../sync-ML-model/src/titanic/models/serialize.py).

## Запуск сервиса ML-модели

Создание сервиса ML-модели происходит в главном пакете [main](../sync-ML-model/service/main.py). Для этого функции загрузки модели и предказания декорируются методами FastAPI. При этом целесообразно проводить предварительное [тестирование](../sync-ML-model/service/test_main.py).
Запуск сервиса осуществляется при помощи [`скрипта`](../sync-ML-model/start.sh). 


