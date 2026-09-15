import pandas as pd
import joblib
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

if not os.path.exists('models'):
    os.makedirs('models')

# Путь к нашему новому файлу
file_path = 'data/tasks_data.csv'

df = pd.read_csv(file_path)
print("Данные загружены. Колонки:", df.columns.tolist())

# 1. Обработка текста
tfidf = TfidfVectorizer(max_features=500)
X_text = tfidf.fit_transform(df['Task_Title']).toarray()

# 2. Обработка категорий
le_cat = LabelEncoder()
df['Category_Enc'] = le_cat.fit_transform(df['Category'])

# Склеиваем признаки
X = np.hstack((X_text, df[['Category_Enc']].values))

# 3. Обучаем классификатор приоритета
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X, df['Priority'])

# 4. Обучаем регрессию времени
lr = LinearRegression()
lr.fit(X, df['Actual_Duration'])

# Сохраняем всё
joblib.dump(rf, 'models/priority_model.pkl')
joblib.dump(lr, 'models/time_model.pkl')
joblib.dump(tfidf, 'models/tfidf.pkl')
joblib.dump(le_cat, 'models/le_cat.pkl')

print("УСПЕХ! Модели обучены и сохранены в папку models/")