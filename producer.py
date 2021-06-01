from json import dumps
from serial import Serial

import paho.mqtt.client as mqtt

from time import sleep
from settings import Settings
from multiprocessing import Process, Queue

import settings


class SerialWorker:
    def __init__(
        self, 
        header: int,
        port: Serial, 
        output: Queue, 
        sleep_time: float = 0.01
    ):
        self._header = header
        self._output_queue = output
        self._sleep_time = sleep_time
        self._uart = port
        self._buffer = []

    def process_buffer(self):
        try:
            index = self._buffer.index(header)
            lenght = self._buffer[index+1]
            message_end = index + lenght + 3
            sub_buffer = self._buffer[index:message_end]
            self._buffer = self._buffer[message_end::]
            payload = sub_buffer[2:-1]
            output = {}
            for i in range(int(len(payload)/3)):
                output[hex(payload[i * 3])] =  (payload[(i * 3) + 1] << 8) | (payload[(i * 3) + 2])
            return output
        except (ValueError,IndexError) as e:
            return {}

    def _target(self):
        while True:
            input = self._uart.read_all()
            if input:
                self._buffer += input
                output = self.process_buffer(buffer=self._buffer, header=self._header)
                if output:
                    print(f"Message added to Queue:{output}")
                    self._output_queue.put(output)        
            sleep()

    def run(self):
        Process(target=self._target)
    

settings = Settings()

mqtt_client = mqtt.Client()
mqtt_client.connect(
    host=settings.MQTT_BROKER, 
    port=settings.MQTT_PORT
)


port = Serial(
    port=settings.SERIAL_PORT, 
    baudrate=settings.SERIAL_BAUDRATE
)

header = 0x7E
buffer = []

def process_buffer(buffer: list, header: int):
    try:
        index = buffer.index(header)
        lenght = buffer[index+1]
        message_end = index + lenght + 3
        sub_buffer = buffer[index:message_end]
        buffer = buffer[message_end::]
        return buffer, sub_buffer
    except (ValueError,IndexError) as e:
        return buffer, None 

header = 0x7E
buffer = []

while True:
    input = port.read_all()
    if input:
        buffer += input
        buffer, datapack = process_buffer(buffer=buffer, header=header)
        if datapack:
            payload = datapack[2:-1]
            output = {}
            for i in range(int(len(payload)/3)):
                output[hex(payload[i * 3])] =  (payload[(i * 3) + 1] << 8) | (payload[(i * 3) + 2])
            print(output)
            mqtt_client.publish(
                topic="sda/sensor2",
                payload=dumps(output)
            )
    sleep(0.01)
    
