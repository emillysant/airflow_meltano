FROM apache/airflow:2.8.1
ADD requirements.txt .
RUN pip install -r requirements.txt

USER airflow