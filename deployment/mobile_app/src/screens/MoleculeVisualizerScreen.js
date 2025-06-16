import React, { useState, useRef } from 'react';
import { StyleSheet, View, Text, TouchableOpacity, ActivityIndicator, Slider } from 'react-native';
import { WebView } from 'react-native-webview';
import { useRoute } from '@react-navigation/native';

/**
 * Screen component for visualizing molecular structures and trajectories
 */
const MoleculeVisualizerScreen = () => {
  const route = useRoute();
  const { xyzData, title = 'Molecule Visualization' } = route.params || {};
  const [isLoading, setIsLoading] = useState(true);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [totalFrames, setTotalFrames] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  const webViewRef = useRef(null);

  // Create HTML content with 3Dmol.js for visualization
  const html = `
<!DOCTYPE html>
<html>
<head>
    <title>Molecule Visualization</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <style>
        body { margin: 0; padding: 0; background-color: #ffffff; overflow: hidden; }
        #container { position: absolute; width: 100%; height: 100%; }
        #viewer { width: 100%; height: 100%; }
    </style>
    <script src="https://3dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
</head>
<body>
    <div id="container">
        <div id="viewer"></div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize 3Dmol viewer
            let viewer = $3Dmol.createViewer('viewer', {
                backgroundColor: 'white',
            });

            // Parse and store frames (for trajectory)
            const xyzData = ${JSON.stringify(xyzData)};
            const frames = xyzData.split('\\n\\n').filter(frame => frame.trim().length > 0);
            
            // Function to show a specific frame
            function showFrame(frameIndex) {
                if (!frames || frameIndex < 0 || frameIndex >= frames.length) return;
                
                // Clear viewer
                viewer.clear();
                
                // Add the model
                let model = viewer.addModel(frames[frameIndex], "xyz");
                model.addBonds();
                
                // Set style
                viewer.setStyle({}, {
                    stick: { radius: 0.2, colorscheme: "Jmol" },
                    sphere: { scale: 0.3, colorscheme: "Jmol" }
                });
                
                // Update view
                viewer.zoomTo();
                viewer.center();
                viewer.render();
                
                // Send frame info back to React Native
                window.ReactNativeWebView.postMessage(JSON.stringify({
                    type: 'frameChange',
                    currentFrame: frameIndex,
                    totalFrames: frames.length
                }));
            }
            
            // Expose functions to React Native
            window.updateFrame = function(frameIndex) {
                showFrame(frameIndex);
            };
            
            // Initialize with first frame
            showFrame(0);
            
            // Notify React Native that visualization is ready
            window.ReactNativeWebView.postMessage(JSON.stringify({
                type: 'loaded',
                totalFrames: frames.length
            }));
        });
    </script>
</body>
</html>
  `;

  // Handle messages from WebView
  const onMessage = (event) => {
    try {
      const data = JSON.parse(event.nativeEvent.data);
      if (data.type === 'loaded') {
        setIsLoading(false);
        setTotalFrames(data.totalFrames);
      } else if (data.type === 'frameChange') {
        setCurrentFrame(data.currentFrame);
        setTotalFrames(data.totalFrames);
      }
    } catch (error) {
      console.error('Error parsing WebView message:', error);
    }
  };

  // Update frame in WebView
  const updateFrame = (frameIndex) => {
    if (webViewRef.current) {
      webViewRef.current.injectJavaScript(`
        if (window.updateFrame) {
          window.updateFrame(${frameIndex});
        }
        true;
      `);
    }
  };

  // Play/pause animation
  const togglePlay = () => {
    if (isPlaying) {
      clearInterval(playIntervalRef.current);
      playIntervalRef.current = null;
    } else {
      playIntervalRef.current = setInterval(() => {
        setCurrentFrame(prev => {
          const next = (prev + 1) % totalFrames;
          updateFrame(next);
          return next;
        });
      }, 500);
    }
    setIsPlaying(!isPlaying);
  };

  // Animation control with timer
  const playIntervalRef = useRef(null);

  // Cleanup interval on component unmount
  React.useEffect(() => {
    return () => {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
      }
    };
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      
      <View style={styles.visualizerContainer}>
        {isLoading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color="#4CAF50" />
            <Text style={styles.loadingText}>Loading visualization...</Text>
          </View>
        )}
        
        <WebView
          ref={webViewRef}
          source={{ html }}
          style={styles.webview}
          javaScriptEnabled={true}
          onMessage={onMessage}
          originWhitelist={['*']}
        />
      </View>
      
      {!isLoading && totalFrames > 1 && (
        <View style={styles.controls}>
          <Text style={styles.frameText}>
            Frame {currentFrame + 1} of {totalFrames}
          </Text>
          
          <Slider
            style={styles.slider}
            minimumValue={0}
            maximumValue={totalFrames - 1}
            step={1}
            value={currentFrame}
            onValueChange={(value) => {
              setCurrentFrame(value);
              updateFrame(value);
            }}
            minimumTrackTintColor="#4CAF50"
            maximumTrackTintColor="#d3d3d3"
            thumbTintColor="#4CAF50"
          />
          
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={styles.button}
              onPress={() => {
                const prev = (currentFrame - 1 + totalFrames) % totalFrames;
                setCurrentFrame(prev);
                updateFrame(prev);
              }}
            >
              <Text style={styles.buttonText}>Previous</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.button}
              onPress={togglePlay}
            >
              <Text style={styles.buttonText}>{isPlaying ? 'Pause' : 'Play'}</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.button}
              onPress={() => {
                const next = (currentFrame + 1) % totalFrames;
                setCurrentFrame(next);
                updateFrame(next);
              }}
            >
              <Text style={styles.buttonText}>Next</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    padding: 16,
    backgroundColor: '#4CAF50',
    color: 'white',
  },
  visualizerContainer: {
    flex: 1,
    position: 'relative',
  },
  webview: {
    flex: 1,
    backgroundColor: 'white',
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#333',
  },
  controls: {
    backgroundColor: 'white',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#ddd',
  },
  frameText: {
    textAlign: 'center',
    fontSize: 16,
    marginBottom: 8,
  },
  slider: {
    width: '100%',
    height: 40,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  button: {
    backgroundColor: '#4CAF50',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 4,
  },
  buttonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
});

export default MoleculeVisualizerScreen;
