from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import tempfile
import os
import sys
import shutil
import time
import uuid
import uvicorn
import json
from pathlib import Path

# Add parent directory to path to import the quantum chemistry modules
parent_dir = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(parent_dir)

from my_hf_program.visualize_trajectory_py3dmol import read_xyz_trajectory, visualize_trajectory_py3dmol
from my_hf_program.optimize_geometry import optimize_geometry

app = FastAPI(
    title="Quantum Chemistry API",
    description="API for quantum chemistry calculations and visualizations",
    version="1.0.0",
)

# Configuration
TEMP_DIR = os.path.join(tempfile.gettempdir(), "quantum-chemistry-api")
os.makedirs(TEMP_DIR, exist_ok=True)

# Store temporary files with their expiration
file_storage = {}

# Models
class OptimizationRequest(BaseModel):
    charge: int = 0
    basis: str = "sto-3g"
    max_steps: int = 100

class OptimizationResult(BaseModel):
    job_id: str
    status: str
    message: str
    result_url: Optional[str] = None
    visualization_url: Optional[str] = None


# Helpers
def cleanup_old_files():
    """Clean up expired temporary files"""
    now = time.time()
    for job_id, file_info in list(file_storage.items()):
        if now > file_info["expires_at"]:
            cleanup_job(job_id)

def cleanup_job(job_id: str):
    """Remove a job's files"""
    if job_id in file_storage:
        try:
            job_dir = file_storage[job_id]["directory"]
            if os.path.exists(job_dir):
                shutil.rmtree(job_dir)
            del file_storage[job_id]
        except Exception as e:
            print(f"Error cleaning up job {job_id}: {str(e)}")


# API routes
@app.get("/")
def read_root():
    return {"message": "Quantum Chemistry API is running"}


@app.post("/optimize", response_model=OptimizationResult)
async def start_optimization(
    background_tasks: BackgroundTasks,
    params: OptimizationRequest,
    molecule: UploadFile = File(...)
):
    """Start a geometry optimization job"""
    
    # Create a unique job ID and directory
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    # Save the uploaded molecule
    molecule_path = os.path.join(job_dir, "input.xyz")
    with open(molecule_path, "wb") as f:
        f.write(await molecule.read())
    
    # Store job info
    file_storage[job_id] = {
        "directory": job_dir,
        "expires_at": time.time() + 60 * 60 * 24,  # 24 hours
        "status": "pending"
    }
    
    # Start optimization in background
    background_tasks.add_task(
        run_optimization,
        job_id,
        molecule_path,
        params.charge,
        params.basis,
        params.max_steps
    )
    
    # Return initial response
    return OptimizationResult(
        job_id=job_id,
        status="pending",
        message="Optimization job started"
    )


@app.get("/jobs/{job_id}", response_model=OptimizationResult)
async def get_job_status(job_id: str):
    """Get the status of a job"""
    
    cleanup_old_files()
    
    if job_id not in file_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_info = file_storage[job_id]
    
    # Build response
    result = OptimizationResult(
        job_id=job_id,
        status=job_info["status"],
        message=job_info.get("message", "")
    )
    
    # Add URLs if job is complete
    if job_info["status"] == "complete":
        base_url = f"/files/{job_id}"
        result.result_url = f"{base_url}/geometry_trajectory.xyz"
        result.visualization_url = f"{base_url}/visualization.html"
    
    return result


@app.get("/files/{job_id}/{filename}")
async def get_job_file(job_id: str, filename: str):
    """Get a file from a job"""
    
    if job_id not in file_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_dir = file_storage[job_id]["directory"]
    file_path = os.path.join(job_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # For HTML visualization, return HTML response
    if filename.endswith(".html"):
        with open(file_path, "r") as f:
            content = f.read()
        return HTMLResponse(content)
    
    # For other files, return as download
    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@app.get("/visualize/{job_id}")
async def visualize_job(job_id: str):
    """Get visualization for a job"""
    
    if job_id not in file_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_info = file_storage[job_id]
    job_dir = job_info["directory"]
    
    if job_info["status"] != "complete":
        raise HTTPException(status_code=400, detail="Job not complete")
    
    # Path to trajectory file
    trajectory_path = os.path.join(job_dir, "geometry_trajectory.xyz")
    
    # Path for HTML visualization
    html_path = os.path.join(job_dir, "visualization.html")
    
    # Generate visualization if it doesn't exist
    if not os.path.exists(html_path):
        try:
            symbols, trajectory = read_xyz_trajectory(trajectory_path)
            visualize_trajectory_py3dmol(symbols, trajectory, html_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Visualization error: {str(e)}")
    
    # Return the HTML content
    with open(html_path, "r") as f:
        content = f.read()
    
    return HTMLResponse(content)


@app.post("/visualize/upload")
async def visualize_uploaded_trajectory(
    molecule: UploadFile = File(...)
):
    """Visualize an uploaded trajectory file"""
    
    # Create a unique job ID and directory
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    # Save the uploaded molecule
    trajectory_path = os.path.join(job_dir, "trajectory.xyz")
    with open(trajectory_path, "wb") as f:
        f.write(await molecule.read())
    
    # Path for HTML visualization
    html_path = os.path.join(job_dir, "visualization.html")
    
    # Generate visualization
    try:
        symbols, trajectory = read_xyz_trajectory(trajectory_path)
        visualize_trajectory_py3dmol(symbols, trajectory, html_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization error: {str(e)}")
    
    # Store job info
    file_storage[job_id] = {
        "directory": job_dir,
        "expires_at": time.time() + 60 * 60,  # 1 hour
        "status": "complete",
        "message": "Visualization generated"
    }
    
    # Return the URL to the visualization
    return {
        "job_id": job_id,
        "visualization_url": f"/files/{job_id}/visualization.html"
    }


@app.get("/molecules", response_model=List[Dict[str, Any]])
async def list_molecules():
    """Get a list of example molecules"""
    return [
        {
            "id": "h2",
            "name": "Hydrogen",
            "formula": "H₂",
            "xyz_url": "/examples/h2.xyz",
            "description": "Hydrogen molecule (H₂)"
        },
        {
            "id": "h2o",
            "name": "Water",
            "formula": "H₂O",
            "xyz_url": "/examples/h2o.xyz",
            "description": "Water molecule (H₂O)"
        },
        {
            "id": "ch4",
            "name": "Methane",
            "formula": "CH₄",
            "xyz_url": "/examples/ch4.xyz",
            "description": "Methane molecule (CH₄)"
        }
    ]


@app.on_event("startup")
async def startup_event():
    """Setup on startup"""
    # Create examples directory
    examples_dir = os.path.join(TEMP_DIR, "examples")
    os.makedirs(examples_dir, exist_ok=True)
    
    # Create example molecules if they don't exist
    create_example_molecules(examples_dir)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Clean up all temporary files
    for job_id in list(file_storage.keys()):
        cleanup_job(job_id)


# Background task for optimization
def run_optimization(job_id: str, molecule_path: str, charge: int, basis: str, max_steps: int):
    """Run geometry optimization as a background task"""
    
    job_dir = file_storage[job_id]["directory"]
    
    try:
        # Change working directory to job directory
        original_dir = os.getcwd()
        os.chdir(job_dir)
        
        # Run optimization
        optimize_geometry(molecule_path, charge, basis, max_steps=max_steps)
        
        # Check for output files
        trajectory_path = os.path.join(job_dir, "geometry_trajectory.xyz")
        optimized_path = os.path.join(job_dir, "optimized.xyz")
        
        if os.path.exists(trajectory_path) and os.path.exists(optimized_path):
            # Create visualization
            html_path = os.path.join(job_dir, "visualization.html")
            symbols, trajectory = read_xyz_trajectory(trajectory_path)
            visualize_trajectory_py3dmol(symbols, trajectory, html_path)
            
            # Update job status
            file_storage[job_id]["status"] = "complete"
            file_storage[job_id]["message"] = "Optimization completed successfully"
        else:
            file_storage[job_id]["status"] = "failed"
            file_storage[job_id]["message"] = "Optimization failed to produce output files"
    
    except Exception as e:
        file_storage[job_id]["status"] = "failed"
        file_storage[job_id]["message"] = f"Error during optimization: {str(e)}"
    
    finally:
        # Restore original working directory
        os.chdir(original_dir)


# Helper to create example molecules
def create_example_molecules(examples_dir: str):
    """Create example molecule XYZ files"""
    
    # H2 molecule
    h2_path = os.path.join(examples_dir, "h2.xyz")
    if not os.path.exists(h2_path):
        with open(h2_path, "w") as f:
            f.write("2\nHydrogen molecule\nH 0.0 0.0 0.0\nH 0.74 0.0 0.0\n")
    
    # H2O molecule
    h2o_path = os.path.join(examples_dir, "h2o.xyz")
    if not os.path.exists(h2o_path):
        with open(h2o_path, "w") as f:
            f.write("3\nWater molecule\nO 0.0 0.0 0.0\nH 0.757 0.586 0.0\nH -0.757 0.586 0.0\n")
    
    # CH4 molecule
    ch4_path = os.path.join(examples_dir, "ch4.xyz")
    if not os.path.exists(ch4_path):
        with open(ch4_path, "w") as f:
            f.write("5\nMethane molecule\nC 0.0 0.0 0.0\nH 0.629 0.629 0.629\nH -0.629 -0.629 0.629\nH -0.629 0.629 -0.629\nH 0.629 -0.629 -0.629\n")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
