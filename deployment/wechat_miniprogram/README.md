# WeChat Mini Program

This directory contains the WeChat Mini Program client for the quantum chemistry software.

## Architecture

The WeChat Mini Program uses a client-server architecture:
1. The Mini Program provides the user interface
2. API server handles quantum chemistry calculations
3. WebView component displays 3D visualizations

## Setup

1. Import this project in the WeChat Developer Tools
2. Configure the API endpoint in `config.js`
3. Run in the simulator or on a real device

## Files Structure

- `pages/`: Mini Program pages
- `components/`: Reusable components
- `utils/`: Utility functions
- `services/`: API services
- `images/`: Images and icons
