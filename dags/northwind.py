from datetime import datetime

from airflow.models import Variable
from airflow.operators.postgres_operator import PostgresOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import \
    KubernetesPodOperator
from airflow.utils.task_group import TaskGroup

from airflow import DAG

default_args = {
  "owner": "Emilly",
  "email_on_failure": True,
  "email_on_retry": True,
  "email": ["emilly.santiago@indicium.tech"],
  "concurrency": 8,
  "max_active_runs": 1,
  "retries": 2
}

with DAG(
  dag_id='Northwind',
  default_args=default_args,
  description='A ELT dag for the Northwind',
  schedule_interval="@daily",
  start_date=datetime(2024, 2, 27),
  tags=["NORTHWIND"],
  catchup=False
) as dag:

  # erro de conexão
  # OSError: [Errno 99] Cannot assign requested address 
  # {standard_task_runner.py:107} ERROR - Failed to execute job 263 for task northwind_creation_db (The conn_id `northwind_creation` isn't defined; 299)
  db_northwind_creation = PostgresOperator(
    task_id='db_northwind_creation',
    sql="source/northwind.sql",
    postgres_conn_id='northwind',
    autocommit=True,
    dag=dag,
    params={
      's3_bucket': 'emilysan-datalake-prod',
      'aws_region': 'us-east-2',
      'aws_access_key_id': '',
      'aws_secret_access_key': '',
    }
  )

  db_northwind_creation



