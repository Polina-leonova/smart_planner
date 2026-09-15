import pandas as pd
import random

# Список примеров задач для обучения ИИ
task_templates = [
    ("Подготовить отчет по проекту", "Work", "High", 3.5),
    ("Изучить основы Python", "Education", "Medium", 2.0),
    ("Сходить в спортзал", "Health", "Low", 1.5),
    ("Купить продукты на неделю", "Personal", "Low", 1.0),
    ("Написать код для бэкенда", "Work", "High", 5.0),
    ("Прочитать книгу по ИИ", "Education", "Medium", 2.5),
    ("Записаться к врачу", "Health", "Medium", 0.5),
    ("Убраться в комнате", "Personal", "Low", 2.0),
    ("Встреча с клиентом", "Work", "High", 1.5),
    ("Подготовка к экзамену", "Education", "High", 4.0),
]

data = []
# Генерируем 1000 строк на основе шаблонов, чтобы ИИ обучился
for _ in range(1000):
    template = random.choice(task_templates)
    data.append({
        "Task_Title": template[0],
        "Category": template[1],
        "Priority": template[2],
        "Actual_Duration": template[3] + random.uniform(-0.5, 0.5) # добавляем шум
    })

df = pd.DataFrame(data)
df.to_csv('data/tasks_data.csv', index=False)
print("Новый датасет data/tasks_data.csv создан!")