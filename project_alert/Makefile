IMAGE_NAME = alert:v1
SOURCES = Dockerfile requirements.txt $(shell find . -type f \( -name "*.py" -o -name "*.csv" \)) # Список py-файлов, изменения которых стоит отслеживать

# Что будет выполняться, если просто ввести make
all: deploy

# Сборка образа
.build_marker: $(SOURCES)
	@echo $(SOURCES)
	@eval $$(minikube docker-env) && docker build -t $(IMAGE_NAME) . 
	@touch .build_marker

# Деплой в Kubernetes (Наш случай - minikube)
deploy: .build_marker
	@kubectl apply --validate=false -f kuber-manifests/config_map.yaml  
	@kubectl apply --validate=false -f kuber-manifests/alert_manifest.yaml

# Принудительная пересборка (очистка)
clean:
	@rm -f .build_marker

# Тестовый запуск (создать Job из CronJob прямо сейчас)
test-run: deploy
	@kubectl delete job manual-test-job 2>/dev/null || true
	@kubectl create job --from=cronjob/python-check-logs manual-test-job
	@sleep 2
	@kubectl get pods -l job-name=manual-test-job

# Остановка кластера
stop:
	@minikube stop

# Полное удаление кластера
destroy:
	@minikube delete
	@rm -f .build_marker

.PHONY: all deploy clean test-run stop destroy