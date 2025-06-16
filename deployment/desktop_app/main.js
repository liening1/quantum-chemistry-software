const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const { PythonShell } = require('python-shell');
const log = require('electron-log');

// Configure logging
log.transports.file.level = 'info';
log.info('Application starting...');

// Keep a global reference of the window object to prevent garbage collection
let mainWindow;

// Python path setup
const isProd = app.isPackaged;
let pythonPath;

if (isProd) {
  // In production, use the bundled Python executable
  pythonPath = path.join(process.resourcesPath, 'python', 'bin', 'python');
} else {
  // In development, use the system Python
  pythonPath = 'python';
}

// Path to the quantum chemistry scripts
const scriptPath = isProd
  ? path.join(process.resourcesPath, 'python', 'my_hf_program')
  : path.join(__dirname, '..', '..', 'my_hf_program');

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load the index.html file
  mainWindow.loadFile('index.html');

  // Open DevTools in development mode
  if (!isProd) {
    mainWindow.webContents.openDevTools();
  }

  // Create menu
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Open XYZ File',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const { canceled, filePaths } = await dialog.showOpenDialog({
              properties: ['openFile'],
              filters: [{ name: 'XYZ Files', extensions: ['xyz'] }]
            });
            if (!canceled) {
              mainWindow.webContents.send('file-opened', filePaths[0]);
            }
          }
        },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: async () => {
            const { shell } = require('electron');
            await shell.openExternal('https://github.com/yourusername/quantum-chemistry-software');
          }
        },
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              title: 'About Quantum Chemistry',
              message: 'Quantum Chemistry Software v1.0.0',
              detail: 'A modular, extensible quantum chemistry framework with visualization capabilities.'
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  // Window closed event handler
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App ready event handler
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    // On macOS, re-create the window when dock icon is clicked and no windows are open
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// App quit event handler
app.on('window-all-closed', () => {
  // Quit the app when all windows are closed (except on macOS)
  if (process.platform !== 'darwin') app.quit();
});

// IPC handlers for Python calculations
ipcMain.handle('run-geometry-optimization', async (event, args) => {
  const { xyzPath, charge, basis, maxSteps } = args;
  
  try {
    log.info(`Running geometry optimization for ${xyzPath}`);
    
    // Create a temporary directory for outputs
    const tempDir = app.getPath('temp');
    const outputDir = path.join(tempDir, 'quantum-chem-' + Date.now());
    fs.mkdirSync(outputDir, { recursive: true });
    
    // Copy the input XYZ file to output directory
    const inputXyz = path.join(outputDir, path.basename(xyzPath));
    fs.copyFileSync(xyzPath, inputXyz);
    
    // Run the Python script
    const options = {
      mode: 'text',
      pythonPath: pythonPath,
      scriptPath: scriptPath,
      args: [inputXyz, charge.toString(), basis, maxSteps.toString()]
    };
    
    return new Promise((resolve, reject) => {
      PythonShell.run('optimize_geometry.py', options, (err, results) => {
        if (err) {
          log.error('Error running optimization:', err);
          reject(err);
          return;
        }
        
        // Get output files
        const trajectoryPath = path.join(outputDir, 'geometry_trajectory.xyz');
        const optimizedPath = path.join(outputDir, 'optimized.xyz');
        const htmlPath = path.join(outputDir, 'geometry_optimization.html');
        
        if (fs.existsSync(trajectoryPath) && fs.existsSync(optimizedPath)) {
          resolve({
            success: true,
            outputDir,
            trajectoryPath,
            optimizedPath,
            htmlPath: fs.existsSync(htmlPath) ? htmlPath : null,
            log: results.join('\n')
          });
        } else {
          reject(new Error('Output files not found'));
        }
      });
    });
  } catch (error) {
    log.error('Error in geometry optimization:', error);
    throw error;
  }
});

ipcMain.handle('visualize-trajectory', async (event, args) => {
  const { xyzPath } = args;
  
  try {
    log.info(`Visualizing trajectory ${xyzPath}`);
    
    // Create a temporary directory for output
    const tempDir = app.getPath('temp');
    const outputDir = path.join(tempDir, 'quantum-chem-vis-' + Date.now());
    fs.mkdirSync(outputDir, { recursive: true });
    
    // Output HTML path
    const htmlPath = path.join(outputDir, 'trajectory_visualization.html');
    
    // Run the Python script
    const options = {
      mode: 'text',
      pythonPath: pythonPath,
      scriptPath: scriptPath,
      args: [xyzPath, htmlPath]
    };
    
    return new Promise((resolve, reject) => {
      PythonShell.run('visualize_trajectory_py3dmol.py', options, (err, results) => {
        if (err) {
          log.error('Error visualizing trajectory:', err);
          reject(err);
          return;
        }
        
        if (fs.existsSync(htmlPath)) {
          resolve({
            success: true,
            htmlPath,
            log: results.join('\n')
          });
        } else {
          reject(new Error('Output HTML file not found'));
        }
      });
    });
  } catch (error) {
    log.error('Error in trajectory visualization:', error);
    throw error;
  }
});
