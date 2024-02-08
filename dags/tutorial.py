
import textwrap
from datetime import datetime, timedelta
import os

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from docker.types import Mount

with DAG(
    "tutorial",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="A simple tutorial DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 2, 1),
    catchup=False,
    tags=["example"],
) as dag:

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    # t0 = DockerOperator(
    #     task_id='docker_command_sleep',
    #     image='bash',
    #     container_name='task___command_sleep',
    #     # api_version='auto',
    #     auto_remove=True,
    #     command="echo hello",
    #     network_mode="bridge"
    # )

    # t1 = BashOperator(
    #     task_id="print_date",
    #     bash_command="date",
    # )

    # t2 = BashOperator(
    #     task_id="sleep",
    #     depends_on_past=False,
    #     bash_command="sleep 5",
    #     retries=3,
    # )

    # t1.doc_md = textwrap.dedent(
    #     """\
    # #### Task Documentation
    # You can document your task using the attributes `doc_md` (markdown),
    # `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
    # rendered in the UI's Task Instance Details page.
    # ![img](http://montcs.bloomu.edu/~bobmon/Semesters/2012-01/491/import%20soul.png)
    # **Image Credit:** Randall Munroe, [XKCD](https://xkcd.com/license.html)
    # """
    # )

    dag.doc_md = __doc__  # providing that you have a docstring at the beginning of the DAG; OR
    dag.doc_md = """
    This is a documentation placed anywhere
    """  # otherwise, type it like this
    templated_command = textwrap.dedent(
        """
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
    {% endfor %}
    """
    )

    # t3 = BashOperator(
    #     task_id="templated",
    #     depends_on_past=False,
    #     bash_command=templated_command,
    # )


    # Ensure directory exists, create it if it doesn't
    # def create_output_directory():
    #     today_date = datetime.now().strftime('%Y-%m-%d')
    #     output_directory = f"/home/emilly/projetos/pipeline/airflow_meltano/northwind_meltano/output/{today_date}"
    #     os.makedirs(output_directory, exist_ok=True)
    #     print(f"Output directory created: {output_directory}")

    # create_directory_task = PythonOperator(
    #     task_id='create_output_directory',
    #     python_callable=create_output_directory,
    #     dag=dag,
    # )

    # today_date = "{{ execution_date.strftime('%Y-%m-%d') }}"
    # volume_path = f"/home/emilly/projetos/pipeline/airflow_meltano/northwind_meltano/output/{today_date}"


    # Primeiro Buildar a imagem meltano dentro da root
    ## docker build -f Dockerfile.meltano -t meltano .
    meltano_extraction_task = DockerOperator(
        task_id='meltano_extraction',
        image='meltano',
        api_version='auto',
        auto_remove=True,
        command='sh -c " . venv/bin/activate && cd northwind_meltano && meltano run tap-postgres target-jsonl"',
        network_mode='host',
        mounts=[Mount(source="/home/emilly/projetos/pipeline/airflow_meltano/northwind_meltano/output/", target="/meltano/northwind_meltano/output", type="bind")],
        dag=dag,
        mount_tmp_dir=False,
    )
    
    meltano_ingestion_task = DockerOperator (
        task_id='meltano_ingestion',
        image='meltano',
        api_version='auto',
        auto_remove=True,
        command='sh -c " . venv/bin/activate && cd northwind_meltano && meltano run tap-singer-jsonl target-postgres"',
        network_mode='host',
        mounts=[Mount(source="/home/emilly/projetos/pipeline/airflow_meltano/northwind_meltano/output", target="/meltano/northwind_meltano/output", type="bind")],
        dag=dag,
        mount_tmp_dir=False,
    )

    create_directory_task >> meltano_extraction_task >> meltano_ingestion_task
