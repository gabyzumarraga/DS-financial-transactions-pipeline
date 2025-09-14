import random
import json
from datetime import datetime
from kafka import KafkaProducer
import time

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
        "timestamp": datetime.utcnow().isoformat()        
    }

def main():
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(2, 4, 1)
    )

    print("Starting transaction generator...")
    while True:
        try:
            transaction = generate_transaction()
            producer.send('financial_transactions', transaction)
            print(f"Generated transaction: {transaction['detalle']} - ${transaction['valor']}")
            time.sleep(1)  # Generate one transaction per second
        except Exception as e:
            print(f"Error generating transaction: {e}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    main()
