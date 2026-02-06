# BIG DATA INTERNSHIP

Trainee: Viachaslau Paharelau

## Project: Alert


### Запуск проекта
---
1) Через Docker-compose:
```bash
    cd project_alert/
    docker compose up -d

```
2) Через kubernetes(для локальной проверки kubernetes - использовать локально установленный minikube):
```bash
    make # подождать 2 минуты, т.к. pod перезапускается каждые две минуты
    make test-run # если хотите тестовый раз запустить
```
   
---
### Структура
---
1) src - папка с модулем для обработки
2) main.py - точка запуска контейнера
3) Dockerfile, docker-compose.yaml, requirements - файлы для Docker
4) logs - папка для логов, откуда читать (и куда кидать уже обработанные)
5) kuber-manifests - папка для kubernetes-манифестов

---
### Как работает
---
1) При запуске контейнер читает csv-файлы из logs/source
2) Предобрабатывает, используя утитилиты из модуля src
3) Предобработанные файлы кидает в logs/tracked