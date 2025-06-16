// visualization.js
const app = getApp();
const API_BASE_URL = 'https://api.quantum-chemistry.example.com';

Page({
  data: {
    molecules: [],
    currentMoleculeId: null,
    currentMolecule: null,
    htmlUrl: '',
    isTrajectory: false,
    currentFrame: 0,
    totalFrames: 0,
    isPlaying: false
  },

  onLoad: function(options) {
    // Load molecules from API or local storage
    this.loadMolecules();
    
    // If molecule ID was passed via navigation
    if (options.id) {
      this.setData({
        currentMoleculeId: options.id
      });
      this.selectMolecule(options.id);
    }
  },

  onUnload: function() {
    // Stop any ongoing animations
    this.stopAnimation();
  },

  loadMolecules: function() {
    // Fetch molecules from API
    wx.request({
      url: `${API_BASE_URL}/molecules`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            molecules: res.data
          });
        } else {
          wx.showToast({
            title: 'Failed to load molecules',
            icon: 'none'
          });
        }
      },
      fail: () => {
        // Fallback to some sample molecules if API is unavailable
        this.setData({
          molecules: [
            {
              id: 'h2',
              name: 'Hydrogen',
              formula: 'H₂',
              thumbnail: '/images/molecules/h2.png',
              isTrajectory: false
            },
            {
              id: 'h2o',
              name: 'Water',
              formula: 'H₂O',
              thumbnail: '/images/molecules/h2o.png',
              isTrajectory: false
            },
            {
              id: 'opt_trajectory',
              name: 'H₂ Optimization',
              formula: 'H₂ (trajectory)',
              thumbnail: '/images/molecules/trajectory.png',
              isTrajectory: true,
              frames: 10
            }
          ]
        });
      }
    });
  },

  onSelectMolecule: function(e) {
    const id = e.currentTarget.dataset.id;
    this.selectMolecule(id);
  },

  selectMolecule: function(id) {
    const molecule = this.data.molecules.find(m => m.id === id);
    
    if (!molecule) {
      wx.showToast({
        title: 'Molecule not found',
        icon: 'none'
      });
      return;
    }
    
    this.stopAnimation();
    
    this.setData({
      currentMoleculeId: id,
      currentMolecule: molecule,
      isTrajectory: molecule.isTrajectory,
      currentFrame: 0,
      totalFrames: molecule.isTrajectory ? molecule.frames || 1 : 1
    });
    
    // Request HTML visualization from the server
    wx.showLoading({
      title: 'Loading visualization',
    });
    
    wx.request({
      url: `${API_BASE_URL}/visualize/${id}`,
      method: 'GET',
      success: (res) => {
        wx.hideLoading();
        if (res.statusCode === 200) {
          this.setData({
            htmlUrl: res.data.url
          });
        } else {
          wx.showToast({
            title: 'Failed to load visualization',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.hideLoading();
        wx.showToast({
          title: 'Network error',
          icon: 'none'
        });
      }
    });
  },

  onSliderChange: function(e) {
    const frameIndex = e.detail.value;
    this.setData({
      currentFrame: frameIndex
    });
    this.sendFrameMessage(frameIndex);
  },

  onPrevFrame: function() {
    if (!this.data.isTrajectory) return;
    
    const prev = (this.data.currentFrame - 1 + this.data.totalFrames) % this.data.totalFrames;
    this.setData({
      currentFrame: prev
    });
    this.sendFrameMessage(prev);
  },

  onNextFrame: function() {
    if (!this.data.isTrajectory) return;
    
    const next = (this.data.currentFrame + 1) % this.data.totalFrames;
    this.setData({
      currentFrame: next
    });
    this.sendFrameMessage(next);
  },

  onTogglePlay: function() {
    if (!this.data.isTrajectory) return;
    
    if (this.data.isPlaying) {
      this.stopAnimation();
    } else {
      this.startAnimation();
    }
  },

  startAnimation: function() {
    this.setData({
      isPlaying: true
    });
    
    this.animationTimer = setInterval(() => {
      const next = (this.data.currentFrame + 1) % this.data.totalFrames;
      this.setData({
        currentFrame: next
      });
      this.sendFrameMessage(next);
    }, 500);
  },

  stopAnimation: function() {
    if (this.animationTimer) {
      clearInterval(this.animationTimer);
      this.animationTimer = null;
    }
    
    this.setData({
      isPlaying: false
    });
  },

  sendFrameMessage: function(frameIndex) {
    // Send message to web-view to update frame
    // This requires custom JavaScript in the web-view to receive messages
    if (this.data.htmlUrl) {
      // WeChat Mini Program web-view communication is limited
      // This would require server-side implementation to handle frame changes
      // or using URL parameters to specify frame index
      const webViewContext = wx.createWebViewContext('webview');
      webViewContext.postMessage({
        data: {
          action: 'setFrame',
          frameIndex: frameIndex
        }
      });
    }
  }
});
