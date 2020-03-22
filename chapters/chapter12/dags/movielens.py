import logging
import json
import os

from airflow import DAG, utils as airflow_utils
from airflow.operators.docker_operator import DockerOperator

with DAG(
    dag_id="chapter12_movielens",
    description="Fetches ratings from the Movielens API using Docker.",
    start_date=airflow_utils.dates.days_ago(3),
    schedule_interval="@daily",
) as dag:

    fetch_ratings = DockerOperator(
        task_id="fetch_ratings",
        image="airflowbook/movielens-api",
        command=[
            "fetch_ratings.py",
            "--start_date",
            "{{ds}}",
            "--end_date",
            "{{next_ds}}",
            "--output_path",
            "/data/ratings/{{ds}}.json",
            "--user",
            os.environ["MOVIELENS_USER"],
            "--password",
            os.environ["MOVIELENS_PASSWORD"],
            "--host",
            os.environ["MOVIELENS_HOST"],
        ],
        network_mode="chapter12_airflow",
        # Note: this host path is on the HOST, not in the Airflow docker container.
        volumes=["/tmp/airflow/data:/data"],
    )

    rank_movies = DockerOperator(
        task_id="rank_movies",
        image="airflowbook/movielens-ranking",
        command=[
            "rank_movies.py",
            "--input_path",
            "/data/ratings/{{ds}}.json",
            "--output_path",
            "/data/rankings/{{ds}}.csv",
        ],
        volumes=["/tmp/airflow/data:/data"],
    )

    fetch_ratings >> rank_movies
