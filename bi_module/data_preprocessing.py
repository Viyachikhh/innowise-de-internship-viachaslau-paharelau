import sys
import os

print(f"Привет из Docker! Версия Python: {sys.version}")
print("Текущая директория:", os.getcwd())

# Проверка установки библиотек (если прописали в requirements.txt)
try:
    import pandas as pd
    print("Библиотека Pandas успешно установлена!")
except ImportError:
    print("Pandas не установлен.")