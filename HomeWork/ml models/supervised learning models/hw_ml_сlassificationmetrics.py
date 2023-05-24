#%%
from sklearn.datasets import make_classification
import matplotlib.pyplot as plt

X, y = make_classification(
    n_samples = 1000,
    n_features = 2,
    n_informative = 2,
    n_redundant = 0,
    n_repeated = 0,
    n_classes = 2,
    n_clusters_per_class = 1,
    weights = (0.15, 0.85),
    class_sep = 6.0,
    hypercube = False,
    random_state = 2,
)
#%%
# Разделяем на обучающую и тестовую в соотношении 80/20
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

#%%
# Распределение выборки по классам:
fig, axs = plt.subplots(1, 2)
axs[0].pie([list(y).count(1), list(y).count(0)], labels=['1', '0'])
axs[0].set_title('Classes in dataset')
plt.show()
#%%
# Скейлинг, оно же масштабирование
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# %%
# Метод K ближайших соседей
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import mean_absolute_error, precision_recall_curve
from sklearn.metrics import average_precision_score, roc_curve, roc_auc_score
classifier = KNeighborsClassifier()
classifier.fit(X_train, y_train)
y_pred = classifier.predict(X_test)

print(classification_report(y_test, y_pred))
print('Доля верных ответов для KNN:', 1 - mean_absolute_error(y_test, y_pred))
print("Confusion matrix для KNN:")
print(confusion_matrix(y_test, y_pred))

precision, recall, thresholds = precision_recall_curve(y_test, y_pred)
fig, ax = plt.subplots()
ax.plot(recall, precision, color='blue')
ax.set_title('PR кривая для KNN')
ax.set_ylabel('Precision')
ax.set_xlabel('Recall')
ax.legend({average_precision_score(y_test, y_pred):'Average precision'},
          title = 'Average precision')
plt.show() 

fpr, tpr, _ = roc_curve (y_test, y_pred)
plt.plot(fpr,tpr)
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.legend({roc_auc_score(y_test, y_pred) : 'ROC AUC'}, title = 'ROC AUC')
plt.show() 
#%%
# Логистическая регрессия
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import mean_absolute_error, precision_recall_curve
from sklearn.metrics import average_precision_score, roc_curve, roc_auc_score

model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print('Доля верных ответов для логистической регрессии:', 1 - mean_absolute_error(y_test, y_pred))
print("Confusion matrix для логистической регрессии:")
print(confusion_matrix(y_test, y_pred))

precision, recall, thresholds = precision_recall_curve(y_test, y_pred)
fig, ax = plt.subplots()
ax.plot(recall, precision, color='blue')
ax.set_title('PR кривая для логистической регрессии')
ax.set_ylabel('Precision')
ax.set_xlabel('Recall')
ax.legend({average_precision_score(y_test, y_pred):'Average precision'},
          title = 'Average precision')
plt.show() 

fpr, tpr, _ = roc_curve (y_test, y_pred)
plt.plot(fpr,tpr)
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.legend({roc_auc_score(y_test, y_pred) : 'ROC AUC'}, title = 'ROC AUC')
plt.show() 
# %%
