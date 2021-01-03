# Tracking User Behavior at Game Co

## Problem Statement

### Situation

Game Co has a RPG-style mobile game. Game is sold at a small fee in the most popular app stores, but most of the revenue stream comes from in-app purchases (users buying new weapons or extra game features).

### Complication

To maximize in-app purchases, it is critical to keep the users engaged with the game. We know that certain actions might contribute more than others to increase user engagement and willigness to purchase extra features. So it is imperative for our business to track all user actions taken during the game, including the metadata associated with each event (ex. timestamp, weapon type, guild name). This will allow our data science team to provide data insights to our design team to improve game features in order to maximize user engagement and revenue for Game Co.

### Objetive

Track user behavior in stream mode, and prepare the infrastructure to land the data in the form and structure it needs to be to be queried by our data scientists.
This will require:

- Instrument the API server to log events of interest to Kafka
- Assemble a data pipeline to catch these events: use Spark streaming to filter
  select event types from Kafka, land them into HDFS/Parquet to make them
  available for analysis using Presto
- Use Apache Bench to generate test data for our pipeline
- Produce an analytics report to the designing team where with some basic analysis of the events

## Data

This project will be based on _generated_ events with the solely purpose of testing our pipeline. We developed a Linux script to randomly simulate real user interactions with the game app using Apache Bench.

## Tools

- This project was done entirely on Google Cloud Platform (GCP).
- This project made use of the following tools:
    * Docker/docker-compose (to set-up the cluster of containers)
    * Flask (to instrument our web server API)
    * Kafka (to publish and consume messages)
    * Zookeeper (broker)
    * Spark/pyspark (to extract, filter, flatten and load the messages into HDFS)
    * Cloudera/HDFS (to store final data in Parquet format)
    * Hive metastore (schema registry)
    * Presto (to query the data from HDFS)
    * Linux Bash (to run commands and scripts through CLI)
    * Apache Bench (to simulate user interactions with the app)
    * Python 3 json package (to wrap and unwrap JSON data models)

## Repo structure

- The project repo contains the following files:
    * Final_report.md (markdown file with the full report)
    * project_3_commands (list of bash commands used to set-up the pipeline and generate test events)
    * code/docker-compose.yml (docker-compose file used to spin up the cluster used in the project)
    * code/game_api.py (python script used to instrument the API server to log events to Kafka)
    * code/ab_events_publisher.sh (bash script used to randomly generate test data for the pipeline)
    * code/battle_events.txt, guild_events.txt, weapon_events.txt (repository of POST events randomly selected by ab_events_publisher.sh)
    * code/filtered_writes_stream.py (pyspark script to extract, filter, flatten and load the messages into HDFS/Parquet)
    * create_tables.hql (hive script to pass schema and create tables for queries)