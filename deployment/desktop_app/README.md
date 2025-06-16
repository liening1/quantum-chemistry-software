# Quantum Chemistry Desktop App

This directory contains the Electron app for desktop platforms (macOS, Windows, Linux).

## Features

- Full integration with local quantum chemistry calculations
- Direct file access without server requirements
- Interactive 3D visualization with 3Dmol.js
- Support for all quantum chemistry functions in the core library

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run the development version:
```bash
npm start
```

3. Build for production:
```bash
npm run build
```

## Building Platform-Specific Binaries

### macOS
```bash
npm run build:mac
```

### Windows
```bash
npm run build:win
```

### Linux
```bash
npm run build:linux
```
