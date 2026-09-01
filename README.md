# 🚦 Intelligent Traffic Control System

An advanced, AI-powered traffic management solution designed to optimize traffic light timings dynamically using computer vision. By analyzing real-time video feeds or images, the system accurately estimates vehicle density and intelligently allocates green-light duration for different lanes, minimizing congestion and improving overall traffic flow.

## 🌟 Features
- **Dynamic Time Allocation:** Replaces traditional static timers with dynamic green-light allocation based on real-time vehicle counts.
- **Real-Time Vehicle Detection:** Utilizes the state-of-the-art **YOLOv8** model to accurately detect and classify vehicles (cars, motorcycles, buses, trucks).
- **Multi-Camera Support:** Handles feeds from multiple directions (North, South, East, West) concurrently.
- **Live Monitoring Dashboard:** A responsive web interface that streams real-time updates of vehicle counts, traffic density, and active lanes using Server-Sent Events (SSE).
- **Zero-Wait Optimization:** Instantly skips green lights for lanes with zero detected vehicles.

## 🏗 System Architecture
The system consists of three main components:
1. **Computer Vision Module:** Uses YOLOv8 (via PyTorch and OpenCV) to process frames, draw bounding boxes, and calculate accurate vehicle counts.
2. **Traffic Controller:** A background daemon that maintains the state of the intersection, executing heuristic algorithms to convert vehicle density (Low, Medium, High, Severe) into optimal time allocations (ranging from 0s to 120s).
3. **Web Server & Dashboard:** A Flask backend that exposes REST endpoints for uploads and SSE streams to a vanilla JavaScript/HTML frontend for live monitoring.

## 🛠 Tech Stack
- **Machine Learning / Computer Vision:** YOLOv8, OpenCV, PyTorch, NumPy
- **Backend Framework:** Python, Flask
- **Real-time Communication:** Server-Sent Events (SSE)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)

## 📋 Prerequisites
- Python 3.8+
- PyTorch (Compatible with your CUDA version for GPU acceleration)
- OpenCV
- Flask
- Ultralytics (for YOLOv8)

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Intelligent-Traffic-Control-System.git
   cd Intelligent-Traffic-Control-System
   ```

2. **Create a virtual environment (Optional but highly recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   *(Ensure you have a `requirements.txt` generated, or install manually)*
   ```bash
   pip install Flask opencv-python numpy ultralytics torch
   ```

4. **Download YOLOv8 Weights:**
   Ensure the `yolov8n.pt` model is placed in the root directory. If missing, it will automatically download upon the first execution.

## 💻 Usage

1. **Start the application server:**
   ```bash
   python backend/app.py
   ```

2. **Access the Live Dashboard:**
   Open your preferred web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. **Simulate Traffic Feeds:**
   Use the frontend interface to upload sample images or connect video streams for the North, South, East, and West cameras. The backend will process the images, and the dashboard will dynamically adjust and reflect the optimized traffic signals.

## 📁 Project Structure
```text
Intelligent_Traffic_Control_System/
├── backend/
│   ├── app.py                 # Flask server and API/SSE endpoints
│   ├── ml_model.py            # Density & green-time prediction logic
│   ├── traffic_controller.py  # Background traffic state management
│   └── vision.py              # YOLOv8 integration and image processing
├── frontend/
│   ├── index.html             # Dashboard UI structure
│   ├── style.css              # Application styling
│   └── script.js              # SSE handling and dynamic UI updates
├── data/                      # Sample datasets and testing images
├── yolov8n.pt                 # Pre-trained YOLOv8 model weights
└── README.md                  # Project documentation
```

## 🔮 Future Enhancements
- **Emergency Vehicle Override:** Implement audio and visual detection for sirens/emergency lights to instantly grant right-of-way.
- **Reinforcement Learning:** Transition from heuristic timers to a Deep Q-Network (DQN) for continuously learning optimal timing policies.
- **Multi-Intersection Synchronization:** Scale the system to communicate with adjacent intersections, creating a "green wave" effect across city corridors.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/Intelligent-Traffic-Control-System/issues).

## 📄 License
This project is licensed under the MIT License.
