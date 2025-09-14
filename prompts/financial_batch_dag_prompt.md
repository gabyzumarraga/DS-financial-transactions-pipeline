# Financial Batch Processing DAG Requirements

## Overview
Create an Apache Airflow DAG that performs daily batch processing of financial transactions, moving them from the real-time streaming layer to historical storage in PostgreSQL.

## Data Source Options
1. Elasticsearch:
   - Index pattern: `financial_transactions*`
   - Data is already aggregated and indexed
   - Easier to query with date ranges
   - Recommended option for batch processing

2. Kafka Topic:
   - Topic name: `financial_transactions`
   - Real-time stream of data
   - Would require additional processing to handle date ranges
   - Better suited for real-time processing

**Recommendation**: Use Elasticsearch as the source due to better querying capabilities for historical data.

## Data Structure
```json
{
  "app": "Banca Móvil",
  "id_ordenante": "4677717306",
  "valor": 367.6,
  "producto": "Corriente",
  "cuenta_ordenante": "1582464633",
  "cuenta_beneficiario": "3216342883",
  "detalle": "Transacción 3",
  "timestamp": "2025-09-13T05:12:15.093369"
}
```

## Requirements

### DAG Configuration
- Schedule: Daily execution
- Retries: Configure appropriate retry mechanism
- Dependencies: Ensure all tasks are properly linked
- Error handling: Implement robust error handling

### Tasks Breakdown
1. **Extract Data**
   - Query Elasticsearch for previous day's transactions
   - Use timestamp field for filtering
   - Implement pagination for large datasets

2. **Transform Data**
   - Validate data structure
   - Convert timestamp to appropriate format if needed
   - Handle any data type conversions required by PostgreSQL

3. **Load Data**
   - Create PostgreSQL table if not exists
   - Bulk insert transformed data
   - Implement transaction handling
   - Verify data integrity after insertion

4. **Clean Up**
   - Delete processed records from Elasticsearch
   - Log the number of records processed
   - Maintain audit trail

### PostgreSQL Schema
```sql
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
```

## Dependencies Required
- `apache-airflow`
- `elasticsearch-dsl`
- `psycopg2-binary`

## Error Handling
- Implement checks for:
  - Connection failures
  - Data validation errors
  - Incomplete transactions
  - Duplicate records
  - Failed deletions

## Logging Requirements
- Number of records processed
- Any validation errors
- Time taken for each task
- Clean-up confirmation

## Success Criteria
1. All previous day's transactions are correctly stored in PostgreSQL
2. Processed records are removed from Elasticsearch
3. Proper error handling and logging is implemented
4. DAG runs successfully on schedule

## Additional Considerations
- Implement idempotency to handle reprocessing
- Add monitoring for task duration and success rates
- Consider implementing data quality checks
- Add alerting for critical failures