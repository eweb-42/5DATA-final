from datetime import timedelta

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.dummy_operator import DummyOperator
from airflow.hooks.S3_hook import S3Hook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.emr_add_steps_operator import EmrAddStepsOperator
from airflow.contrib.sensors.emr_step_sensor import EmrStepSensor
from airflow.models import Variable

import boto3
import json, csv, os

os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(3)
}

dag = DAG(
    dag_id='unload_erp',
    default_args=default_args,
    description= 'Unloads students to S3',
    schedule_interval=None,
    catchup=False
)

def csv_to_s3_stage():
    s3 = S3Hook(aws_conn_id='s3_conn')
    # s3 = S3Hook()
    bucket_name = Variable.get('bucket_name')
    for file in os.listdir('/tmp'):
        if file.endswith('.csv'):
            key = 'stage/' + file
            s3.load_file(filename='/tmp/' + file, bucket_name=bucket_name, replace=True, key=key)

def query_to_local(sqlFilePath, dest):
    sqlFile = open(sqlFilePath, 'r')
    dml = sqlFile.read()
    pg_hook = PostgresHook(postgres_conn_id='5DATA-ERP')
    conn = pg_hook.get_conn()
    curs = conn.cursor()
    curs.execute(dml)
    results = curs.fetchall()
    with open(dest, 'w') as f:
        writer = csv.writer(f)
        for res in results:
            print(str(res))
            writer.writerow(res)

unload_apprenticeships = PythonOperator(
    dag=dag,
    task_id="unload_apprenticeships",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_apprenticeships.sql',
        'dest': '/tmp/apprenticeships.csv'
    }
)

unload_attendances = PythonOperator(
    dag=dag,
    task_id="unload_attendances",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_attendances.sql',
        'dest': '/tmp/attendances.csv'
    }
)

unload_audiences = PythonOperator(
    dag=dag,
    task_id="unload_audiences",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_audiences.sql',
        'dest': '/tmp/audiences.csv'
    }
)

unload_campuses = PythonOperator(
    dag=dag,
    task_id="unload_campuses",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_campuses.sql',
        'dest': '/tmp/campuses.csv'
    }
)

unload_companies = PythonOperator(
    dag=dag,
    task_id="unload_companies",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_companies.sql',
        'dest': '/tmp/companies.csv'
    }
)

unload_events = PythonOperator(
    dag=dag,
    task_id="unload_events",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_events.sql',
        'dest': '/tmp/events.csv'
    }
)

unload_grades = PythonOperator(
    dag=dag,
    task_id="unload_grades",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_grades.sql',
        'dest': '/tmp/grades.csv'
    }
)

unload_lessons = PythonOperator(
    dag=dag,
    task_id="unload_lessons",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_lessons.sql',
        'dest': '/tmp/lessons.csv'
    }
)

unload_professors = PythonOperator(
    dag=dag,
    task_id="unload_professors",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_professors.sql',
        'dest': '/tmp/professors.csv'
    }
)

unload_students = PythonOperator(
    dag=dag,
    task_id="unload_students",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_students.sql',
        'dest': '/tmp/students.csv'
    }
)

unload_subjects = PythonOperator(
    dag=dag,
    task_id="unload_subjects",
    python_callable=query_to_local,
    op_kwargs={
        'sqlFilePath': '/usr/local/airflow/dags/scripts/unload_subjects.sql',
        'dest': '/tmp/subjects.csv'
    }
)

csv_to_s3_stage = PythonOperator(
    dag=dag,
    task_id='CSVs_to_S3_stage',
    python_callable=csv_to_s3_stage
)

clean_tmp_dir = BashOperator(
    dag=dag,
    task_id='clean_tmp_dir',
    bash_command='rm /tmp/*.csv'
)

with open('/usr/local/airflow/dags/EMR/steps.json') as steps_file:
    emr_steps = json.load(steps_file)

students_average = EmrAddStepsOperator(
    dag=dag,
    task_id='students_average',
    job_flow_id= Variable.get('emr_cluster_id'),
    aws_conn_id='aws_default',
    steps=emr_steps,
    params = {
        'bucket_name' : Variable.get('bucket_name')
    }
)

step_checker = EmrStepSensor(
    dag=dag,
    task_id='watch_step',
    job_flow_id=Variable.get('emr_cluster_id'),
    step_id="{{ task_instance.xcom_pull('students_average', key='return_value')[0] }}",
    aws_conn_id='aws_default'
)

[
    unload_apprenticeships,
    unload_attendances,
    unload_audiences,
    unload_campuses,
    unload_companies,
    unload_events,
    unload_grades,
    unload_lessons,
    unload_professors,
    unload_students,
    unload_subjects
] >> csv_to_s3_stage >> clean_tmp_dir >> students_average >> step_checker