import subprocess

# Replace 'YourCameraModel' with the actual model of your Nikon camera.
camera_model = 'YourCameraModel'

# Function to start video recording
def start_recording():
    subprocess.call(['gphoto2', '--port', 'usb:', '--set-config', 'movie=1'])

# Function to stop video recording
def stop_recording():
    subprocess.call(['gphoto2', '--port', 'usb:', '--set-config', 'movie=0'])

# Check the camera model and decide whether it's supported
camera_info = subprocess.check_output(['gphoto2', '--auto-detect']).decode('utf-8')
if camera_model in camera_info:
    print(f"Found {camera_model}. Starting recording...")
    start_recording()
    input("Press Enter to stop recording.")
    stop_recording()
    print("Recording stopped.")
else:
    print(f"Camera model {camera_model} not found or not supported.")
