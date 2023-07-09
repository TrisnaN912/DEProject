from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd
from datetime import datetime

default_args = {
    'start_date': datetime(2023, 7, 8),
    'schedule_interval': None
}

dag = DAG(
    'read_csv_dag',
    default_args=default_args,
    description='DAG to read CSV file',
)

def read_csv_file():
    # Read the CSV file
    csv_path = '/opt/airflow/dags/McDonald_s_Reviews.csv'
    df = pd.read_csv(csv_path, encoding='latin-1')
    
    # Perform operations on the data
    # ...
    
    # Example: Print the first few rows
    print(df.head())

def on_success_callback(context):
    print("Task succeeded!")

read_csv_task = PythonOperator(
    task_id='read_csv',
    python_callable=read_csv_file,
    on_success_callback=on_success_callback,
    dag=dag
)

read_csv_task
