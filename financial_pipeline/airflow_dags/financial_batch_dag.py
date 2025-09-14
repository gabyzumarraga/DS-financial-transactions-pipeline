from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import psycopg2
import logging
import json
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# DAG default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# PostgreSQL connection parameters
PG_CONN = {
    'host': 'postgres',  # Docker service name
    'database': 'financial_db',  # Specific database for our transactions
    'user': 'airflow',    # Docker compose configured user
    'password': 'airflow'  # Docker compose configured password
}

# Elasticsearch connection parameters
ES_CONN = {
    'hosts': ['elasticsearch:9200']  # Docker service name
}

def extract_data(**context) -> List[Dict[str, Any]]:
    """
    Extract all transactions from Elasticsearch.
    """
    try:
        # Initialize Elasticsearch client
        es = Elasticsearch(**ES_CONN)
        
        # Create search query without date filter
        s = Search(using=es, index="financial_transactions*")
        
        # Execute search with scroll to handle large datasets
        data = []
        
        for hit in s.scan():
            doc = hit.to_dict()
            # Convert @timestamp to timestamp if exists
            if '@timestamp' in doc:
                doc['timestamp'] = doc.pop('@timestamp')
            data.append(doc)
            
        logger.info(f"Extracted {len(data)} records from Elasticsearch")
        
        # Push data to XCom for next task
        context['task_instance'].xcom_push(key='extracted_data', value=data)
        return data
        
    except Exception as e:
        logger.error(f"Error extracting data from Elasticsearch: {str(e)}")
        raise

def transform_data(**context) -> List[Dict[str, Any]]:
    """
    Transform and validate the extracted data.
    """
    try:
        # Get data from previous task
        data = context['task_instance'].xcom_pull(task_ids='extract_data', key='extracted_data')
        
        transformed_data = []
        validation_errors = []
        
        required_fields = ['app', 'id_ordenante', 'valor', 'producto', 
                          'cuenta_ordenante', 'cuenta_beneficiario', 
                          'detalle', 'timestamp']
        
        for record in data:
            # Skip record version field
            if '@version' in record:
                del record['@version']
                
            # Validate required fields
            missing_fields = [field for field in required_fields if field not in record]
            if missing_fields:
                validation_errors.append(f"Missing required fields in record: {missing_fields}")
                logger.warning(f"Record with missing fields: {record}")
                continue
                
            try:
                # Transform timestamp to datetime if needed
                if isinstance(record['timestamp'], str):
                    record['timestamp'] = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                
                # Ensure valor is decimal
                record['valor'] = float(record['valor'])
                
                # Add batch date
                record['batch_date'] = datetime.now().date()
                
                transformed_data.append(record)
                
            except (ValueError, TypeError) as e:
                validation_errors.append(f"Error transforming record {record}: {str(e)}")
                logger.warning(f"Error transforming record: {str(e)}")
        
        if validation_errors:
            logger.warning(f"Validation errors encountered:\n{json.dumps(validation_errors, indent=2)}")
            
        logger.info(f"Transformed {len(transformed_data)} records successfully")
        
        # Push transformed data to XCom
        context['task_instance'].xcom_push(key='transformed_data', value=transformed_data)
        return transformed_data
        
    except Exception as e:
        logger.error(f"Error transforming data: {str(e)}")
        raise

def load_data(**context) -> None:
    """
    Load transformed data into PostgreSQL.
    """
    try:
        # Get transformed data from previous task
        data = context['task_instance'].xcom_pull(task_ids='transform_data', key='transformed_data')
        
        if not data:
            logger.warning("No data to load into PostgreSQL")
            return
            
        logger.info(f"Attempting to load {len(data)} records into PostgreSQL")
        
        conn = psycopg2.connect(**PG_CONN)
        cur = conn.cursor()
        
        # Create table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS historical_transactions (
            id SERIAL PRIMARY KEY,
            app VARCHAR(50),
            id_ordenante VARCHAR(10),
            valor DECIMAL(10,2),
            producto VARCHAR(50),
            cuenta_ordenante VARCHAR(10),
            cuenta_beneficiario VARCHAR(10),
            detalle VARCHAR(100),
            timestamp TIMESTAMP,
            batch_date DATE
        );
        """
        cur.execute(create_table_sql)
        
        # Prepare insert query
        insert_sql = """
        INSERT INTO historical_transactions (
            app, id_ordenante, valor, producto, cuenta_ordenante,
            cuenta_beneficiario, detalle, timestamp, batch_date
        ) VALUES (
            %(app)s, %(id_ordenante)s, %(valor)s, %(producto)s,
            %(cuenta_ordenante)s, %(cuenta_beneficiario)s, %(detalle)s,
            %(timestamp)s, %(batch_date)s
        );
        """
        
        # Execute batch insert
        cur.executemany(insert_sql, data)
        
        # Commit transaction
        conn.commit()
        
        logger.info(f"Successfully loaded {len(data)} records into PostgreSQL")
        
    except Exception as e:
        logger.error(f"Error loading data to PostgreSQL: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        raise
        
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def cleanup_data(**context) -> None:
    """
    Delete processed records from Elasticsearch and log summary.
    """
    try:
        # Get processed data
        data = context['task_instance'].xcom_pull(task_ids='transform_data', key='transformed_data')
        
        # Initialize Elasticsearch client
        es = Elasticsearch(**ES_CONN)
        
        # Delete all documents using delete_by_query
        query = {
            "query": {
                "match_all": {}
            }
        }
        
        result = es.delete_by_query(
            index="financial_transactions",
            body=query,
            refresh=True
        )
        
        deleted_count = result.get('deleted', 0)
        
        logger.info(f"Cleanup Summary:")
        logger.info(f"- Total records processed: {len(data)}")
        logger.info(f"- Records deleted from Elasticsearch: {deleted_count}")
        logger.info(f"- Batch Date: {datetime.now().date()}")
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        raise

# Create DAG
with DAG(
    'financial_batch_processing',
    default_args=default_args,
    description='Manual batch processing of financial transactions',
    schedule_interval=None,  # None means manual trigger only
    start_date=datetime(2025, 9, 13),
    catchup=False,
    tags=['financial', 'batch'],
) as dag:
    
    # Define tasks
    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        provide_context=True,
    )
    
    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,
    )
    
    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        provide_context=True,
    )
    
    cleanup_task = PythonOperator(
        task_id='cleanup_data',
        python_callable=cleanup_data,
        provide_context=True,
    )
    
    # Set task dependencies
    extract_task >> transform_task >> load_task >> cleanup_task