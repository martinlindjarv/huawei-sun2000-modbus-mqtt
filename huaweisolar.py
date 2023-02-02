import time
from huawei_solar import HuaweiSolar
import huawei_solar
import paho.mqtt.client
import os

import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

inverter_ip = os.getenv('INVERTER_IP', '192.168.1.1')

## MQTT parameters from environment
mqtt_host = os.getenv('MQTT_HOST', '192.168.1.1')
mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
mqtt_username = os.getenv('MQTT_USER', '')
mqtt_password = os.getenv('MQTT_PASS', '')

inverter = huawei_solar.HuaweiSolar(inverter_ip, port=502, slave=1)
inverter._slave = 1
inverter.wait = 1

#vars = ['state_1','state_2', 'state_3', 'alarm_1', 'alarm_2', 'alarm_3', 'pv_01_voltage', 'pv_01_current', 'pv_02_voltage','pv_02_current', 'input_power', 'grid_voltage', 
#'grid_current', 'day_active_power_peak', 'active_power', 'reactive_power', 
#'grid_frequency', 'efficiency', 'internal_temperature', 'insulation_resistance', 'device_status', 'fault_code', 'startup_time', 'shutdown_time', 'accumulated_yield_energy',
#'daily_yield_energy', 'grid_A_voltage', 'active_grid_A_current', 'power_meter_active_power', 
#'grid_exported_energy', 'grid_accumulated_energy']

#vars = ['alarm_1', 'pv_01_voltage', 'pv_01_current', 'pv_02_voltage','pv_02_current', 'input_power', 'grid_voltage', 
#'grid_current', 'day_active_power_peak', 'active_power', 'reactive_power', 
#'grid_frequency', 'efficiency', 'internal_temperature', 'insulation_resistance', 'device_status', 'fault_code', 'startup_time', 'shutdown_time', 'accumulated_yield_energy',
#'daily_yield_energy', 'grid_A_voltage', 'active_grid_A_current', 'power_meter_active_power', 
#'grid_exported_energy', 'grid_accumulated_energy']


def modbusAccess():

    vars_inmediate = ['pv_01_voltage', 'pv_01_current', 'pv_02_voltage','pv_02_current', 'input_power', 'grid_voltage', 
    'grid_current', 'active_power', 
    'grid_A_voltage', 'active_grid_A_current', 'power_meter_active_power']

    vars = ['day_active_power_peak', 'efficiency', 'internal_temperature', 'insulation_resistance', 'device_status', 'fault_code', 'accumulated_yield_energy',
    'daily_yield_energy', 'grid_exported_energy', 'grid_accumulated_energy']

    cont = 0
    while True:

        for i in vars_inmediate:
            try:
                mid = inverter.get(i)
                log.debug(i)
                log.debug(mid)
                log.debug("---")

                clientMQTT.publish(topic="emon/NodeHuawei/"+i, payload= str(mid.value), qos=1, retain=False)
            except:
                pass

        if(cont > 5):
            for i in vars:
                try:
                    mid = inverter.get(i)
                    log.debug(i)
                    log.debug(mid)
                    log.debug("---")

                    clientMQTT.publish(topic="emon/NodeHuawei/"+i, payload= str(mid.value), qos=1, retain=False)
                except:
                    pass

            cont = 0

        cont = cont + 1   
        time.sleep(1)

          
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        log.info("MQTT OK!")
    else:
        log.info("MQTT FAILURE. ERROR CODE: %s",rc)


paho.mqtt.client.Client.connected_flag=False#create flag in class

clientMQTT = paho.mqtt.client.Client()
clientMQTT.on_connect=on_connect #bind call back function
clientMQTT.loop_start()
log.info("Connecting to MQTT broker: %s:%s ",mqtt_host, mqtt_port)
clientMQTT.username_pw_set(mqtt_username,mqtt_password)
clientMQTT.connect(mqtt_host, mqtt_port) #connect to broker
while not clientMQTT.connected_flag: #wait in loop
    log.info("...")
time.sleep(1)
log.info("START MODBUS...")

modbusAccess()

clientMQTT.loop_stop()
