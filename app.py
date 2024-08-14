import threading
import cv2
import time
import base64
import collections
import atexit
import signal
import numpy as np
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from djitellopy import Tello
from ultralytics import YOLO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

# Global variables for Tello drone and video streaming threads
tello = None
video_thread = None
video_processing_thread = None

# Set to store unique IDs of detected objects
unique_objects = set()

# Deque to store the last 95 latency values for calculating average latency
latency_history = collections.deque(maxlen=95)

# Thread class for handling video stream from the Tello drone
class VideoStreamThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stopped = threading.Event()
        # Load YOLO model for object detection
        self.model = YOLO("yolov8m.pt")

    def run(self):
        global tello
        while not self.stopped.is_set() and tello:
            try:
                # Capture frame from Tello drone
                frame = tello.get_frame_read().frame
                if frame is not None:
                    # Process frame to track objects
                    frame, count = self.track_frame(frame)
                    if frame is not None:
                        # Convert frame to BGR color format (if necessary)
                        if isinstance(frame, np.ndarray) and frame.shape[2] == 3:
                            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        # Encode frame as JPEG
                        ret, buffer = cv2.imencode('.jpg', frame)
                        if ret:
                            frame_bytes = buffer.tobytes()
                            # Encode the image to base64 for transmission
                            jpg_as_text = base64.b64encode(frame_bytes).decode('utf-8')
                            # Emit the processed frame to the client
                            socketio.emit('video_frame', {'image_data': jpg_as_text, 'count': count}, namespace='/')
            except Exception as e:
                print(f"Error in video stream thread: {e}")

    def stop(self):
        self.stopped.set()

    def track_frame(self, frame):
        global unique_objects
        try:
            # Track objects in the frame using YOLO model with ByteTrack
            results = self.model.track(frame, persist=True, device="mps", classes=[49] )
            if not results:
                raise ValueError("No results returned from the model")
            result = results[0]
            if result.boxes and result.boxes.id:
                # Update unique object IDs set
                unique_ids = set(result.boxes.id.cpu().numpy())
                unique_objects.update(unique_ids)
            # Annotate the frame with detected objects
            annotated_frame = result.plot()
            return annotated_frame, len(unique_objects)
        except Exception as e:
            print(f"Error in track_frame: {e}")
            return frame, len(unique_objects)

# Flask route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to start video stream from the drone
@app.route('/start_stream', methods=['POST'])
def start_stream():
    global tello, video_thread
    if not tello:
        tello = Tello()
    try:
        # Start video stream from Tello drone
        tello.streamon()
        video_thread = VideoStreamThread()
        video_thread.start()
        return jsonify({'message': 'Video streaming started.'}), 200
    except Exception as e:
        print(f"Error starting video stream: {e}")
        return jsonify({'message': 'Error starting video stream', 'error': str(e)}), 500

# SocketIO event to stop the video stream
@socketio.on('stop_stream', namespace='/')
def stop_stream():
    global tello, video_thread
    if tello:
        try:
            # Stop video stream from Tello drone
            tello.streamoff()
            if video_thread:
                video_thread.stop()
            emit('status', {'message': 'Video streaming stopped.'})
        except Exception as e:
            print(f"Error stopping video stream: {e}")

# SocketIO event to connect to the Tello drone
@socketio.on('connect_drone', namespace='/')
def connect_drone():
    global tello
    if not tello:
        tello = Tello()
    try:
        # Connect to Tello drone
        tello.connect()
        emit('drone_connected', {'message': 'Drone connected successfully'})
    except Exception as e:
        print(f"Error connecting to drone: {e}")

# Flask route to handle commands for the drone (takeoff, land, move, etc.)
@app.route('/command_handler', methods=['POST'])
def command_handler():
    global tello, video_thread
    command = request.json.get('command')
    distance = request.json.get('distance')
    radius = request.json.get('radius')
    shape = request.json.get('shape')
    speed = request.json.get('speed')
    response_message = 'Command executed successfully.'

    try:
        if command == 'connect':
            if not tello:
                tello = Tello()
            tello.connect()
            response_message = 'Drone connected successfully.'
        elif command == 'start_stream':
            if not tello:
                tello = Tello() 
            tello.streamon()
            if not video_thread or not video_thread.is_alive():
                video_thread = VideoStreamThread()
                video_thread.start()
            response_message = 'Video streaming started.'
        elif command == 'stop_stream':
            if tello:
                tello.streamoff()
                if video_thread:
                    video_thread.stop()
            response_message = 'Video streaming stopped.'
        elif tello:
            # Handle drone movement commands
            if command == 'takeoff':
                tello.takeoff()
            elif command == 'land':
                tello.land()
            elif command.startswith('move'):
                direction, distance = command.split()[1], int(command.split()[2])
                if direction == 'up':
                    tello.move_up(distance)
                elif direction == 'down':
                    tello.move_down(distance)
                elif direction == 'left':
                    tello.move_left(distance)
                elif direction == 'right':
                    tello.move_right(distance)
                elif direction == 'forward':
                    tello.move_forward(distance)
                elif direction == 'back':
                    tello.move_back(distance)
            elif command == 'start_flight':
                response_message = start_flight_path(distance, radius, shape, speed)
            else:
                response_message = 'Unknown command.'
        else:
            response_message = 'Drone not connected.'
    except Exception as e:
        response_message = f'Error executing command: {e}'

    return jsonify({'message': response_message}), 200

# Function to execute a predefined flight path for the drone
def start_flight_path(distance, radius, shape,speed):
    global tello, video_thread
    try:
        # Step 1: Check and connect to the drone
        if not tello:
            tello = Tello()
        tello.connect()

        # Step 3: Take off
        tello.takeoff()

        # Wait for IMU to initialize
        time.sleep(3)
        if (int(distance) > 19):
            tello.move_forward(int(distance))
            time.sleep(2)

       

        # Define the movement parameters based on shape
        if shape == 'square':
            sides = 4
        elif shape == '10_faces':
            sides = 10
        elif shape == '12_faces':
            sides = 12
        elif shape == 'circle':
            sides = 100  # Approximating a circle with small steps

        # Movement calculation
        speed = 15  # Speed in cm/s
        yaw_rate = 360 / 12  # Yaw rate to create the desired shape
        duration = 3  # Time to move for each leg

        # Loop through each side of the polygon
        for _ in range(sides):
            # Move forward (relative to the current orientation)
            tello.send_rc_control(speed, 0, 0, 0)
            time.sleep(duration)
            tello.send_rc_control(0, 0, 0, 0)  # stop
            time.sleep(1)  # brief pause before turning

            # Turn to create the desired shape
            tello.rotate_counter_clockwise(int(yaw_rate))

        # Land the drone after completing the polygon
        tello.land()

        return 'Flight path executed successfully.'
    except Exception as e:
        return f'Error executing flight path: {e}'

# Cleanup function to ensure resources are released when the app stops
def cleanup():
    global video_thread, video_processing_thread
    if video_thread:
        video_thread.stop()
        video_thread.join()
    if video_processing_thread:
        video_processing_thread.stop()
        video_processing_thread.join()
    if tello:
        tello.end()

# Register cleanup function to be called when the app exits
atexit.register(cleanup)

# Signal handler for clean exit on SIGTERM
def handle_sigterm(*args):
    cleanup()
    raise SystemExit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

# Main entry point to start the Flask app with SocketIO
if __name__ == '__main__':
    socketio.run(app)
