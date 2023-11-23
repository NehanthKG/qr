import cv2
import numpy as np

# Global variables to store coordinates
pts = []
drawing = False

# Mouse callback function to get coordinates on click
def get_coordinates(event, x, y, flags, param):
    global pts, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        pts.append((x, y))
        drawing = True

# Create an OpenCV window and set mouse callback
cv2.namedWindow('Select ROI')
cv2.setMouseCallback('Select ROI', get_coordinates)

# File to store coordinates
file_path = 'coordinates.txt'

# Load coordinates from file (if file exists)
try:
    with open(file_path, 'r') as file:
        content = file.readlines()
        pts = [(int(p.split(',')[0]), int(p.split(',')[1])) for p in content]
except FileNotFoundError:
    pass

# Initialize video capture (change 0 to your camera index or video file)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if drawing:
        # Draw the temporary polygon based on the collected points
        if len(pts) > 1:
            cv2.polylines(frame, [np.array(pts)], True, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow('Select ROI', frame)

    # Check for key press
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        # Save coordinates to the file when exiting
        with open(file_path, 'w') as file:
            for point in pts:
                file.write(f"{point[0]},{point[1]}\n")
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
