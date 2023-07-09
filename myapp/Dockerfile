FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary --no-cache-dir
RUN pip install pandas plotly --no-cache-dir

COPY . .

CMD ["python", "app.py"]
