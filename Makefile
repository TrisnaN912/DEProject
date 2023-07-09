include .env
export

CURRENT_DATE := $(shell powershell -Command "Get-Date -Format 'yyyy-MM-dd'")
JDBC_URL := "jdbc:postgresql://${POSTGRES_HOST}/${POSTGRES_DB}"
JDBC_PROPERTIES := '{"user": "${POSTGRES_ACCOUNT}", "password": "${POSTGRES_PASSWORD}"}'

help:
	@echo ## postgres			- Run a Postgres container, including its inter-container network.

all: network postgres airflow jupyter

network:
	@docker network inspect de-network >/dev/null 2>&1 || docker network create de-network

postgres: postgres-create

postgres-create:
	@docker-compose -f ./docker/docker-compose-postgres.yml --env-file .env up -d
	@echo '__________________________________________________________'
	@echo 'Postgres container created at port ${POSTGRES_PORT}...'
	@echo '__________________________________________________________'
	@echo 'Postgres Docker Host    : ${POSTGRES_HOST}' &&\
		echo 'Postgres User       	  : ${POSTGRES_USER}' &&\
		echo 'Postgres password       : ${POSTGRES_PASSWORD}' &&\
		echo 'Postgres Db             : ${POSTGRES_DB}'
	@sleep 5
	@echo '==========================================================='

airflow: airflow-create

airflow-create:
	@docker-compose -f ./docker/docker-compose-airflow.yml --env-file .env up -d
	
clean:
	@bash ./helper/goodnight.sh

jupyter:
	@echo '__________________________________________________________'
	@echo 'Creating Jupyter Notebook Cluster at http://localhost:${JUPYTER_PORT}...'
	@echo '__________________________________________________________'
	@docker build -t de/jupyter -f ./docker/jupyter.Dockerfile .
	@docker-compose -f ./docker/docker-compose-jupyter.yml --env-file .env up -d
	@echo 'Created...'
	@echo 'Processing token...'
	@sleep 10
	@docker logs de-jupyter 2>&1 | grep '\?token\=' -m 1 | cut -d '=' -f2
	@echo '==========================================================='