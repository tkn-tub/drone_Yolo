import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from djitellopy import Tello
from aiModel import processFrame, trackFrame

class TelloGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tello Drone Control")

        self.orange_count = 0

        # Initialize Tello drone object
        self.tello = Tello()

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Connect button
        self.connect_button = ttk.Button(self.root, text="Connect to Drone", command=self.connect_to_drone)
        self.connect_button.grid(row=0, column=0, pady=10, padx=10)

        # Stream On button
        self.stream_on_button = ttk.Button(self.root, text="Stream On", command=self.start_stream)
        self.stream_on_button.grid(row=0, column=1, pady=10, padx=10)

        # Stream Off button
        self.stream_off_button = ttk.Button(self.root, text="Stream Off", command=self.stop_stream)
        self.stream_off_button.grid(row=0, column=2, pady=10, padx=10)

        # Take Off button
        self.takeoff_button = ttk.Button(self.root, text="Take Off", command=self.takeoff)
        self.takeoff_button.grid(row=1, column=0, pady=10, padx=10)

        # Land button
        self.land_button = ttk.Button(self.root, text="Land", command=self.land)
        self.land_button.grid(row=1, column=1, pady=10, padx=10)

        # Perform Route button
        self.route_button = ttk.Button(self.root, text="Perform Route", command=self.perform_route)
        self.route_button.grid(row=1, column=2, pady=10, padx=10)

        # Video Label for stream
        self.video_label = ttk.Label(self.root)
        self.video_label.grid(row=2, column=0, columnspan=3, pady=10, padx=10)

    def connect_to_drone(self):
        # Connect to the Tello drone
        self.tello.connect()
        print("Connected to Tello Drone")

    def start_stream(self):
        # Start video stream
        self.tello.streamon()
        self.show_video_stream()
        print("Video Stream Started")

    def stop_stream(self):
        # Stop video stream
        self.tello.streamoff()
        print("Video Stream Stopped")

    def takeoff(self):
        # Take off
        self.tello.takeoff()
        print("Drone Took Off")

    def land(self):
        # Land
        self.tello.land()
        print("Drone Landed")

    def perform_route(self):
        # Perform a 360-degree turn with a pace of 1 second per 10 degrees
        self.takeoff()
        for _ in range(36):
            self.tello.rotate_clockwise(10)
            self.root.after(1000)  # Wait for 1 second
        self.land()
        print("Performed 360-degree Route")

    def show_video_stream(self):
        # Get frame and count of oranges from the video stream
        frame = trackFrame(self.tello.get_frame_read().frame)

        # Convert frame to PIL format
        image = Image.fromarray(frame)

        # Convert PIL image to Tkinter PhotoImage
        photo = ImageTk.PhotoImage(image)

        # Update the video label with the new frame
        self.video_label.img = photo
        self.video_label.configure(image=photo)

        # Schedule the next frame update (every 30 milliseconds)
        self.root.after(30, self.show_video_stream)

def main():
    root = tk.Tk()
    app = TelloGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
