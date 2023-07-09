import pandas as pd
import psycopg2
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('csv_to_postgres_dag', default_args=default_args, schedule_interval=None)

def read_csv_file():
    csv_path = '/opt/airflow/dags/McDonald_s_Reviews.csv'
    dataframe = pd.read_csv(csv_path, encoding='latin-1')
    dataframe = dataframe.drop("rating_count", axis=1)
    return dataframe

def insert_data_to_postgres():
    dataframe = read_csv_file()

    # Membuat koneksi ke database PostgreSQL
    conn = psycopg2.connect(
        host="postgres",
        port=5432,  # Port PostgreSQL
        database="mydatabase",
        user="airflow",
        password="mypassword"
    )

    # Membuka kursor untuk eksekusi perintah SQL
    cur = conn.cursor()

    # Menghapus tabel jika sudah ada
    cur.execute("DROP TABLE IF EXISTS reviews")

    # Membuat tabel baru
    cur.execute("""
        CREATE TABLE reviews (
            reviewer_id INTEGER,
            store_name VARCHAR(255),
            category VARCHAR(255),
            store_address VARCHAR(255),
            latitude FLOAT,
            longitude FLOAT,
            review_time VARCHAR(255),
            review TEXT,
            rating VARCHAR(10)
        )
    """)

    # Mengubah format data DataFrame menjadi tupel yang dapat dimasukkan ke dalam tabel
    data = [tuple(row) for row in dataframe.values]

    # Menyusun perintah SQL untuk memasukkan data ke dalam tabel
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

    # Menjalankan perintah SQL dengan data yang akan dimasukkan
    cur.executemany(insert_query, data)

    # Mengeksekusi dan mengcommit perubahan
    conn.commit()

    # Menutup koneksi dan kursor
    cur.close()
    conn.close()

read_csv_task = PythonOperator(
    task_id='read_csv',
    python_callable=read_csv_file,
    dag=dag
)

insert_data_task = PythonOperator(
    task_id='insert_data_to_postgres',
    python_callable=insert_data_to_postgres,
    dag=dag
)

read_csv_task >> insert_data_task
