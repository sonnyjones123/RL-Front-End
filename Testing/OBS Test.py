import obspython as obs
import websocket
import threading
import json

# Function to execute actions based on incoming commands
def execute_command(command):
    if command == "StartRecording":
        obs.obs_frontend_recording_start()
        obs.script_log(obs.LOG_INFO, "Recording started")
    elif command == "StopRecording":
        obs.obs_frontend_recording_stop()
        obs.script_log(obs.LOG_INFO, "Recording stopped")

# WebSocket event callback
def on_message(ws, message):
    obs.script_log(obs.LOG_INFO, "Decoding message")
    try:
        obs.script_log(obs.LOG_INFO, message)
        payload = json.loads(message)
        if "request-type" in payload:
            execute_command(payload["request-type"])
    except Exception as e:
        obs.script_log(obs.LOG_ERROR, f"WebSocket Error: {e}")

# Function description
def script_description():
    return "WebSocket Command Listener"

# Function to be called when the script is unloaded
def script_unload():
    obs.script_log(obs.LOG_INFO, "WebSocket Script: Unloading script")

# Define the WebSocket server URL (replace with your server address)
websocket_url = "ws://10.46.6.53:10005"  # Replace with your server address

# Start WebSocket listener
def start_websocket_listener():
    websocket.enableTrace(True)  # You can disable this for production use
    ws = websocket.WebSocketApp(websocket_url, on_message=on_message)
    ws.run_forever()

# Start the WebSocket listener in a separate thread
websocket_thread = threading.Thread(target=start_websocket_listener)
websocket_thread.daemon = True
websocket_thread.start()
obs.script_log(obs.LOG_INFO, "Starting WebSocket Listener")