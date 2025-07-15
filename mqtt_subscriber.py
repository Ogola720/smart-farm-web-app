import paho.mqtt.client as mqtt

# HiveMQ Broker Settings
broker = "broker.hivemq.com"
port = 1883  # Unsecured MQTT port

# MQTT Topics
topic_humidity = "greenhouse/humidity"
topic_temperature = "greenhouse/temperature"
topic_soilMoisture = "greenhouse/soilMoisture"
topic_lightIntensity = "greenhouse/lightIntensity"
topic_control = "greenhouse/control"

# Callback function when connecting to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
        # Subscribe to all relevant topics
        client.subscribe(topic_humidity)
        client.subscribe(topic_temperature)
        client.subscribe(topic_soilMoisture)
        client.subscribe(topic_lightIntensity)
        client.subscribe(topic_control)
    else:
        print(f"Failed to connect, return code {rc}")

# Callback function when a message is received
def on_message(client, userdata, msg):
    print(f"Message received -> Topic: {msg.topic}, Payload: {msg.payload.decode()}")

# Create an MQTT client instance
client = mqtt.Client()

# Assign the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
print("Connecting to broker...")
client.connect(broker, port, 60)

# Loop to keep the client running
client.loop_forever()