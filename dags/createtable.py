from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('create_table_dag', default_args=default_args, schedule_interval=None)

create_table_query = """
CREATE TABLE reviews (
    reviewer_id INTEGER,
    store_name VARCHAR(255),
    category VARCHAR(255),
    store_address VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    rating_count INTEGER,
    review_time VARCHAR(255),
    review TEXT,
    rating VARCHAR(10)
);
"""

def on_success_callback(context):
    print("Task 'create_postgres_table' succeeded!")

create_table_task = PostgresOperator(
    task_id='create_postgres_table',
    sql=create_table_query,
    postgres_conn_id='postgres_airflow',
    dag=dag,
    on_success_callback=on_success_callback
)

create_table_task
