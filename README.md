# Air Sculpting 

Air Sculpting is a futuristic, gesture-controlled 3D modeling and exploration interface. It leverages computer vision and AI to let users manipulate 3D objects in real-time through a web browser, without touching a mouse or keyboard. 

## Features

- **Gesture Control**: Use intuitive hand signs (Pinch, Fist, Rotate, Extrude, Idle) to interact with the environment.
- **Real-Time 3D Rendering**: Built with React, Three.js, and React Three Fiber for a smooth, hardware-accelerated 3D experience.
- **AI Backend**: Python-based backend using OpenCV, MediaPipe, and TensorFlow/Keras for blazing-fast hand tracking and gesture recognition.
- **WebSocket Streaming**: Seamless, low-latency communication between the AI computer vision engine and the frontend UI.
- **Holographic Aesthetics**: Designed with premium, futuristic aesthetics inspired by modern sci-fi interfaces.

## Tech Stack

### Frontend
- **React.js** + **Vite**
- **Three.js** / **React Three Fiber** (R3F)
- **React Three Drei** (for environment and controls)

### Backend
- **Python 3**
- **FastAPI** + **WebSockets**
- **OpenCV** (Camera integration)
- **MediaPipe** (Hand tracking)
- **TensorFlow / Keras** (Custom Gesture Classification Model)

## Setup & Installation

*Instructions for running the local dev servers (Vite + Uvicorn) will be added here as the project matures.*

## Future Roadmap

- [ ] Smooth delta-based rotation with Kalman/EMA jitter filtering
- [ ] Multi-model carousel (Swipe to switch objects)
- [ ] Real-time object deformation (True Sculpting)
- [ ] UI control panels navigable via gestures

---

