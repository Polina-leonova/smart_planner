import joblib
import numpy as np
import os

# Пути к моделям
MODEL_DIR = "models"

def predict_task_params(title, category):
    try:
        # Загружаем модели
        rf = joblib.load(os.path.join(MODEL_DIR, 'priority_model.pkl'))
        lr = joblib.load(os.path.join(MODEL_DIR, 'time_model.pkl'))
        tfidf = joblib.load(os.path.join(MODEL_DIR, 'tfidf.pkl'))
        le_cat = joblib.load(os.path.join(MODEL_DIR, 'le_cat.pkl'))

        # 1. Текст -> Вектор
        text_vec = tfidf.transform([title]).toarray()
        
        # 2. Категория -> Число
        try:
            cat_enc = le_cat.transform([category])[0]
        except:
            cat_enc = 0
            
        # Собираем данные для подачи в модели
        features = np.hstack((text_vec, [[cat_enc]]))
        
        # 3. Предсказания
        priority = rf.predict(features)[0]
        time_pred = round(float(abs(lr.predict(features)[0])), 1)
        
        return priority, time_pred
    except Exception as e:
        print(f"Ошибка ИИ: {e}")
        return "Medium", 1.0 # Заглушка на случай ошибки