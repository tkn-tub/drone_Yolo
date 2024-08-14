# Tello Drone Control with Flask and YOLOv8

This project allows you to control a Tello drone using a Flask web interface. It includes real-time video streaming and object detection using YOLOv8. The drone can be controlled to follow a predefined flight path, and it tracks objects of a specific class in real-time.

## Features

- **Real-time Video Streaming**: View live video feed from the Tello drone.
- **Object Detection and Tracking**: Detect and track objects of class 49 using YOLOv8.
- **Flight Path Control**: Configure and execute predefined flight paths (e.g., square, circle, etc.) from the web interface.
- **Responsive Web Interface**: Control the drone and view real-time data using a responsive web interface.

## Requirements

To run this project, you need the following Python packages:

- Flask
- Flask-SocketIO
- djitellopy
- opencv-python-headless
- ultralytics (YOLOv8)
- numpy
- torch (Make sure to match the version with your hardware configuration)

You can install all required dependencies using:

```bash
pip install -r requirements.txt
```

## Setup Instructions
 - Clone the Repository
bash
Copy code
git clone https://github.com/yourusername/tello-flask-yolo.git
cd tello-flask-yolo
- Install Dependencies
Make sure you have Python installed. Then, install the necessary Python packages:

```bash
pip install -r requirements.txt
```

- Run the Application
Start the Flask application with:

```bash

python app.py
The application will be accessible at http://127.0.0.1:5000/ by default.
```

- Connect and Control the Tello Drone
Open the web interface in your browser.
Use the buttons to connect to the drone, start video streaming, and control the flight.
Configure the flight path and parameters (e.g., distance, radius, shape, speed) using the modal.
-  Stop the Application
To safely stop the application, you can press Ctrl + C in your terminal. The application ensures that all resources are cleaned up properly.

Notes
Ensure that your computer is connected to the Tello drone's Wi-Fi network before starting the application.
The YOLOv8 model used in this project is configured to detect objects of class 49. Modify the track_frame method in the VideoStreamThread class if you want to track different classes.
License
This project is licensed under the MIT License.


### Summary:

This `README.md` provides all the necessary details in a structured format, making it easy for users to understand, set up, and run your Tello drone project with Flask and YOLOv8. It covers features, requirements, setup instructions, notes, and licensing information.