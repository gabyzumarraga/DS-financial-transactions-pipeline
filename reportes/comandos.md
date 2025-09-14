Topico: financial_transactions

COMANDOS

- Listar tópicos (contenedor)
  kafka-topics.sh --list --bootstrap-server localhost:9092

- Ejecución script 
  "C:/Users/gabyz/Downloads/Proyecto Final/.venv/Scripts/python.exe" "c:/Users/gabyz/Downloads/Proyecto Final/financial_pipeline/scripts/transaction_generator.py"


- Verificar contenedores
  docker-compose ps

- Veificar logs logstash
  docker-compose logs logstash



_______
docker compose exec airflow airflow users list

docker compose exec airflow airflow users delete -u admin

docker compose exec airflow airflow users create  --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin











_____________________


docker cp "c:\Users\gabyz\Downloads\Proyecto Final\financial_pipeline\airflow_dags\financial_batch_dag.py" financial_pipeline-airflow-webserver-1:/opt/airflow/dags/ ; docker cp "c:\Users\gabyz\Downloads\Proyecto Final\financial_pipeline\airflow_dags\financial_batch_dag.py" financial_pipeline-airflow-scheduler-1:/opt/airflow/dags/



_______


docker-compose exec postgres psql -U airflow -c "CREATE DATABASE financial_db;


docker-compose exec postgres psql -U airflow -d financial_db -c "
CREATE TABLE IF NOT EXISTS financial_transactions (
    id SERIAL PRIMARY KEY,
    app VARCHAR(100),
    id_ordenante VARCHAR(20),
    valor NUMERIC(10,2),
    producto VARCHAR(100),
    cuenta_ordenante VARCHAR(20),
    cuenta_beneficiario VARCHAR(20),
    detalle VARCHAR(200),
    timestamp TIMESTAMP,
    batch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"