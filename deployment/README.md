# Quantum Chemistry Software Deployment Guide

This directory contains deployment tools and configurations for multiple platforms:

1. Web: Streamlit-based web application
2. Mobile: React Native app for iOS and Android
3. Desktop: Electron app for macOS, Windows, and Linux
4. WeChat Mini Program: Client for WeChat platform
5. API Server: REST API to power mobile and WeChat apps

## Deployment Architecture

The deployment architecture varies based on platform:

### Desktop App (macOS, Windows, Linux)
- Full integration with Python backend code
- Local computation without requiring an internet connection
- Direct file system access

### Web App (Streamlit)
- Server-side computation
- Web-based visualization
- Easy to deploy on cloud platforms (Heroku, AWS, GCP)

### Mobile Apps (iOS & Android)
- Client-server architecture
- UI built with React Native
- Communicates with API server for calculations
- Local visualization using WebView with 3Dmol.js

### WeChat Mini Program
- Client-server architecture
- UI built using WeChat Mini Program framework
- Communicates with API server for calculations
- Visualization through WebView component

## Deployment Instructions

### Web App (Streamlit)

1. Install requirements:
```bash
cd deployment/streamlit
pip install -r streamlit_requirements.txt
```

2. Run the app:
```bash
streamlit run streamlit_app.py
```

3. Deploy to Streamlit Cloud:
   - Create an account on [Streamlit Sharing](https://streamlit.io/sharing)
   - Connect your GitHub repository
   - Select the `deployment/streamlit_app.py` as the main file

### API Server

1. Install requirements:
```bash
cd deployment/api_server
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

3. Deploy to cloud:
```bash
# Heroku
heroku create quantum-chemistry-api
git subtree push --prefix deployment/api_server heroku main

# Docker
docker build -t quantum-chemistry-api .
docker run -p 8000:8000 quantum-chemistry-api
```

### Mobile App (React Native)

1. Install dependencies:
```bash
cd deployment/mobile_app
npm install
```

2. Run for development:
```bash
npm start
```

3. Build for iOS:
```bash
npm run build:ios
```

4. Build for Android:
```bash
npm run build:android
```

### Desktop App (Electron)

1. Install dependencies:
```bash
cd deployment/desktop_app
npm install
```

2. Run for development:
```bash
npm start
```

3. Build for production:
```bash
# For macOS
npm run build:mac

# For Windows
npm run build:win

# For Linux
npm run build:linux
```

### WeChat Mini Program

1. Import the project:
   - Open WeChat Developer Tools
   - Import the `deployment/wechat_miniprogram` directory
   - Configure the API endpoint in `config.js`

2. Preview in simulator or on device:
   - Use the preview feature in WeChat Developer Tools
   - Scan the QR code with WeChat to test on a real device

3. Release:
   - Submit for review in the WeChat Developer Tools
   - After approval, publish to the WeChat ecosystem

## API Documentation

The REST API provides the following endpoints:

- `POST /optimize`: Start a geometry optimization job
- `GET /jobs/{job_id}`: Get the status of a job
- `GET /files/{job_id}/{filename}`: Get a file from a job
- `GET /visualize/{job_id}`: Get visualization for a job
- `POST /visualize/upload`: Visualize an uploaded trajectory file
- `GET /molecules`: Get a list of example molecules

For full API documentation, visit `/docs` when the API server is running.
