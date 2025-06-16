# Quantum Chemistry Mobile App

This directory contains the React Native project for the mobile app that interfaces with the quantum chemistry backend.

## Architecture

The mobile app uses a client-server architecture where:
1. The React Native app provides the user interface
2. Backend calculations run on a server (REST API)
3. Visualization is done client-side using WebView with 3Dmol.js

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm start
```

3. Run the app on iOS:
```bash
npm run ios
```

4. Run the app on Android:
```bash
npm run android
```

## Project Structure

- `src/screens/`: App screens (Home, Optimization, Visualization)
- `src/components/`: Reusable UI components
- `src/services/`: API services for backend communication
- `src/utils/`: Utility functions
- `src/assets/`: Images, icons, and other static assets
