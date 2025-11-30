#!/usr/bin/env python3
"""
Script to apply optimizations to the CT-cSTC notebook
This script will update the notebook with optimized PNG saving and GIF creation functions
"""

import json
import re
from pathlib import Path


def update_notebook_with_optimizations(notebook_path):
    """
    Update the notebook with optimized functions
    """
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Find and replace the make_gif function with the optimized version
    cells = notebook['cells']
    
    # Find the cell containing the original make_gif function
    for i, cell in enumerate(cells):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'def make_gif(frame_folder, duration, name="animation"):' in source:
                # Replace with optimized version
                optimized_make_gif = [
                    "def make_gif(frame_folder, duration, name=\"animation\"):\n",
                    "    '''\n",
                    "    Optimized GIF creation using imageio which is faster than PIL\n",
                    "    '''\n",
                    "    import os\n",
                    "    import glob\n",
                    "    try:\n",
                    "        import imageio.v2 as imageio\n",
                    "        use_imageio = True\n",
                    "    except ImportError:\n",
                    "        from PIL import Image\n",
                    "        use_imageio = False\n",
                    "    \n",
                    "    if not os.path.exists(frame_folder):\n",
                    "        os.makedirs(frame_folder)\n",
                    "    \n",
                    "    if use_imageio:\n",
                    "        # Optimized path using imageio\n",
                    "        import time\n",
                    "        png_files = sorted([f for f in os.listdir(frame_folder) if f.endswith('.png')])\n",
                    "        png_files = png_files[::2]  # Keep existing frame skipping\n",
                    "        \n",
                    "        if not png_files:\n",
                    "            print(f\"No PNG files found in {frame_folder}\")\n",
                    "            return\n",
                    "            \n",
                    "        images = []\n",
                    "        for filename in png_files:\n",
                    "            img_path = os.path.join(frame_folder, filename)\n",
                    "            images.append(imageio.imread(img_path))\n",
                    "        \n",
                    "        gif_path = os.path.join(frame_folder, name + \".gif\")\n",
                    "        start_time = time.time()\n",
                    "        imageio.mimsave(gif_path, images, duration=duration)\n",
                    "        end_time = time.time()\n",
                    "        print(f\"Created GIF with {len(images)} frames at {gif_path} in {end_time - start_time:.3f}s\")\n",
                    "    \n",
                    "    else:\n",
                    "        # Fallback to original PIL implementation\n",
                    "        from PIL import Image\n",
                    "        frames = [Image.open(image) for image in sorted(glob.glob(f\"{frame_folder}/*\"+\".png\"))][::2]\n",
                    "        print(len(frames))\n",
                    "        frame_one = frames[0]\n",
                    "        frame_one.save(frame_folder+\"/\" + name + \".gif\", format=\"GIF\", \n",
                    "                       append_images=frames, save_all=True, duration=duration, loop=0)\n"
                ]
                
                cells[i]['source'] = optimized_make_gif
                print(f"Updated make_gif function in cell {i}")
                break
    
    # Find the import section and add optimized imports
    for i, cell in enumerate(cells):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'import matplotlib.pyplot as plt' in source and 'import os' in source:
                # Add optimized matplotlib configuration
                import_section = cell['source']
                
                # Add backend optimization after matplotlib imports
                backend_config = [
                    "import matplotlib\n",
                    "matplotlib.use('Agg')  # Use non-interactive backend for better performance\n",
                    "matplotlib.rcParams['figure.max_open_warning'] = 0  # Disable figure max warning\n",
                    "matplotlib.rcParams['font.size'] = 10  # Smaller font for faster rendering during animation\n",
                    "matplotlib.rcParams['axes.linewidth'] = 0.5  # Thinner lines for faster rendering\n",
                    "matplotlib.rcParams['lines.linewidth'] = 1.0  # Thinner lines for faster rendering\n",
                    "\n"
                ]
                
                # Find where to insert the configuration
                insert_idx = -1
                for j, line in enumerate(import_section):
                    if 'import matplotlib.pyplot as plt' in line:
                        insert_idx = j + 1
                        break
                
                if insert_idx != -1:
                    for offset, config_line in enumerate(backend_config):
                        import_section.insert(insert_idx + offset, config_line)
                    
                    print(f"Added optimized matplotlib configuration in cell {i}")
                break
    
    # Save the updated notebook
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1)
    
    print(f"Updated notebook saved to {notebook_path}")


def create_optimized_savefig_wrapper():
    """
    Create an optimized wrapper function for savefig that can be used in the notebook
    """
    optimized_savefig_code = '''
def save_frame_optimized(fig, filename, dpi=None):
    """
    Optimized function to save matplotlib figure as PNG with better performance
    """
    import time
    if dpi is None:
        # Use lower DPI for animation frames, higher for final images
        dpi = int(fig_png_dpi/2) if 'rl_pos_' in filename else fig_png_dpi
    
    start_time = time.time()
    fig.savefig(
        filename,
        bbox_inches='tight',
        dpi=dpi,
        facecolor='white',
        edgecolor='none',
        format='png',
        pil_kwargs={'optimize': True},  # Optimize PNG compression
        backend='Agg'  # Use the anti-grain geometry backend for better performance
    )
    end_time = time.time()
    print(f"Saved {filename} in {end_time - start_time:.3f} seconds")
'''
    return optimized_savefig_code


def suggest_rl_plot_modifications():
    """
    Provide suggestions for modifying the rl_plot function to use optimized saving
    """
    suggestions = """
# Suggested modifications to rl_plot function:

# Replace this line:
# fig.savefig('sim/rl_pos_' + str(rl_anim_k).zfill(3) + '.' + 'png', bbox_inches='tight', dpi=int(fig_png_dpi/2))

# With this:
# save_frame_optimized(fig, 'sim/rl_pos_' + str(rl_anim_k).zfill(3) + '.' + 'png', dpi=int(fig_png_dpi/2))

# Also consider adding plt.close(fig) immediately after saving to free memory
"""
    return suggestions


if __name__ == "__main__":
    notebook_path = Path("/workspace/CT-cSTC.ipynb")
    
    if notebook_path.exists():
        print("Applying optimizations to the notebook...")
        update_notebook_with_optimizations(notebook_path)
        
        print("\nOptimization Summary:")
        print("1. Updated make_gif function to use imageio for faster GIF creation")
        print("2. Added optimized matplotlib backend configuration")
        print("3. Created optimized savefig wrapper (see create_optimized_savefig_wrapper function)")
        print("4. Suggested rl_plot modifications (see suggest_rl_plot_modifications function)")
        
        print("\nAdditional recommendations:")
        print("- Consider using PyVista or Plotly for GPU-accelerated 3D rendering")
        print("- Use lower DPI values during animation generation")
        print("- Close figures immediately after saving to free memory")
        print("- Consider MP4 instead of GIF for better performance and quality")
    else:
        print(f"Notebook not found at {notebook_path}")