import sys
import py3Dmol
import time

# Read XYZ trajectory
def read_xyz_trajectory(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    trajectory = []
    i = 0
    while i < len(lines):
        n_atoms = int(lines[i])
        frame = ''.join(lines[i:i+n_atoms+2])
        trajectory.append(frame)
        i += n_atoms + 2
    return trajectory

def save_html_animation(trajectory, out_html='geometry_optimization.html', delay=300):
    # Create HTML with py3Dmol animation
    html = """
    <html><head><script src='https://3dmol.org/build/3Dmol-min.js'></script></head><body>
    <div id='viewer' style='width:500px; height:500px;'></div>
    <script>
    let xyzs = [
    """
    html += ',\n'.join([repr(frame.replace('\n', '\\n')) for frame in trajectory])
    html += "]\n"  # end xyzs array
    html += f"""
    let viewer = $3Dmol.createViewer('viewer', {{backgroundColor: 'white'}});
    let i = 0;
    function showFrame(idx) {{
        viewer.clear();
        viewer.addModel(xyzs[idx], 'xyz');
        viewer.setStyle({{}}, {{stick:{{radius:0.15}}, sphere:{{scale:0.3}}}});
        viewer.zoomTo();
        viewer.render();
    }}
    showFrame(0);
    setInterval(function() {{
        i = (i + 1) % xyzs.length;
        showFrame(i);
    }}, {delay});
    </script></body></html>
    """
    with open(out_html, 'w') as f:
        f.write(html)
    print(f'py3Dmol HTML animation saved as {out_html}')

if __name__ == "__main__":
    xyz_traj = sys.argv[1] if len(sys.argv) > 1 else 'geometry_trajectory.xyz'
    out_html = sys.argv[2] if len(sys.argv) > 2 else 'geometry_optimization.html'
    trajectory = read_xyz_trajectory(xyz_traj)
    save_html_animation(trajectory, out_html)
