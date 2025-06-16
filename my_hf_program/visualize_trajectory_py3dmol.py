"""
Visualize molecular trajectories interactively in 3D using py3Dmol/3Dmol.js

This module provides functions to visualize XYZ trajectory files (multi-frame XYZ files)
using py3Dmol and 3Dmol.js for interactive 3D visualization in web browsers.

The visualization includes:
- Interactive 3D viewer with proper molecule rendering and bond detection
- Animation controls (play, pause, previous, next)
- Frame slider for easy navigation
- Animation speed control
- Keyboard shortcuts (arrow keys, spacebar)
- Automatic view centering and zoom

Usage as script:
    python visualize_trajectory_py3dmol.py [xyz_trajectory_file] [output_html_file]

Usage as module:
    from visualize_trajectory_py3dmol import visualize_trajectory_py3dmol
    
    # Read trajectory file
    symbols, trajectory = read_xyz_trajectory('geometry_trajectory.xyz')
    
    # Create visualization
    html_file = visualize_trajectory_py3dmol(symbols, trajectory, 'my_visualization.html')
"""
import sys
import numpy as np

def read_xyz_trajectory(filename):
    """
    Read a multi-frame XYZ trajectory file
    
    Parameters:
    -----------
    filename : str
        Path to the XYZ trajectory file
    
    Returns:
    --------
    symbols : list of str
        Atom symbols
    trajectory : list of numpy arrays
        List of coordinate arrays for each step
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
    trajectory = []
    symbols = []
    i = 0
    while i < len(lines):
        n_atoms = int(lines[i])
        if not symbols:
            for j in range(n_atoms):
                parts = lines[i+2+j].split()
                symbols.append(parts[0])
        coords = []
        for j in range(n_atoms):
            parts = lines[i+2+j].split()
            coords.append([float(parts[1]), float(parts[2]), float(parts[3])])
        trajectory.append(np.array(coords))
        i += n_atoms + 2
    return symbols, trajectory

def visualize_trajectory_py3dmol(symbols, trajectory, output_html='trajectory_visualization.html'):
    """
    Create an HTML file with an interactive 3D visualization of the molecular trajectory using py3Dmol.
    
    Parameters:
    -----------
    symbols : list of str
        Atom symbols
    trajectory : list of numpy.ndarray
        List of coordinate arrays for each step of the trajectory
    output_html : str
        Output HTML file name
    """
    # Convert trajectory to XYZ format strings
    xyz_frames = []
    for i, coords in enumerate(trajectory):
        frame = f"{len(symbols)}\nStep {i+1}\n"
        for sym, xyz in zip(symbols, coords):
            frame += f"{sym} {xyz[0]:.6f} {xyz[1]:.6f} {xyz[2]:.6f}\n"
        xyz_frames.append(frame)
    
    # Create HTML with JavaScript for 3D visualization using 3Dmol.js
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Molecular Trajectory Visualization</title>
    <script src="https://3dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            text-align: center;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        #viewer {
            width: 600px;
            height: 400px;
            margin: 20px auto;
            position: relative;
            border: 1px solid #ccc;
        }
        .controls {
            margin: 20px 0;
        }
        button {
            padding: 8px 15px;
            margin: 0 5px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background-color: #45a049;
        }
        .slider-container {
            width: 80%;
            margin: 20px auto;
        }
        #frameSlider {
            width: 100%;
        }
        #speedControl {
            width: 50%;
        }
        #frameCounter {
            margin-top: 10px;
            font-size: 16px;
            font-weight: bold;
        }
        .notes {
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Molecular Trajectory Visualization</h1>
        <div id="viewer"></div>
        <div id="frameCounter">Frame 1 / FRAME_COUNT</div>
        
        <div class="slider-container">
            <input type="range" min="0" max="FRAME_MAX" value="0" class="slider" id="frameSlider">
        </div>
        
        <div class="controls">
            <button id="prevBtn">Previous</button>
            <button id="playBtn">Play</button>
            <button id="nextBtn">Next</button>
            <button id="resetBtn">Reset View</button>
        </div>
        
        <div class="slider-container">
            <label for="speedControl">Animation Speed:</label>
            <input type="range" min="100" max="2000" value="500" class="slider" id="speedControl">
            <span id="speedValue">500 ms</span>
        </div>
        
        <div class="notes">
            <p>Use left/right arrow keys to navigate frames, spacebar to play/pause</p>
        </div>
    </div>

    <script>
        // Initialize the viewer after page has loaded
        $(document).ready(function() {
            let viewer = null;
            let currentFrame = 0;
            let isPlaying = false;
            let playInterval;
            let frameDelay = 500;
            
            // Store all XYZ frames
            const frames = [
FRAME_DATA
            ];
            
            // Initialize the 3Dmol viewer
            viewer = $3Dmol.createViewer($("#viewer"), {
                backgroundColor: "white"
            });
            
            // Function to show a specific frame
            function showFrame(frameIndex) {
                if (frameIndex < 0 || frameIndex >= frames.length) return;
                
                currentFrame = frameIndex;
                
                // Update UI
                $("#frameCounter").text(`Frame ${frameIndex + 1} / ${frames.length}`);
                $("#frameSlider").val(frameIndex);
                
                // Update viewer
                viewer.clear();
                let model = viewer.addModel(frames[frameIndex], "xyz");
                model.addBonds();
                
                // Set style for atoms and bonds
                viewer.setStyle({}, {
                    stick: {
                        radius: 0.2, 
                        colorscheme: "Jmol"
                    },
                    sphere: {
                        scale: 0.3,
                        colorscheme: "Jmol"
                    }
                });
                
                viewer.center();
                viewer.zoomTo();
                viewer.render();
            }
            
            // Play/pause the animation
            function togglePlay() {
                if (isPlaying) {
                    clearInterval(playInterval);
                    $("#playBtn").text("Play");
                    isPlaying = false;
                } else {
                    playInterval = setInterval(function() {
                        showFrame((currentFrame + 1) % frames.length);
                    }, frameDelay);
                    $("#playBtn").text("Pause");
                    isPlaying = true;
                }
            }
            
            // UI event handlers
            $("#prevBtn").click(function() {
                showFrame((currentFrame - 1 + frames.length) % frames.length);
            });
            
            $("#nextBtn").click(function() {
                showFrame((currentFrame + 1) % frames.length);
            });
            
            $("#playBtn").click(togglePlay);
            
            $("#resetBtn").click(function() {
                viewer.center();
                viewer.zoomTo();
                viewer.render();
            });
            
            $("#frameSlider").on("input", function() {
                showFrame(parseInt($(this).val()));
            });
            
            $("#speedControl").on("input", function() {
                frameDelay = parseInt($(this).val());
                $("#speedValue").text(`${frameDelay} ms`);
                
                // Reset the animation with the new speed if it's playing
                if (isPlaying) {
                    clearInterval(playInterval);
                    playInterval = setInterval(function() {
                        showFrame((currentFrame + 1) % frames.length);
                    }, frameDelay);
                }
            });
            
            // Keyboard controls
            $(document).keydown(function(e) {
                switch(e.which) {
                    case 37: // left arrow
                        $("#prevBtn").click();
                        break;
                    case 39: // right arrow
                        $("#nextBtn").click();
                        break;
                    case 32: // spacebar
                        e.preventDefault();
                        togglePlay();
                        break;
                }
            });
            
            // Initialize first frame
            showFrame(0);
        });
    </script>
</body>
</html>
"""
    # Replace placeholders in the template
    frames_str = ""
    for i, frame in enumerate(xyz_frames):
        frame_escaped = frame.replace("\n", "\\n").replace('"', '\\"')
        frames_str += f'                "{frame_escaped}"'
        if i < len(xyz_frames) - 1:
            frames_str += ',\n'
        else:
            frames_str += '\n'
    
    html = html.replace("FRAME_COUNT", str(len(xyz_frames)))
    html = html.replace("FRAME_MAX", str(len(xyz_frames) - 1))
    html = html.replace("FRAME_DATA", frames_str)
    
    # Write the HTML file
    with open(output_html, 'w') as f:
        f.write(html)
    
    print(f"3D visualization saved as '{output_html}'")
    return output_html

def main():
    # Parse command line arguments
    if len(sys.argv) > 1:
        xyz_file = sys.argv[1]
    else:
        xyz_file = 'geometry_trajectory.xyz'
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = 'trajectory_visualization.html'
    
    # Read the trajectory
    symbols, trajectory = read_xyz_trajectory(xyz_file)
    
    # Create the visualization
    html_file = visualize_trajectory_py3dmol(symbols, trajectory, output_file)
    
    print(f"Visualized {len(trajectory)} frames from {xyz_file}")
    print(f"Open {html_file} in a web browser to view the interactive 3D animation")
    print("Tip: You can use keyboard shortcuts - left/right arrow keys to navigate frames, spacebar to play/pause")

if __name__ == "__main__":
    main()
