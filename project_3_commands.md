## Bash commands used to set-up the pipeline and generate test events

### Spin up the cluster

docker-compose up -d

### Perform some checks

docker-compose ps
docker-compose logs -f kafka
docker-compose logs -f cloudera
docker-compose exec cloudera hadoop fs -ls /tmp/

### Create the events topic

docker-compose exec kafka \
  kafka-topics \
    --create \
    --topic events \
    --partitions 1 \
    --replication-factor 1 \
    --if-not-exists --zookeeper zookeeper:32181

### Run Flask_App

docker-compose exec mids \
  env FLASK_APP=/w205/project-3-lbrossi/code/game_api.py \
  flask run --host 0.0.0.0

### Generate random events through AB

chmod +x ab_events_publisher.sh
./ab_events_publisher.sh

### Read from kafka

docker-compose exec mids \
  kafkacat -C -b kafka:29092 -t events -o beginning
    
### Run Spark stream
    
docker-compose exec spark \
    spark-submit \
    /w205/project-3-lbrossi/code/filtered_writes_stream.py

### Check out results in Hadoop

docker-compose exec cloudera hadoop fs -ls /tmp/
docker-compose exec cloudera hadoop fs -ls /tmp/purchase_weapon
docker-compose exec cloudera hadoop fs -ls /tmp/join_guild
docker-compose exec cloudera hadoop fs -ls /tmp/enter_battle

### Create tables in Hive, one per event type
    
docker-compose exec cloudera hive -f /w205/project-3-lbrossi/code/create_tables.hql

### Initiate Presto
Note: run these from the main prompt

docker-compose exec presto presto --server presto:8080 --catalog hive --schema default;

### Check tables

show tables;
DESCRIBE hive.default.purchase_weapon;
DESCRIBE hive.default.join_guild;
DESCRIBE hive.default.enter_battle;

### Count number of rows

select count(*) from purchase_weapon;
select count(*) from join_guild;
select count(*) from enter_battle;

### Check tables content

select * from purchase_weapon limit 10;
select * from join_guild limit 10;
select * from enter_battle limit 10;

### Run Queries

#### Which proportion of battles do users win?
select outcome, count(*) as count from enter_battle where outcome is not null group by outcome;

#### Which enemies do users more frequently battle against?
select enemy, count(*) as count from enter_battle where enemy is not null group by enemy order by count desc;

#### Which enemy does defeat users the most?
select enemy, count(*) as count from enter_battle where outcome = 'lost' group by enemy order by count desc;

#### Which guild is preferred by users from comcast?
select guild_name, count(*) as count from join_guild where guild_name is not null and host like '%.comcast.com' group by guild_name order by count desc;

#### Which users do have acquired special power "X-Ray Vision"?
select host from join_guild where special_power = 'X-Ray Vision' order by host;

#### Which weapon is most purchased among users?
select weapon_type, count(*) as count from purchase_weapon where weapon_type is not null group by weapon_type order by count desc;

#### From which host domain do users spend more gold coins?
select substr(host, position('.' in host) + 1), sum(gold_cost) as total_spend from purchase_weapon where host <> 'localhost' group by substr(host, position('.' in host) + 1) order by total_spend desc;