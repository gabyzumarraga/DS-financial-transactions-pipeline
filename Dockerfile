FROM python:3.8-slim

WORKDIR /app

RUN pip install kafka-python

COPY scripts/ /app/scripts/

CMD ["python", "/app/scripts/transaction_generator.py"]