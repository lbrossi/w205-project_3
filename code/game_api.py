#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')

def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())

@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "This is the default response!\n"

@app.route("/purchase_a_weapon", methods = ['GET', 'POST'])
def purchase_a_weapon():
    if request.method == 'GET':
        purchase_weapon_event = {'event_type': 'purchase_weapon'}
        log_to_kafka('events', purchase_weapon_event)
        return "Weapon Purchased!\n"
    else:
        if request.headers['Content-Type'] == 'application/json':
            purchase_weapon_event = {'event_type': 'purchase_weapon', 'attributes': json.dumps(request.json)}
            log_to_kafka('events', purchase_weapon_event)
            return "Weapon Purchased!" + json.dumps(request.json) + "\n"

@app.route("/join_a_guild", methods = ['GET', 'POST'])
def join_a_guild():
    if request.method == 'GET':
        join_guild_event = {'event_type': 'join_guild'}
        log_to_kafka('events', join_guild_event)
        return "Joined a Guild!\n"
    else:
        if request.headers['Content-Type'] == 'application/json':
            join_guild_event = {'event_type': 'join_guild', 'attributes': json.dumps(request.json)}
            log_to_kafka('events', join_guild_event)
            return "Joined a Guild!" + json.dumps(request.json) + "\n"

@app.route("/enter_a_battle", methods = ['GET','POST'])
def enter_battle():
    if request.method == 'GET':
        enter_battle_event = {'event_type': 'enter_battle'}
        log_to_kafka('events', enter_battle_event)
        return "Entered a Battle!\n"
    else:
        if request.headers['Content-Type'] == 'application/json':
            enter_battle_event = {'event_type': 'enter_battle', 'attributes': json.dumps(request.json)}
            log_to_kafka('events', enter_battle_event)
            return "Entered a Battle!" + json.dumps(request.json) + "\n"