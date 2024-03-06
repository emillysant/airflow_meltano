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
  dag_id='Northwind_s3_rds',
  default_args=default_args,
  description='A ELT dag for the Northwind',
  schedule_interval="@daily",
  start_date=datetime(2024, 2, 27),
  tags=["NORTHWIND"],
  catchup=False
) as dag:

  northwind_db=KubernetesPodOperator(
    task_id='northwind_db',
    namespace="prod-airflow",
    image='',
    cmds=[
      "bash",
      "-c",
      "meltano run tap-s3-csv target-postgres"
    ],
    env_vars={
        'TARGET_S3_CSV_AWS_ACCESS_KEY_ID':'',
        'TARGET_S3_CSV_AWS_SECRET_ACCESS_KEY':'',
    },
    dag=dag
  )

  # Defina o comando que será executado no pod.
command = [
    'bash',
    '-c',
    'date',
]

# Crie uma tarefa usando o KubernetesPodOperator para executar o comando no pod.
print_date_task = KubernetesPodOperator(
    task_id='print_date_task',
    name='print-date-pod',
    namespace='default',  # Altere o namespace conforme necessário
    image='ubuntu:latest',  # Imagem do container que será usada
    cmds=command,  # Comando a ser executado no container
    dag=dag,
)

# Defina a ordem de execução das tarefas, se houver mais no DAG.
print_date_task >> northwind_db
