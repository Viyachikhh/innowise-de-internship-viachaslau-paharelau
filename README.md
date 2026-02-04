# BIG DATA INTERNSHIP

Intern: Viachaslau Paharelau

## Project: LocalStack


Запуск проекта:<br>

```bash
    cd project_localstack/
    docker compose up -d --scale spark-worker='ваше количество (макс.: кол-во ядер)'

```
<br>
* Примечание: с учётом InferSchema и механизмом чтения данных в Spark, макс. кол-во может являться не самым оптимальным параметром

---

Структура:<br>
1) dags - папка с DAG
2) docker-scripts - там лежат все докерфайлы сервисов
3) lambda_func - папка с Lambda-функциями и её зависимостями
4) localstack_scripts_init - скрипт, который инициализирует бакет, DynamoDB-таблицы и Lambda-функцию
5) logs - папка для логов Airflow
6) scripts - папка для Spark-скриптов
7) data - папка с csv (orig - большая csv, splits - маленькие разделённые по месяцам - из неё и работают DAGs)

---

