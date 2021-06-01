import paho.mqtt.client as mqtt
import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("sda/sensor2")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    #print(msg.topic+" "+str(msg.payload))
    payload= (msg.payload).decode()
    payload_dict = json.loads(payload)
    #print(payload_dict)
    
    with open('data.txt','a+', newline='') as f:
        
        for key, value in payload_dict.items():
            f.write(f"{value}, {key}, ")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()