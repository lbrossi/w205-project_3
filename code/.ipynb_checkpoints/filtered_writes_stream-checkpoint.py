#!/usr/bin/env python
"""Extract events from kafka, filter, transform and write to hdfs
"""
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

@udf('boolean')
def is_purchase_weapon(event_as_json):
    """udf for filtering purchase_a_weapon events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'purchase_weapon':
        return True
    return False

@udf('boolean')
def is_join_guild(event_as_json):
    """udf for filtering join_a_guild events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'join_guild':
        return True
    return False

@udf('boolean')
def is_enter_battle(event_as_json):
    """udf for filtering enter_battle events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'enter_battle':
        return True
    return False

def post_schema():
    """define schema for post events
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("Content-Length", StringType(), True),
        StructField("Content-Type", StringType(), True),
        StructField("attributes", StringType(), True)
    ])

def battle_attr_schema():
    """define schema for attributes of enter_a_battle events
    """
    return StructType([
        StructField("enemy", StringType(), True),
        StructField("outcome", StringType(), True)
    ])

def guild_attr_schema():
    """define schema for attributes of join_a_guild events
    """
    return StructType([
        StructField("guild_name", StringType(), True),
        StructField("special_power", StringType(), True)
    ])

def weapon_attr_schema():
    """define schema for attributes of purchase_a_weapon events
    """
    return StructType([
        StructField("weapon_type", StringType(), True),
        StructField("damage_level", IntegerType(), True),
        StructField("range", IntegerType(), True),
        StructField("gold_cost", IntegerType(), True)
    ])
        
def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .getOrCreate()

    raw_events = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .load()

    purchase_weapon = raw_events \
        .filter(is_purchase_weapon(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          post_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')
    
    purchase_weapon2 = purchase_weapon \
        .select('raw_event', 'timestamp', 'Accept', 'Host', 
                'User-Agent', 'event_type', 'Content-Length', 'Content-Type', 
                from_json('attributes', weapon_attr_schema()).alias('jsonData')) \
        .select('raw_event', 'Host','timestamp', 'event_type', 'jsonData.*')

    sink_purchase_weapon = purchase_weapon2 \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_purchase_weapon") \
        .option("path", "/tmp/purchase_weapon") \
        .trigger(processingTime="10 seconds") \
        .start()
        
    join_guild = raw_events \
        .filter(is_join_guild(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          post_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')
    
    join_guild2 = join_guild \
        .select('raw_event', 'timestamp', 'Accept', 'Host', 
                'User-Agent', 'event_type', 'Content-Length', 'Content-Type', 
                from_json('attributes', guild_attr_schema()).alias('jsonData')) \
        .select('raw_event', 'Host','timestamp', 'event_type', 'jsonData.*')
    
    sink_join_guild = join_guild2 \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_join_guild") \
        .option("path", "/tmp/join_guild") \
        .trigger(processingTime="10 seconds") \
        .start()
         
    enter_battle = raw_events \
        .filter(is_enter_battle(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          post_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')
    
    enter_battle2 = enter_battle \
        .select('raw_event', 'timestamp', 'Accept', 'Host', 
                'User-Agent', 'event_type', 'Content-Length', 'Content-Type', 
                from_json('attributes', battle_attr_schema()).alias('jsonData')) \
        .select('raw_event', 'Host','timestamp', 'event_type', 'jsonData.*')
    
    sink_enter_battle = enter_battle2 \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_enter_battle") \
        .option("path", "/tmp/enter_battle") \
        .trigger(processingTime="10 seconds") \
        .start()
    
    sink_enter_battle.awaitTermination()
    sink_join_guild.awaitTermination()
    sink_purchase_weapon.awaitTermination()

if __name__ == "__main__":
    main()