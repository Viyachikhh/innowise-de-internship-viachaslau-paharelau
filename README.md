# BIG DATA INTERNSHIP

Trainee: Viachaslau Paharelau

## Project: Alert


### Запуск проекта
---

```bash
    cd project_alert/
    docker compose up -d

```

### Структура
---
1) src - папка с модулем для обработки
2) main.py - точка запуска контейнера
3) Dockerfile, docker-compose.yaml, requirements - файлы для Docker
4) logs - папка для логов, откуда читать (и куда кидать уже обработанные)


### Как работает
---
1) При запуске контейнер читает csv-файлы из logs/source
2) Предобрабатывает, используя утитилиты из модуля src
3) Предобработанные файлы кидает в logs/tracked