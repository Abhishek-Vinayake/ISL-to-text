# Real-time Indian Sign Language recognition system using MediaPipe and temporal deep learning, achieving low-latency predictions via WebSocket streaming.
Real-time Indian Sign Language (ISL) gesture recognition application powered by deep learning and web-based video streaming.

## Problem Statement
Indian Sign Language (ISL) serves as the primary mode of communication for the deaf and hard-of-hearing community in India. However, the communication barrier between ISL users and those unversed in the language remains significant. This project bridges that gap by providing a real-time, browser-based translation tool that interprets continuous ISL gestures into text, fostering accessibility and independent communication.

## Key Features
- **Real-Time Gesture Inference**: Predicts continuous ISL gestures with real-time confidence scoring using a temporal sequence model.
- **Low-Latency Streaming**: Utilizes WebSockets for bidirectional, low-latency transmission of video frames from the browser to the inference server.
- **Holistic Landmark Extraction**: Precisely tracks 138 spatial landmarks points across hand and shoulder pose coordinates using MediaPipe Holistic.
- **Jitter-Free Predictions**: Implements temporal smoothing (`PredictionSmoother`) to filter out micro-fluctuations and stabilize output labels.

## System Architecture

```text
User Input (Webcam Video Stream) → Processing Module (WebSocket Server & MediaPipe Feature Extraction) → Model/Logic (TensorFlow Sequence Inference & Temporal Smoothing) → Output (Frontend React Overlay)
```

The system architecture consists of a React-based frontend client handling media devices and a FastAPI backend operating as the AI inference engine. 
- The client captures frames and transmits them rapidly over WebSockets as base64-encoded JPEGs.
- The backend decodes the stream, applies MediaPipe Holistic to extract a 138-dimensional vector representing skeletal landmarks, and aggregates these features into a rolling sequence buffer (32 frames).
- The buffered sequence is fed into a Keras model (`isl_gesture_model.h5`), which predicts the gesture. Support classes (`PredictionSmoother`) eliminate noise before echoing the predicted label back to the frontend.

## Tech Stack
**Frontend:**
- React (v18.3.1)
- Vite build tool
- TailwindCSS (Styling, PostCSS, Autoprefixer)

**Backend:**
- FastAPI (Web framework and WebSocket handling)
- Uvicorn (ASGI server)
- TensorFlow & Keras (Model inference engine)
- MediaPipe (Holistic landmark tracking)
- OpenCV-Python (Image processing and decoding)
- NumPy (Tensor reshaping and manipulation)
- Pydantic (Data validation)

## How It Works (Execution Flow)
1. **Video Initialization**: The frontend user activates the camera in `WebcamPanel.jsx` using `navigator.mediaDevices.getUserMedia`.
2. **WebSocket Handshake**: `usePredictionSocket.js` establishes a live connection to `ws://127.0.0.1:8000/ws/predict`.
3. **Frame Transmission**: The client draws the video frame to a hidden `<canvas>`, encodes it as base64 JPEG, and streams it to the backend every 100ms.
4. **Decoding & Extraction**: The FastAPI endpoint in `main.py` decodes the base64 payload into a NumPy array and reads it via `cv2.imdecode`.
5. **Holistic Landmark Mapping**: `inference.py` processes the frame through MediaPipe Holistic, extracting exactly 138 spatial points representing left hand, right hand, palms, and shoulders.
6. **Sequence Buffering**: The feature vector is appended to a fixed-length `deque` (32 frames).
7. **Model Prediction**: Once the buffer fills, the temporal vector is fed into the Keras `.h5` model to determine raw gesture probabilities.
8. **Temporal Smoothing**: The raw prediction routes through `utils.py:PredictionSmoother`, which applies a sliding window to cast majority votes, producing a stabilized `label` and `confidence` rating.
9. **UI Refrain**: The JSON payload containing the prediction details is emitted back over WebSocket. `PredictionOverlay.jsx` / `WebcamPanel.jsx` receives the data and dynamically renders a progress bar representing confidence.

## Installation & Setup

### Requirements
- Node.js (v18+)
- Python (3.9+)

### Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Usage Examples

**Starting the Application:**
After starting both the frontend and backend servers, navigate to `http://localhost:5173`. Click the "Start" or "Enable Webcam" button to initiate the WebSocket connection. 

**Interacting with the Application:**
Perform a trained ISL gesture in front of the camera (e.g., ensuring hands and shoulders are fully visible framing). The UI will overlay data in real-time, for example:
- **Prediction**: "HELLO"
- **Confidence**: 98.4%
The confidence bar will smoothly dynamically track your movement accuracy.

## Project Structure
```text
ISL_txt/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entry point, WebSocket routing
│   │   ├── inference.py           # Feature extraction logic & sequence manipulation
│   │   ├── utils.py               # Smoothing algorithms and FPS counters
│   │   └── model_loader.py        # Alternative TFLite model loader instance
│   └── requirements.txt           # Python dependency manifests
└── frontend/
    ├── src/
    │   ├── components/            # UI pieces
    │   │   └── WebcamPanel.jsx    # Hardware interfacing and UI container for feedback
    │   ├── hooks/
    │   │   └── usePredictionSocket.js # WebSocket event loop and frame transmitter
    │   └── App.jsx                # Application root
    ├── package.json               # Node dependency declarations
    └── tailwind.config.js         # Tailwind styling guidelines
```

## Limitations
- **Sequence Bottleneck**: The system strictly relies on exactly 32 frames of continuous data before generating an inference. Jitter may occur if the user gestures faster or slower than the trained sequence pacing.
- **Resource Intensity**: Real-time extraction of 138 landmarks via MediaPipe Holistic alongside WebSockets puts notable pressure on CPU and memory, potentially lagging on lower-end machines.
- **Lighting and Framing**: The MediaPipe backend struggles when hands overlap severely or under poor lighting conditions, leading to zero-filled vectors and false negatives.

## Future Improvements
- **Dynamic Sequence Handling**: Migrate from fixed 32-frame boundaries to dynamic sequence detection (e.g., using CTC loss or Transformer heads) to allow for variable speed signing.
- **Model Quantization**: Completely transition inference workloads to the `isl_gesture_model.tflite` currently sitting idle in `model_loader.py` to vastly improve inference latency and diminish overall compute loads.
- **WebRTC Implementation**: Replace WebSockets base64 transmission with a native WebRTC video track workflow for significantly reduced networking payload and lag.

## Why This Project Matters
- **Demonstrates End-to-End System Design**: Successfully integrates asynchronous Python backends (FastAPI) with modern client-side React rendering (Vite).
- **Showcases Real-Time Machine Learning**: Highlights the ability to process dense multidimensional data (138-d vectors) through continuous sequence Keras models without hanging the main application thread.
- **Emphasizes Practical Problem Solving**: Addresses jittering predictions by writing custom temporal smoothing logics (`PredictionSmoother`), proving the ability to optimize raw ML output into a user-friendly product.
