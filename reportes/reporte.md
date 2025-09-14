# Pipeline de Procesamiento de Transacciones Financieras

## Resumen Ejecutivo
Este proyecto implementa una infraestructura de procesamiento de datos financieros que combina capacidades de procesamiento en tiempo real y por lotes. El sistema está diseñado para manejar transacciones financieras con alta confiabilidad, garantizando la persistencia de datos y proporcionando capacidades tanto de monitoreo en tiempo real como de análisis histórico.

## Objetivos del Proyecto
- Implementar un sistema escalable para el procesamiento de transacciones financieras
- Garantizar la persistencia y trazabilidad de las transacciones
- Proporcionar visualización en tiempo real de las operaciones
- Mantener un histórico de transacciones para análisis y auditoría
- Asegurar la confiabilidad y recuperación de datos

## Arquitectura del Sistema

### Componentes Principales
1. **Generación de Datos**
   - Simulador de transacciones en Python
   - Genera transacciones financieras realistas con campos estructurados

2. **Procesamiento en Tiempo Real**
   - Apache Kafka para mensajería distribuida
   - Logstash para ingesta y transformación de datos
   - Elasticsearch para almacenamiento temporal
   - Kibana para visualización en tiempo real

3. **Procesamiento por Lotes**
   - Apache Airflow para orquestación
   - PostgreSQL para almacenamiento histórico
   - DAG personalizado para ETL

### Flujo de Datos
1. **Flujo en Tiempo Real**
   ```
   Generador → Kafka → Logstash → Elasticsearch → Kibana
   ```

2. **Flujo por Lotes**
   ```
   Elasticsearch → Airflow DAG → PostgreSQL
   ```

## Estructura de Datos

### Modelo de Transacción
```json
{
    "app": "string",            // Aplicación origen
    "id_ordenante": "string",   // ID del ordenante
    "valor": "decimal",         // Monto de la transacción
    "producto": "string",       // Tipo de producto financiero
    "cuenta_ordenante": "string",    // Cuenta origen
    "cuenta_beneficiario": "string", // Cuenta destino
    "detalle": "string",       // Descripción de la transacción
    "timestamp": "datetime",    // Fecha y hora de la transacción
    "batch_date": "date"       // Fecha de procesamiento batch
}
```

## Justificación de la Arquitectura

### Elección de Tecnologías
1. **Apache Kafka**
   - Alta disponibilidad y tolerancia a fallos
   - Capacidad de procesamiento de millones de mensajes por segundo
   - Garantía de orden y entrega de mensajes
   - Escalabilidad horizontal

2. **Elasticsearch**
   - Búsqueda y análisis en tiempo real
   - Indexación rápida
   - Capacidades de agregación avanzadas
   - Integración nativa con Kibana

3. **PostgreSQL**
   - ACID compliance para transacciones críticas
   - Esquema estructurado para datos históricos
   - Capacidades de consulta SQL avanzadas
   - Soporte para grandes volúmenes de datos

4. **Apache Airflow**
   - Orquestación confiable de procesos
   - Monitoreo y logging integrado
   - Manejo de dependencias y reintentos
   - Interfaz web para administración

### Ventajas en Ambiente Productivo

1. **Escalabilidad**
   - Arquitectura distribuida que permite escalar horizontalmente
   - Separación de preocupaciones entre procesamiento en tiempo real y batch
   - Capacidad de manejar picos de carga

2. **Confiabilidad**
   - Múltiples capas de persistencia de datos
   - Sistema de recuperación ante fallos
   - Monitoreo en tiempo real de la salud del sistema

3. **Mantenibilidad**
   - Arquitectura modular
   - Separación clara de responsabilidades
   - Fácil diagnóstico y resolución de problemas

4. **Observabilidad**
   - Dashboards en tiempo real
   - Logs centralizados
   - Métricas de rendimiento

## Consideraciones de Implementación

### Seguridad
- Comunicación segura entre componentes
- Autenticación y autorización
- Auditoría de accesos y cambios

### Monitoreo
- Dashboards de Kibana para visualización
- Métricas de rendimiento del sistema
- Alertas configurables

### Respaldo y Recuperación
- Persistencia de datos en múltiples niveles
- Estrategias de backup
- Procedimientos de recuperación

## Retos Técnicos y Soluciones Implementadas

### 1. Integración Kafka-Elasticsearch
#### Desafío
La conexión directa entre Kafka y Elasticsearch presentó varios desafíos:
- Incompatibilidad de formatos de datos entre Kafka y Elasticsearch
- Necesidad de transformación de datos en tiempo real
- Manejo de backpressure y garantía de entrega de mensajes
- Gestión de errores y recuperación de fallos

#### Solución
Se implementó Logstash como intermediario entre Kafka y Elasticsearch debido a:
- Capacidad de transformación de datos en tiempo real
- Manejo nativo de la conexión con ambos sistemas
- Buffer interno para manejar picos de carga
- Configuración declarativa mediante archivo `logstash.conf`

```conf
input {
  kafka {
    bootstrap_servers => "kafka:9093"
    topics => ["financial_transactions"]
    codec => json
    client_id => "logstash_consumer"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "financial_transactions"
  }
}
```

### 2. Lectura de Datos en Tiempo Real con Airflow DAG
#### Desafío
El DAG necesitaba:
- Acceder a datos en tiempo real desde Elasticsearch
- Manejar grandes volúmenes de datos sin saturar la memoria
- Garantizar la consistencia en el procesamiento por lotes
- Evitar duplicados y pérdida de datos

#### Solución Implementada
Se diseñó un sistema robusto de ETL utilizando:

1. **Extracción Eficiente**:
```python
def extract_data(**context):
    es = Elasticsearch(**ES_CONN)
    s = Search(using=es, index="financial_transactions*")
    data = []
    for hit in s.scan():
        doc = hit.to_dict()
        if '@timestamp' in doc:
            doc['timestamp'] = doc.pop('@timestamp')
        data.append(doc)
```
- Uso de `scan()` para manejar grandes conjuntos de datos
- Procesamiento por lotes para optimizar memoria
- Transformación de campos durante la extracción

2. **Validación y Transformación**:
```python
def transform_data(**context):
    required_fields = ['app', 'id_ordenante', 'valor', 'producto', 
                      'cuenta_ordenante', 'cuenta_beneficiario', 
                      'detalle', 'timestamp']
    # Validación de campos requeridos
    missing_fields = [field for field in required_fields if field not in record]
```
- Validación estricta de campos requeridos
- Transformación de tipos de datos
- Manejo de errores con registro detallado

3. **Gestión de Estado**:
- Implementación de sistema de limpieza post-procesamiento
- Confirmación de inserción en PostgreSQL antes de eliminar de Elasticsearch
- Logging detallado para auditoría y troubleshooting

### 3. Sincronización de Procesos
#### Desafío
- Coordinar el procesamiento en tiempo real con el procesamiento por lotes
- Evitar pérdida de datos durante la ventana de procesamiento
- Mantener la consistencia entre Elasticsearch y PostgreSQL

#### Solución
1. **Implementación de Ventanas de Procesamiento**:
- El DAG se ejecuta manualmente para controlar el momento del procesamiento
- Validación de datos antes de la eliminación
- Sistema de logging para rastrear cada operación

2. **Manejo de Errores**:
```python
try:
    # Operaciones de procesamiento
    conn.commit()
except Exception as e:
    conn.rollback()
    logger.error(f"Error: {str(e)}")
    raise
```
- Transacciones atómicas en PostgreSQL
- Rollback automático en caso de error
- Registro detallado de excepciones

## Mejoras Futuras
1. **Alta Disponibilidad**
   - Implementación de clusters
   - Replicación geográfica
   - Balanceo de carga

2. **Seguridad**
   - Implementación de SSL/TLS
   - Cifrado de datos sensibles
   - Autenticación OAuth/OIDC

3. **Análisis Avanzado**
   - Implementación de ML para detección de fraudes
   - Análisis predictivo
   - Reportes automatizados

## Conclusiones
Este proyecto demuestra una arquitectura robusta y escalable para el procesamiento de transacciones financieras, combinando lo mejor de los paradigmas batch y tiempo real. La implementación actual proporciona una base sólida para futuras extensiones y mejoras, mientras mantiene la confiabilidad y rendimiento necesarios para un sistema financiero.

## Apéndices

### Requisitos del Sistema
- Docker y Docker Compose
- Python 3.8+
- Mínimo 8GB RAM
- 20GB espacio en disco

### Guía de Despliegue
1. Clonar el repositorio
2. Configurar variables de entorno
3. Ejecutar `docker-compose up -d`
4. Verificar la salud de los servicios

### Documentación Adicional
- [Configuración de Logstash](./config/logstash.conf)
- [DAG de Airflow](./airflow_dags/financial_batch_dag.py)
- [Generador de Transacciones](./scripts/transaction_generator.py)

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
