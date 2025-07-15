import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import paho.mqtt.client as mqtt
import threading

# Global variables to store sensor data
sensor_data = {
    "humidity": "--", 
    "temperature": "--", 
    "soil_moisture": "--", 
    "light_intensity": "--", 
    "controls": "--"
}

# MQTT Callback Functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
        # Subscribe to all topics under "greenhouse/"
        client.subscribe("greenhouse/#")
    else:
        print(f"Failed to connect to MQTT broker, return code {rc}")

def on_message(client, userdata, msg):
    global sensor_data
    # Extract the last part of the topic (e.g., humidity, temperature, soil_moisture)
    topic = msg.topic.split("/")[-1]
    value = msg.payload.decode()  # Decode the message
    if topic in sensor_data:
        sensor_data[topic] = value  # Update sensor data

# MQTT Client Setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to a public broker (replace this if using your own broker)
broker = "broker.hivemq.com"
port = 1883
mqtt_client.connect(broker, port, 60)

# Run MQTT client loop in a separate thread to avoid blocking the Dash app
threading.Thread(target=mqtt_client.loop_forever).start()

# Dash App Setup
app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"])
app.title = "Greenhouse Sensor Dashboard"

# Layout of the Web Application
app.layout = html.Div([
    html.H1("Greenhouse Sensor Dashboard", className="text-center my-4"),
    html.Div([
        html.Div([
            html.H3("Humidity"),
            html.H4(id="humidity-display", children="-- %", className="text-primary")
        ], className="col text-center"),
        html.Div([
            html.H3("Temperature"),
            html.H4(id="temperature-display", children="-- °C", className="text-danger")
        ], className="col text-center"),
        html.Div([
            html.H3("Soil Moisture"),
            html.H4(id="soil-moisture-display", children="--", className="text-success")
        ], className="col text-center"),
        html.Div([
            html.H3("Light Intensity"),
            html.H4(id="light-intensity-display", children="--", className="text-warning")
        ], className="col text-center"),
        html.Div([
            html.H3("Controls Status"),
            html.H4(id="controls-display", children="--", className="text-secondary")
        ], className="col text-center"),
    ], className="row justify-content-center my-5")
], className="container")

# Callback to Update the Dashboard
@app.callback(
    [Output("humidity-display", "children"),
     Output("temperature-display", "children"),
     Output("soil-moisture-display", "children"),
     Output("light-intensity-display", "children"),
     Output("controls-display", "children")],
    [Input("humidity-display", "id")]  # Dummy input to trigger the callback
)
def update_dashboard(_):
    # Return the current values of the sensors
    return (
        f"{sensor_data['humidity']} %",
        f"{sensor_data['temperature']} °C",
        sensor_data["soil_moisture"],
        sensor_data["light_intensity"],
        sensor_data["controls"]
    )

# Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)
