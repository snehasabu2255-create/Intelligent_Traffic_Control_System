import threading
import time
import cv2
import json
from flask import Flask, Response, jsonify, send_from_directory, request
from backend.vision import cameras
from backend.traffic_controller import controller

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

# Start the traffic controller in the background
controller.start()

def generate_frames(camera_name):
    """Generator for video streaming (now used to stream the static latest image)."""
    cam = cameras.get(camera_name)
    while True:
        frame = cam.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
            
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(1) # Send image update every 1s instead of 20 FPS

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/upload/<camera_name>', methods=['POST'])
def upload_image(camera_name):
    """Endpoint to receive uploaded images."""
    if camera_name not in cameras:
        return jsonify({"error": "Camera not found"}), 404
        
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
        
    file = request.files['image']
    image_bytes = file.read()
    
    # Process the image synchronously
    cam = cameras[camera_name]
    count, _ = cam.process_image(image_bytes)
    
    # Ensure upload endpoint explicitly sets the detected count on the camera object
    cam.current_count = count
    from backend.ml_model import predict_green_time
    allocated_time, _ = predict_green_time(count)
    cam.allocated_time = allocated_time
    
    return jsonify({"success": True, "count": count})

@app.route('/reset/<camera_name>', methods=['POST'])
def reset_camera(camera_name):
    """Endpoint to reset a camera state when image is closed."""
    if camera_name not in cameras:
        return jsonify({"error": "Camera not found"}), 404
        
    cam = cameras[camera_name]
    cam.reset()
    cam.allocated_time = 0
    
    # If the resetting road is currently active, instantly skip it
    state = controller.get_state()
    if state["active_camera"] == camera_name:
        controller.skip_current = True
        
    return jsonify({"success": True})

@app.route('/video/<camera_name>')
def video_feed(camera_name):
    """Route for video streaming the preview."""
    if camera_name not in cameras:
        return "Camera not found", 404
    return Response(generate_frames(camera_name), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/state_stream')
def state_stream():
    """Server-Sent Events (SSE) endpoint to push state updates to the frontend."""
    from backend.ml_model import predict_green_time
    def generate():
        while True:
            # Gather state from traffic controller
            state = controller.get_state()
            
            # Add current vehicle counts and instantly compute their densities
            counts = {}
            densities = {}
            allocated_times = {}
            for name, cam in cameras.items():
                count = cam.get_count()
                counts[name] = count
                allocated_time, density = predict_green_time(count)
                densities[name] = density
                allocated_times[name] = allocated_time
                
            state['counts'] = counts
            state['densities'] = densities
            state['allocated_times'] = allocated_times
            
            yield f"data: {json.dumps(state)}\n\n"
            time.sleep(1)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
