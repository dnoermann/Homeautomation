#!/usr/bin/env python3
# Um die Daten vom Wärmemengenzähler via Mbus auszulesen und sie via MQTT in Homeassistant zu bringen
# Code von https://forum.fhem.de/index.php?topic=45212.45 übernommen und ergänzt
# Howto use:
#    Change IP of yout MQTT Server 
#    Add Crontab entry like this:
#    */2 * * * * /usr/bin/python3 /root/ReadHRIDataUnitMBus.py /dev/ttyAMA0 0 >/dev/null 2>&1
# (C) Dennis Nörmann 2023

import sys
import json
import paho.mqtt.client as mqtt

import xml.etree.ElementTree as ET

from mbus.MBus import MBus

usbdevice = sys.argv[1] # /dev/ttyAMA0 
address = sys.argv[2]   # 0 

mbus = MBus(device=usbdevice)

mbus.connect()
mbus.send_request_frame(int(address))

reply = None

try:
        reply = mbus.recv_frame()
except:
        sys.exit(1)

reply_data = mbus.frame_data_parse(reply)

xml = mbus.frame_data_xml(reply_data).strip()

#print(xml)

mbus.frame_data_free(reply_data)
mbus.disconnect()


# MQTT it
#
tree = ET.ElementTree(ET.fromstring(xml))

Meter        = int(tree.findall(".//DataRecord[@id='1']/Value")[0].text)
ThermalPower = int(tree.findall(".//DataRecord[@id='3']/Value")[0].text)
Flow         = int(tree.findall(".//DataRecord[@id='5']/Value")[0].text)
Temp_VL      = int(tree.findall(".//DataRecord[@id='7']/Value")[0].text)
Temp_RL      = int(tree.findall(".//DataRecord[@id='8']/Value")[0].text)
Temp_Diff    = int(tree.findall(".//DataRecord[@id='9']/Value")[0].text)

client = mqtt.Client()
client.connect("192.168.178.89", 1883, 60)

client.publish("panasonic_heat_pump/Mbus/Meter",Meter)
client.publish("panasonic_heat_pump/Mbus/ThermalPower",ThermalPower)
client.publish("panasonic_heat_pump/Mbus/Flow",Flow)
client.publish("panasonic_heat_pump/Mbus/Temp_VL",Temp_VL)
client.publish("panasonic_heat_pump/Mbus/Temp_RL",Temp_RL)
client.publish("panasonic_heat_pump/Mbus/Temp_Diff",Temp_Diff)

client.disconnect()

