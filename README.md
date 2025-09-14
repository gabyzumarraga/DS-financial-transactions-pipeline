# Financial Pipeline Setup Guide

## Prerequisites

- Python 3.8 or higher
- Docker Desktop
- KNIME Analytics Platform

## Setup Instructions

1. Create and activate Python virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

2. Start the infrastructure services:
```powershell
docker-compose up -d
```

3. Initialize Airflow database:
```powershell
docker-compose run airflow db init
docker-compose run airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

4. Start data generation:
```powershell
python scripts/transaction_generator.py
```

5. Access Services:
- Kibana: http://localhost:5601
- Airflow: http://localhost:8081
- Elasticsearch: http://localhost:9200
- PostgreSQL: localhost:5432

## Directory Structure

```
financial_pipeline/
├── airflow_dags/          # Airflow DAG files
├── config/                # Configuration files
├── data/                  # Data files
├── logs/                  # Log files
├── scripts/              # Python scripts
├── docker-compose.yml    # Docker services configuration
└── requirements.txt      # Python dependencies
```

## Starting the Pipeline

1. Ensure all services are running:
```powershell
docker-compose ps
```

2. Start the transaction generator:
```powershell
python scripts/transaction_generator.py
```

3. Open Kibana to view real-time data:
   - Navigate to http://localhost:5601
   - Click on "Menu" (☰) in the top-left corner
   - Go to "Stack Management" → "Index Patterns"
   - Create a new index pattern with pattern "financial_transactions*"
   - Go back to the main menu
   - Navigate to "Analytics" → "Discover"
   - Select your index pattern to see real-time transaction data
   - Optional: Create visualizations in "Analytics" → "Dashboard" to monitor:
     * Transaction volumes over time
     * Average transaction amounts
     * Distribution by application type
     * Top products being used

4. Check Airflow for batch processing status:
   - Navigate to http://localhost:8081
   - Login with username: admin, password: admin
   - On the DAGs view, look for "financial_batch_dag"
   - Click on the DAG to see detailed execution status
   - Monitor:
     * Task success/failure status
     * Processing timestamps
     * Batch execution logs
     * Data quality checks

## Monitoring

- Check Kibana dashboards for real-time monitoring
- View Airflow UI for batch processing status
- Check application logs in the logs directory

## Troubleshooting

1. If Kafka fails to start:
   - Ensure ports 2181 and 9092 are available
   - Check Docker logs: `docker-compose logs kafka`

2. If Elasticsearch fails:
   - Verify system has enough memory
   - Check logs: `docker-compose logs elasticsearch`

3. If Airflow tasks fail:
   - Check task logs in Airflow UI
   - Verify database connections
