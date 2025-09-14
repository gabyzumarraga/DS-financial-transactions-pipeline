# Pipeline de Registro Centralizado de Transacciones Financieras

## 🎯 Objetivo
Implementar un sistema de registro centralizado de transacciones financieras que procese datos en batch y near real-time, permitiendo el análisis y monitoreo de transacciones financieras de diferentes aplicaciones bancarias.

## 🏗️ Arquitectura Propuesta

### Componentes Principales:
1. **Generadores de Datos**
   - Simulador de transacciones en tiempo real (Python + Kafka)

2. **Procesamiento y Orquestación**
   - Apache Airflow (DAGs para procesamiento batch)
   - Apache Kafka (Streaming de datos en tiempo real)
   - KNIME (Transformación y análisis de datos)

3. **Almacenamiento**
   - Elasticsearch (Almacenamiento principal y búsqueda)
   - PostgreSQL (Almacenamiento histórico)

4. **Visualización**
   - Kibana (Dashboards en tiempo real)

## 🔄 Flujos de Datos

### Flujo Batch
1. Procesamiento mediante DAGs de Airflow
2. Almacenamiento en PostgreSQL y Elasticsearch

### Flujo Near Real-Time
1. Generación continua de transacciones
2. Streaming a través de Kafka
3. Procesamiento en tiempo real
4. Indexación en Elasticsearch
5. Visualización en tiempo real en Kibana

## 📋 Pasos de Implementación

### 1. Configuración del Entorno Local

```bash
# Crear directorios del proyecto
mkdir financial_pipeline
cd financial_pipeline
mkdir data scripts airflow_dags knime_workflows config logs
```

### 2. Instalación de Componentes

#### Docker y Docker Compose
```bash
# Instalar Docker Desktop para Windows
# Verificar instalación
docker --version
docker-compose --version
```

#### Elasticsearch y Kibana
```yaml
# docker-compose.yml
version: '3'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.9.3
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  
  kibana:
    image: docker.elastic.co/kibana/kibana:7.9.3
    ports:
      - "5601:5601"
```

#### Apache Kafka
```yaml
# Añadir a docker-compose.yml
  zookeeper:
    image: wurstmeister/zookeeper
    ports:
      - "2181:2181"
  
  kafka:
    image: wurstmeister/kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_HOST_NAME: localhost
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
```

### 3. Configuración de Apache Airflow

```python
# airflow_dags/financial_batch_dag.py
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'financial_transactions_batch',
    default_args=default_args,
    schedule_interval='@daily'
)
```

### 4. Generador de Datos de Prueba

```python
# scripts/transaction_generator.py
import random
import json
from datetime import datetime
from kafka import KafkaProducer

def generate_transaction():
    apps = ['Banca Web', 'DeUna', 'Banca Móvil', 'Otras Aplicaciones']
    productos = ['Ahorros', 'Corriente', 'Inversiones', 'Tarjeta Crédito', 'Tarjeta Débito']
    
    return {
        'app': random.choice(apps),
        'id_ordenante': str(random.randint(1000000000, 9999999999)),
        'valor': round(random.uniform(10, 1000), 2),
        'producto': random.choice(productos),
        'cuenta_ordenante': str(random.randint(1000000000, 9999999999)),
        'cuenta_beneficiario': str(random.randint(1000000000, 9999999999)),
        'detalle': f"Transacción {random.randint(1, 1000)}",
        'timestamp': datetime.now().isoformat()
    }
```

### 5. Configuración de Elasticsearch

```json
// config/elasticsearch_mapping.json
{
  "mappings": {
    "properties": {
      "app": { "type": "keyword" },
      "id_ordenante": { "type": "keyword" },
      "valor": { "type": "float" },
      "producto": { "type": "keyword" },
      "cuenta_ordenante": { "type": "keyword" },
      "cuenta_beneficiario": { "type": "keyword" },
      "detalle": { "type": "text" },
      "timestamp": { "type": "date" }
    }
  }
}
```

## 🚀 Ejecución del Pipeline

1. Iniciar servicios:
```bash
docker-compose up -d
```

2. Iniciar Airflow:
```bash
airflow webserver -p 8080
airflow scheduler
```

3. Ejecutar generador de datos en tiempo real:
```bash
python scripts/transaction_generator.py
```

4. Acceder a los dashboards:
   - Kibana: http://localhost:5601
   - Airflow: http://localhost:8080

## 📊 Monitoreo y Visualización

### Dashboards en Kibana
1. Transacciones por aplicación
2. Montos promedio por producto
3. Tendencias temporales
4. Alertas de transacciones inusuales

### Reportes en KNIME
1. Análisis histórico de transacciones
2. Patrones de comportamiento
3. Reportes de auditoría

## 🔍 Consideraciones de Seguridad

1. Implementar autenticación en todos los servicios
2. Encriptar datos sensibles
3. Implementar logs de auditoría
4. Monitorear el rendimiento del sistema

## 📈 Métricas de Éxito

1. Latencia del procesamiento en tiempo real < 5 segundos
2. Procesamiento batch completado en < 1 hora
3. Disponibilidad del sistema > 99.9%
4. Tasa de error en procesamiento < 0.1%

## 🛠️ Mantenimiento

1. Backup diario de Elasticsearch
2. Monitoreo de logs
3. Actualización periódica de componentes
4. Pruebas de carga mensual
