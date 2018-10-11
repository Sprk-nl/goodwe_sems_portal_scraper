#!/usr/bin/env python3
import sys
import datetime
import time as t
import os
import subprocess
import json
import re
import base64
import ssl
import urllib.request
from datetime import timedelta, datetime, time
import paho.mqtt.client as mqtt #import the client1

#Web scraping module:
import requests
from bs4 import BeautifulSoup

url = 'https://www.semsportal.com/home/login'
login_data = dict(account='YOUR_USERNAME', pwd='YOUR_PASSWORD')

session_requests = requests.session()
r = session_requests.post(url, data=login_data)

htmlresponse = json.loads(r.text).get('data').get('redirect') # Convert response to dict
url = "https://www.semsportal.com" + htmlresponse

result = session_requests.get(url, headers = dict(referer = url) )

htmlcontent= result.content # transform the result to html content

# parse the html using beautiful soup
soup = BeautifulSoup(htmlcontent, 'html.parser')

# Filtering
data  = soup.find_all("script")[19].string
filter1 = ( str(soup).split("var pw_info = ")[1] )
filter2 = str(filter1).split("var pw_id = ")[0]
filter3 = filter2.split(";")[0]

filter4 = json.loads(filter3)
filter5 = dict(filter4)


# MQTT
#Client(client_id="GoodweScraper", clean_session=True, userdata=None, protocol=MQTTv311, transport=”tcp”)
mqtt_client_name = "goodwescraper"
mqtt_host = "YOUR_MQTT_SERVER"
homeassistant_initial_config = True
homeassistant_state_update = True
homeassistant_delete_sensor = False

discovery_prefix = 'homeassistant'
component = 'sensor'
node_id = 'goodwe_sems_portal'
mqtt_topic_template = discovery_prefix + "/" + component + "/" + node_id

client =mqtt.Client(mqtt_client_name)
client.connect(mqtt_host, port=1883, keepalive=60)
payload_start = filter4['inverter'][0]['invert_full']


if (homeassistant_initial_config):
    for k, v in filter4['inverter'][0]['invert_full'].items():
        mqtt_topic = str( mqtt_topic_template + '_' + k + '/config')
        payload_dict = {}
        #payload_dict['device_class'] = 'sensor'
        payload_dict['name'] = str(node_id + '_' + k).lower()
        payload_dict['state_topic'] = mqtt_topic_template + '_' + k + '/state'
        payload_json = json.dumps(payload_dict)
        mqtt_payload = str(payload_json)
        client.publish(mqtt_topic,mqtt_payload)
        t.sleep(0.2)

if (homeassistant_delete_sensor):
    mqtt_topic = str( mqtt_topic_template + "/" + k + '/state')
    payload = ''
    client.publish(mqtt_topic,payload)

if (homeassistant_state_update):
    for k, v in filter4['inverter'][0]['invert_full'].items():
        payload_dict = {}
        key = k
        value = v
        payload_dict[key] = value
        mqtt_topic = str( mqtt_topic_template + '_' + k + '/state')
        payload_json = json.dumps(payload_dict)
        mqtt_payload = str(v)
        client.publish(mqtt_topic,mqtt_payload)
        t.sleep(0.2)
