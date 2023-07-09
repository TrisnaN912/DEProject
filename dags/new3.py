from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import psycopg2

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 7, 9),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def read_csv_file():
    dataframe = pd.read_csv('/opt/airflow/dags/McDonald_s_Reviews.csv', encoding='latin-1')
    dataframe = dataframe.drop("rating_count", axis=1)
    dataframe.replace('NaT', None, inplace=True)
    return dataframe

def clean_dataframe(dataframe):
    def parse_date(date_str):
        if pd.isnull(date_str) or date_str == 'NaT':
            return None
        if 'ago' in date_str:
            num_units, unit = date_str.split(' ')[0], date_str.split(' ')[1]
            if unit == 'days':
                return datetime.now() - pd.DateOffset(days=int(num_units))
            elif unit == 'months':
                return datetime.now() - pd.DateOffset(months=int(num_units))
            elif unit == 'years':
                return datetime.now() - pd.DateOffset(years=int(num_units))
        else:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    dataframe['review_time'] = dataframe['review_time'].apply(parse_date)
    dataframe.dropna(inplace=True)
    dataframe.drop_duplicates(inplace=True)
    dataframe['rating'] = dataframe['rating'].str.extract('(\d)').astype(int)
    return dataframe

def create_table():
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        database="mydatabase",
        user="airflow",
        password="mypassword"
    )
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS reviews")
    cur.execute("""
        CREATE TABLE reviews (
            reviewer_id INTEGER,
            store_name VARCHAR(255),
            category VARCHAR(255),
            store_address VARCHAR(255),
            latitude FLOAT,
            longitude FLOAT,
            review_time TIMESTAMP,
            review TEXT,
            rating VARCHAR(10)
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_data(dataframe):
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        database="mydatabase",
        user="airflow",
        password="mypassword"
    )
    cur = conn.cursor()
    data = [tuple(row) for row in dataframe.values]
    insert_query = """
        INSERT INTO reviews (
            reviewer_id,
            store_name,
            category,
            store_address,
            latitude,
            longitude,
            review_time,
            review,
            rating
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.executemany(insert_query, data)
    conn.commit()
    cur.close()
    conn.close()

with DAG('process_data_dag', default_args=default_args, schedule_interval=None) as dag:
    read_csv_task = PythonOperator(
        task_id='read_csv_file',
        python_callable=read_csv_file
    )

    clean_data_task = PythonOperator(
        task_id='clean_dataframe',
        python_callable=clean_dataframe,
        op_args=[read_csv_task.output],
        provide_context=True
    )

    create_table_task = PythonOperator(
        task_id='create_table',
        python_callable=create_table
    )

    insert_data_task = PythonOperator(
        task_id='insert_data',
        python_callable=insert_data,
        op_args=[clean_data_task.output],
        provide_context=True
    )

    read_csv_task >> clean_data_task >> create_table_task >> insert_data_task
