# Tracking User Behavior at Game Co

## 1. Problem Statement

### 1.1 Situation

Game Co has a RPG-style mobile game. Game is sold at a small fee in the most popular app stores, but most of the revenue stream comes from in-app purchases (users buying new weapons or extra game features).

### 1.2 Complication

To maximize in-app purchases, it is critical to keep the users engaged with the game. We know that certain actions might contribute more than others to increase user engagement and willigness to purchase extra features. So it is imperative for our business to track all user actions taken during the game, including the metadata associated with each event (ex. timestamp, weapon type, guild name). This will allow our data science team to provide data insights to our design team to improve game features in order to maximize user engagement and revenue for Game Co.

### 1.3 Objetive

Track user behavior in stream mode, and prepare the infrastructure to land the data in the form and structure it needs to be to be queried by our data scientists.
This will require:

- Instrument the API server to log events of interest to Kafka
- Assemble a data pipeline to catch these events: use Spark streaming to filter
  select event types from Kafka, land them into HDFS/Parquet to make them
  available for analysis using Presto
- Use Apache Bench to generate test data for our pipeline
- Produce an analytics report to the designing team where with some basic analysis of the events

## 2. Data

This project will be based on _generated_ events with the solely purpose of testing our pipeline. We developed a Linux script to randomly simulate real user interactions with the game app using Apache Bench.

## 3. Tools

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

## 4. Pipeline

1. User interacts with mobile app (our game);
2. Mobile app makes API calls to web services;
3. API server handles requests:
   - handles actual business requirements (eg. process game actions, purchases, etc.) - OUT OF SCOPE FOR THIS PROJECT
   - logs events (user actions) to kafka - SCOPE OF THE PROJECT
4. Spark pulls events from kafka, filters events by type, apply data schemas, and writes them to HDFS in Parquet format;
5. Hive reads Parquet files and creates tables for queries;
5. Presto queries tables to produce analytics.

## 5. Tracked events

In our project, we track three types of event:

1. Purchase a weapon
2. Join a guild
3. Enter a battle

Each of this events can be a simple GET event or a POST event with extra metadata.

For GET events we track the following data:
* Accept
* Host
* User_agent
* Event_type

For POST events we track the following data:
* Accept
* Host
* User_agent
* Event_type
* Content-Length
* Content-Type
* Attributes (metadata related to the user action, eg. type of weapon purchased, strength, range, cost, etc.)

## 6. Bash commands used to set-up the pipeline and generate test events

### 6.1 Spin up the cluster

docker-compose up -d

### 6.2 Perform some checks

docker-compose ps
docker-compose logs -f kafka
docker-compose logs -f cloudera
docker-compose exec cloudera hadoop fs -ls /tmp/

### 6.3 Create the events topic

docker-compose exec kafka \
  kafka-topics \
    --create \
    --topic events \
    --partitions 1 \
    --replication-factor 1 \
    --if-not-exists --zookeeper zookeeper:32181

### 6.4 Run Flask_App

docker-compose exec mids \
  env FLASK_APP=/w205/project-3-lbrossi/code/game_api.py \
  flask run --host 0.0.0.0

### 6.5 Generate random events through AB

chmod +x ab_events_publisher.sh
./ab_events_publisher.sh

### 6.6 Read from kafka

docker-compose exec mids \
  kafkacat -C -b kafka:29092 -t events -o beginning
    
### 6.7 Run Spark stream
    
docker-compose exec spark \
    spark-submit \
    /w205/project-3-lbrossi/code/filtered_writes_stream.py

### 6.8 Check out results in Hadoop

docker-compose exec cloudera hadoop fs -ls /tmp/
docker-compose exec cloudera hadoop fs -ls /tmp/purchase_weapon
docker-compose exec cloudera hadoop fs -ls /tmp/join_guild
docker-compose exec cloudera hadoop fs -ls /tmp/enter_battle

### 6.9 Create tables in Hive, one per event type

docker-compose exec cloudera hive -f /w205/project-3-lbrossi/code/create_tables.hql

### 6.10 Initiate Presto
Note: run these from the main prompt

docker-compose exec presto presto --server presto:8080 --catalog hive --schema default;

### 6.11 Check tables

show tables;
DESCRIBE hive.default.purchase_weapon;
DESCRIBE hive.default.join_guild;
DESCRIBE hive.default.enter_battle;

### 6.12 Count number of rows

select count(*) from purchase_weapon;
select count(*) from join_guild;
select count(*) from enter_battle;

### 6.13 Check tables content

select * from purchase_weapon limit 10;
select * from join_guild limit 10;
select * from enter_battle limit 10;

### 6.14 Run Queries

#### 6.14.1 Which proportion of battles do users win?
select outcome, count(*) as count from enter_battle where outcome is not null group by outcome;

#### 6.14.2 Which enemies do users more frequently battle against?
select enemy, count(*) as count from enter_battle where enemy is not null group by enemy order by count desc;

#### 6.14.3 Which enemy does defeat users the most?
select enemy, count(*) as count from enter_battle where outcome = 'lost' group by enemy order by count desc;

#### 6.14.4 Which guild is preferred by users from comcast?
select guild_name, count(*) as count from join_guild where guild_name is not null and host like '%.comcast.com' group by guild_name order by count desc;

#### 6.14.5 Which users do have acquired special power "Time Freezing"?
select host from join_guild where special_power = 'Time Freezing' order by host;

#### 6.14.6 Which weapon is most purchased among users?
select weapon_type, count(*) as count from purchase_weapon where weapon_type is not null group by weapon_type order by count desc;

#### 6.14.7 From which host domain do users spend more gold coins?
select substr(host, position('.' in host) + 1), sum(gold_cost) as total_spend from purchase_weapon where host <> 'localhost' group by substr(host, position('.' in host) + 1) order by total_spend desc;

## 7. Sample of Results

#### 7.1 Which proportion of battles do users win?
presto:default> select outcome, count(*) as count from enter_battle where outcome is not null group by outcome;

| outcome     | count |
|-------------|-------|
| lost        | 6     |
| won         | 4     |
(2 rows)

#### 7.2 Which enemies do users more frequently battle against?
presto:default> select enemy, count(*) as count from enter_battle where enemy is not null group by enemy order by count desc;

| enemy       | count |
|-------------|-------|
| Head Crabs  | 3     |
| Black Snake | 3     |
| Blitz       | 2     |
| Vega        | 2     |
| Mutilator   | 2     |
| Limerick    | 2     |
| Dark Ganon  | 1     |
(7 rows)


#### 7.3 Which enemy does defeat users the most?
presto:default> select enemy, count(*) as count from enter_battle where outcome = 'lost' group by enemy order by count desc;

| enemy       | count |
|-------------|-------|
| Vega        | 2     |
| Blitz       | 2     |
| Mutilator   | 2     |
| Head Crabs  | 2     |
| Black Snake | 1     |
| Limerick    | 1     |
(6 rows)


#### 7.4 Which guild is preferred by users from comcast?
presto:default> select guild_name, count(*) as count from join_guild where guild_name is not null and host like '%.comcast.com' group by guild_name order by count desc;

| guild_name                | count |
|---------------------------|-------|
| Children Of Virtue        | 2     |
| Twisted Destiny           | 1     |
| Shadows of the Arcane Lost| 1     |
(3 rows)


#### 7.5 Which users do have acquired special power "Time Freezing"?
presto:default> select host from join_guild where special_power = 'Time Freezing' order by host;

| host               |
|--------------------|
| user1.comcast.com  | 
| user12.sprint.com  | 
| user17.sprint.com  | 
| user38.verizon.com | 
| user45.sprint.com  | 
| user6.verizon.com  |
(6 rows)


#### 7.6 Which weapon is most purchased among users?
presto:default> select weapon_type, count(*) as count from purchase_weapon where weapon_type is not null group by weapon_type order by count desc;

| weapon_type       | count |
|-------------------|-------|
| sword             | 10    |
| bow               | 4     |
| spear             | 3     |
| dagger            | 2     |
(4 rows)


#### 7.7 From which host domain do users spend more gold coins?
presto:default> select substr(host, position('.' in host) + 1), sum(gold_cost) as total_spend from purchase_weapon where host <> 'localhost' group by substr(host, position('.' in host) + 1) order by total_spend desc;

| col_0.            | total_spend |
|-------------------|-------------|
| att.com           | 780         |
| verizon.com       | 600         |
| comcast.com       | 510         |
| sprint.com        | 420         |
(4 rows)