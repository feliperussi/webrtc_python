# WebRTC Webcam Demo

This repository contains a WebRTC webcam demo using Python, aiohttp, and aiortc. The server application streams video from the host's webcam to a web client.

## Requirements

- Docker
- A webcam

## Setup Instructions

### 1. Clone the Repository

Clone the repository to your local machine:

```sh
git clone <repository-url>
cd <repository-directory>
```

### 2. Create `requirements.txt`

Create a `requirements.txt` file with the following contents:

```text
aiohttp==3.9.5
aiohttp-cors==0.7.0
aiortc==1.9.0
```
### 3. Build the Docker Image

Build the Docker image using the following command:

```sh
docker build -t webrtc-webcam-demo .
```

### 4. Run the Docker Container

Run the Docker container with access to the host's webcam:

```sh
docker run --device=/dev/video0 -p 8080:8080 webrtc-webcam-demo
```

### 5. Access the Web Application

Open your web browser and navigate to `http://localhost:8080` to access the WebRTC webcam demo.

## Files in the Repository

- `server.py`: The main server application.
- `index.html`: The HTML file for the web client.
- `client.js`: The JavaScript file for the web client.
- `requirements.txt`: The file specifying the Python dependencies.
- `Dockerfile`: The Docker configuration file.

## Notes

- Make sure your webcam is connected and accessible via `/dev/video0`. Adjust the device path if your webcam is located at a different path.
- The application listens on port 8080 by default. You can change the port by modifying the `docker run` command and the `Dockerfile` if necessary.