#! /usr/bin/env python3

import paho.mqtt.client as mqtt
from converter import read_datagram
from serial_reader import read_telegram
from time import sleep, time
from json import dumps

power_topic = 'home/power_meter'
mqtt_server = '10.0.0.10'
client_name = 'power_meter'
refresh_int = 60

def main():
    secs = time()
    mqtt_client = mqtt.Client(client_name)
    mqtt_client.connect(mqtt_server, 1883)
    max_time = refresh_int
    datagram = read_datagram(next(read_telegram()))
    gas      = datagram['gas_delivered']
    gas_old  = gas
    gas_time = datagram['gas_read_time_str']
    pwr      = datagram['tarif_1_delivered'] + datagram['tarif_2_delivered']
    pwr_old  = pwr
    pwr_time = datagram['date_time_str']
    pwr_avg  = None
    gas_avg  = None

    while True:   
        if time()-secs > max_time: 
            datagram = read_datagram(next(read_telegram()))
            if pwr_time != datagram['date_time_str']:
                pwr      = datagram['tarif_1_delivered'] + datagram['tarif_2_delivered']
                pwr_avg  = round((pwr - pwr_old)*(3600000/refresh_int),3) # convert from kWh to Ws
                pwr_old = pwr
            if gas_time != datagram['gas_read_time_str']:
                gas_time = datagram['gas_read_time_str']
                gas      = datagram['gas_delivered']
                gas_avg  = round((gas - gas_old)*(3600000/300),3) #gas refresh is 5 min
                gas_old = gas

             datagram['power_avg'] = pwr_avg # either None, old value or new value, dept on update
             datagram['gas_avg'] = gas_avg   # either None, old value or new value, dept on update
#            print('{:3} current_power {:10} last_power {:10} diff {}'.format(round(time()-secs), pwr  , pwr_old, pwr_avg))
#            print('{:3} current gas   {:10} last gas   {:10} diff {}'.format(round(time()-secs),gas, gas_old, gas_avg))
#            print(round(time()-secs), 'gas', gas_avg, 'power', pwr_avg)
#            print('gas {:10} power {:10}'.format(datagram['gas_avg'], datagram['power_avg']))
            print('{} total power {} total gas {} power used {} gas used {}'.format(datagram['date_time_str'], pwr, gas, pwr_avg, gas_avg)) 
            mqtt_client.publish(power_topic, dumps(datagram))
            secs = time()
        sleep(1)

if __name__ == '__main__':
    main()