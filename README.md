# 2024-spring-ab-python-ads-HW-6

Реализовать дэшборд на Streamlit с обучением uplift модели и EDA на датасете X5. Для имитации обновления данных реализовать случайный выбор 80% датасета train. В дэшборде реализовать возможность выбора из подходов Solo Model и Two Model и классификаторов CatBoostClassifier и RandomForestClassifier (аналогично семинару). С помощью DockerOperator реализовать ежедневное дообучение модели в Airflow.

**Критерии**:

1. Реализован дэшборд с необходимым функционалом - +3 балла
1. Реализован Dockerfile для дэшборда - +1 балл
1. Выполнен запуск и конфигурация Airflow в kind (приложить скрины Airflow webserver) - +4 балла
1. Реализован ежедневный запуск с помощью DockerOperator - +2 балла

### Подготовка airflow in kind

kind create cluster --name airflow-cluster --config kind-cluster.yaml

kubectl create namespace airflow

kubectl --namespace airflow create secret generic airflow-ssh --from-file=gitSshKey=<PATH_TO_YOUR_PRIVATE_SSH_KEY>

cd airflow && helm upgrade --install -f values.yaml \
--set data.metadataConnection.user=postgres \
--set data.metadataConnection.pass=postgres \
--set data.metadataConnection.db=postgres \
--set webserverSecretKey=94e86f1d2854d6792e554794915f521d \
--namespace airflow \
airflow .

Для доступа к интерфейсу airflow:  
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow

###
