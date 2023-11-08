import websocket
import json

# OBS WebSocket server URL (replace with your server address)
websocket_url = "ws://10.46.6.53:10005"  # Replace with your server address

# Function to send a command to OBS Studio
def send_command(command, websocket_url=websocket_url):
    try:
        ws = websocket.WebSocket()
        ws.connect(websocket_url)
        message = json.dump({"request-type":command})
        ws.send(message)
        ws.close()
        print(f"Sent command: {command}")
    except Exception as e:
        print(f"Error: {e}")

# Example commands:
send_command("StartRecording")
# send_command("StopRecording")
