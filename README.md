# 2024-spring-ab-python-ads-HW-6

Реализовать дэшборд на Streamlit с обучением uplift модели и EDA на датасете X5. Для имитации обновления данных реализовать случайный выбор 80% датасета train. В дэшборде реализовать возможность выбора из подходов Solo Model и Two Model и классификаторов CatBoostClassifier и RandomForestClassifier (аналогично семинару). С помощью DockerOperator реализовать ежедневное дообучение модели в Airflow.

**Критерии**:

1. Реализован дэшборд с необходимым функционалом - +3 балла
1. Реализован Dockerfile для дэшборда - +1 балл
1. Выполнен запуск и конфигурация Airflow в kind (приложить скрины Airflow webserver) - +4 балла
1. Реализован ежедневный запуск с помощью ~~DockerOperator~~ KubernetesPodOperator - +2 балла

P.S. DockerOperator запускать в airflow, который в Kubernetes оказалось тяжко и в целом антипаттерн, поэтому я выбрал KubernetesPodOperator

### Подготовка airflow in kind

kind create cluster --name airflow-cluster --config kind-cluster.yaml

kubectl create namespace airflow

\# Необходимо добавить публичный ssh ключ в deploy keys гит репозитория  
kubectl --namespace airflow create secret generic airflow-ssh --from-file=gitSshKey=<PATH_TO_YOUR_PRIVATE_SSH_KEY>

\# Собираем кастомный образ airflow  
docker build -t custom-airflow:2.8.2 . -f airflow.Dockerfile

\# Пушим собранный образ в kind  
kind load docker-image custom-airflow:2.8.2 --name airflow-cluster

\# Деплоим airflow(с папки airflow)
helm upgrade --install -f values.yaml \
--set data.metadataConnection.user=postgres \
--set data.metadataConnection.pass=postgres \
--set data.metadataConnection.db=postgres \
--set webserverSecretKey=94e86f1d2854d6792e554794915f521d \
--namespace airflow \
airflow .

\# Собираем образ для нашего DAG-a(с папки dags)  
docker build -t model-train:1.0.0 . -f train.Dockerfile

\# Пушим собранный образ в kind  
kind load docker-image model-train:1.0.0 --name airflow-cluster

\#Для доступа к интерфейсу airflow:  
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow

### Подготовка streamlit in kind

\# Собираем образ streamlit(с папки streamlit)  
docker build -t custom-streamlit:1.0.0 . -f Dockerfile

\# Пушим собранный образ в kind  
kind load docker-image custom-streamlit:1.0.0 --name airflow-cluster

\# Деплоим airflow(с папки streamlit/deploy)
helm upgrade --install -f values.yaml \
--namespace airflow \
streamlit .

\#Для доступа к интерфейсу streamlit:  
kubectl port-forward svc/streamlit-service 8501:8501 --namespace airflow

### Скриншот из интерфейса airflow

![Alt text](./Screenshot_2024-03-31_06-06-13.png?raw=true "Airflow Dag")
