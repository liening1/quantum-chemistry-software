import streamlit as st
import os
import sys
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
import base64
import time
import shutil

# Add parent directory to path to import the quantum chemistry modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from my_hf_program.molecule import load_molecule
from my_hf_program.visualize_trajectory_py3dmol import read_xyz_trajectory, visualize_trajectory_py3dmol
from my_hf_program.optimize_geometry import optimize_geometry

# Page configuration
st.set_page_config(
    page_title="Quantum Chemistry Web App",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Title and introduction
st.title("⚛️ Quantum Chemistry Software")
st.markdown("""
This web application provides a user-friendly interface to perform quantum chemistry calculations
and visualize molecular structures and optimization trajectories.
""")

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Choose a function:",
    ["Home", "Geometry Optimization", "Trajectory Visualization"]
)

# Function to create a download link for files
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

# Home page
if page == "Home":
    st.header("Welcome to the Quantum Chemistry Web App!")
    
    st.markdown("""
    **Available Functions:**
    
    1. **Geometry Optimization**: Optimize molecular geometries using Hartree-Fock with PySCF and BFGS
    2. **Trajectory Visualization**: Visualize molecular trajectories interactively in 3D
    
    **How to Use:**
    - Navigate using the sidebar on the left
    - Upload XYZ files for molecules
    - Run calculations and visualizations directly in your browser
    
    **Requirements:**
    - XYZ files should follow standard format (number of atoms, comment, then atom coordinates)
    - For best results with visualization, use modern browsers
    """)
    
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/9f/Benzene3D.png", 
             caption="Example molecular structure visualization", width=300)

# Geometry Optimization page
elif page == "Geometry Optimization":
    st.header("Geometry Optimization")
    st.markdown("Optimize molecular geometry using Hartree-Fock calculations with PySCF")
    
    # File upload
    uploaded_file = st.file_uploader("Upload an XYZ file", type="xyz")
    
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xyz') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_xyz_path = tmp_file.name
        
        st.success(f"Successfully uploaded {uploaded_file.name}")
        
        # Display the uploaded molecule
        with open(temp_xyz_path, 'r') as f:
            xyz_content = f.read()
        st.text_area("XYZ File Content:", xyz_content, height=200)
        
        # Parameters for geometry optimization
        st.subheader("Optimization Parameters")
        col1, col2, col3 = st.columns(3)
        with col1:
            charge = st.number_input("Charge", value=0)
        with col2:
            basis = st.selectbox("Basis Set", ["sto-3g", "3-21g", "6-31g", "cc-pvdz"])
        with col3:
            max_steps = st.slider("Max Optimization Steps", 10, 200, 100)
        
        # Run optimization
        if st.button("Run Geometry Optimization"):
            try:
                st.info("Running geometry optimization... This may take a while.")
                progress_bar = st.progress(0)
                
                # Temporarily change directory for file output
                current_dir = os.getcwd()
                temp_dir = tempfile.mkdtemp()
                os.chdir(temp_dir)
                
                # Run the optimization
                optimize_geometry(temp_xyz_path, charge, basis, max_steps=max_steps)
                
                # Check for result files
                trajectory_file = os.path.join(temp_dir, 'geometry_trajectory.xyz')
                optimized_file = os.path.join(temp_dir, 'optimized.xyz')
                
                # Move back to original directory
                os.chdir(current_dir)
                
                if os.path.exists(trajectory_file) and os.path.exists(optimized_file):
                    st.success("Optimization completed successfully!")
                    
                    # Create download links
                    st.markdown("### Download Results")
                    st.markdown(get_binary_file_downloader_html(trajectory_file, 'Trajectory XYZ'), unsafe_allow_html=True)
                    st.markdown(get_binary_file_downloader_html(optimized_file, 'Optimized XYZ'), unsafe_allow_html=True)
                    
                    # Visualize the trajectory
                    st.subheader("Visualization")
                    if st.button("Visualize Trajectory"):
                        symbols, trajectory = read_xyz_trajectory(trajectory_file)
                        html_file = os.path.join(temp_dir, 'trajectory_vis.html')
                        visualize_trajectory_py3dmol(symbols, trajectory, html_file)
                        
                        # Display the HTML content in an iframe
                        with open(html_file, 'r') as f:
                            html_content = f.read()
                        st.components.v1.html(html_content, height=600)
                else:
                    st.error("Optimization failed. Please check your input file and parameters.")
            
            except Exception as e:
                st.error(f"An error occurred during optimization: {str(e)}")
            
            # Clean up temporary files
            try:
                os.remove(temp_xyz_path)
                shutil.rmtree(temp_dir)
            except:
                pass

# Trajectory Visualization page
elif page == "Trajectory Visualization":
    st.header("Trajectory Visualization")
    st.markdown("Visualize molecular trajectories using interactive 3D viewer")
    
    # File upload
    uploaded_file = st.file_uploader("Upload a trajectory XYZ file", type="xyz")
    
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xyz') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_xyz_path = tmp_file.name
        
        st.success(f"Successfully uploaded {uploaded_file.name}")
        
        try:
            # Read trajectory
            symbols, trajectory = read_xyz_trajectory(temp_xyz_path)
            st.write(f"Loaded trajectory with {len(trajectory)} frames and {len(symbols)} atoms")
            
            # Create visualization
            temp_dir = tempfile.mkdtemp()
            html_file = os.path.join(temp_dir, 'trajectory_vis.html')
            visualize_trajectory_py3dmol(symbols, trajectory, html_file)
            
            # Display the HTML content in an iframe
            with open(html_file, 'r') as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=600)
            
            # Clean up temporary files
            try:
                os.remove(temp_xyz_path)
                shutil.rmtree(temp_dir)
            except:
                pass
        
        except Exception as e:
            st.error(f"An error occurred during visualization: {str(e)}")
            st.error("Please make sure the uploaded file is a valid multi-frame XYZ trajectory file.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "This app was created as part of a quantum chemistry software project. "
    "For more information, check out the [GitHub repository](https://github.com/yourusername/quantum-chemistry-software)."
)
