FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Оптимизация кэша: Сначала копируем только requirements.txt
# Если вы поменяете код, но не зависимости, Docker пропустит шаг установки библиотек при пересборке
COPY requirements.txt .

# COPY ./db .
# COPY ./result .
# COPY ./main.py .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]