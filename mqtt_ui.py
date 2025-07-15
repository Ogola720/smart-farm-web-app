import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import paho.mqtt.client as mqtt
import threading
import plotly.graph_objs as go
from collections import deque

# Global variables to store sensor data
sensor_data = {
    "humidity": "--",
    "temperature": "--",
    "soil_moisture": "--",
    "light_intensity": "--",
    "controls": "--"
}

# Historical data storage
history = {
    "humidity": deque(maxlen=50),
    "temperature": deque(maxlen=50),
    "soil_moisture": deque(maxlen=50),
    "light_intensity": deque(maxlen=50)
}

# MQTT Callback Functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
        client.subscribe("greenhouse/#")
    else:
        print(f"Failed to connect to MQTT broker, return code {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic.split("/")[-1]
    value = msg.payload.decode()
    if topic in sensor_data:
        sensor_data[topic] = value
        try:
            history[topic].append(float(value))
        except ValueError:
            pass

# MQTT Setup
def setup_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    threading.Thread(target=client.loop_forever).start()
    return client

mqtt_client = setup_mqtt()

# Dash App Setup
app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"])
app.title = "Greenhouse Sensor Dashboard"

# Layout of the Web Application
app.layout = html.Div([
    html.H1("Greenhouse Sensor Dashboard", className="text-center my-4"),
    
    # Sensor data display
    html.Div([
        html.Div([
            html.H3("Humidity"),
            html.H4(id="humidity-display", className="text-primary")
        ], className="col text-center"),
        html.Div([
            html.H3("Temperature"),
            html.H4(id="temperature-display", className="text-danger")
        ], className="col text-center"),
        html.Div([
            html.H3("Soil Moisture"),
            html.H4(id="soil-moisture-display", className="text-success")
        ], className="col text-center"),
        html.Div([
            html.H3("Light Intensity"),
            html.H4(id="light-intensity-display", className="text-warning")
        ], className="col text-center"),
        html.Div([
            html.H3("Controls Status"),
            html.H4(id="controls-display", className="text-secondary")
        ], className="col text-center"),
    ], className="row justify-content-center my-5"),

    # Graphs for historical data
    html.Div([
        html.Div([dcc.Graph(id="humidity-graph")], className="col-md-6"),
        html.Div([dcc.Graph(id="temperature-graph")], className="col-md-6"),
    ], className="row"),
    html.Div([
        html.Div([dcc.Graph(id="soil-moisture-graph")], className="col-md-6"),
        html.Div([dcc.Graph(id="light-intensity-graph")], className="col-md-6"),
    ], className="row"),

    # Controls section
    html.Div([
        html.H2("Controls", className="text-center my-4"),
        html.Div([
            html.Button("Sprinkler ON", id="sprinkler-on", className="btn btn-primary mx-2"),
            html.Button("Fan ON", id="fan-on", className="btn btn-info mx-2"),
            html.Button("Lights ON", id="lights-on", className="btn btn-warning mx-2"),
            html.Button("Heater ON", id="heater-on", className="btn btn-danger mx-2")
        ], className="d-flex justify-content-center")
    ]),

    # Interval component for updates
    dcc.Interval(id="update-interval", interval=2000)  # Updates every 2 seconds
], className="container")

# Callback to Update the Dashboard
@app.callback(
    [Output("humidity-display", "children"),
     Output("temperature-display", "children"),
     Output("soil-moisture-display", "children"),
     Output("light-intensity-display", "children"),
     Output("controls-display", "children"),
     Output("humidity-graph", "figure"),
     Output("temperature-graph", "figure"),
     Output("soil-moisture-graph", "figure"),
     Output("light-intensity-graph", "figure")],
    Input("update-interval", "n_intervals")
)
def update_dashboard(n):
    # Create figures
    humidity_fig = go.Figure(data=[go.Scatter(y=list(history["humidity"]), mode="lines", name="Humidity")])
    temperature_fig = go.Figure(data=[go.Scatter(y=list(history["temperature"]), mode="lines", name="Temperature")])
    soil_moisture_fig = go.Figure(data=[go.Scatter(y=list(history["soil_moisture"]), mode="lines", name="Soil Moisture")])
    light_intensity_fig = go.Figure(data=[go.Scatter(y=list(history["light_intensity"]), mode="lines", name="Light Intensity")])

    return (
        f"{sensor_data['humidity']} %",
        f"{sensor_data['temperature']} °C",
        sensor_data["soil_moisture"],
        sensor_data["light_intensity"],
        sensor_data["controls"],
        humidity_fig,
        temperature_fig,
        soil_moisture_fig,
        light_intensity_fig
    )

# Callback for Control Buttons
@app.callback(
    Input("sprinkler-on", "n_clicks"),
    Input("fan-on", "n_clicks"),
    Input("lights-on", "n_clicks"),
    Input("heater-on", "n_clicks")
)
def send_control_commands(sprinkler_clicks, fan_clicks, lights_clicks, heater_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    control_map = {
        "sprinkler-on": "sprinkler_on",
        "fan-on": "fan_on",
        "lights-on": "lights_on",
        "heater-on": "heater_on"
    }
    if button_id in control_map:
        mqtt_client.publish("greenhouse/controls", control_map[button_id])

# Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)
