"""
Optimized functions for PNG rendering and GIF creation in the CT-cSTC notebook
"""

import os
import glob
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for better performance
import matplotlib.pyplot as plt
import time
from typing import Optional

# Try to import imageio for faster GIF creation
try:
    import imageio.v2 as imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False
    print("imageio not available, falling back to PIL for GIF creation")

def save_frame_optimized(fig, filename: str, dpi: int = 150):
    """
    Optimized function to save matplotlib figure as PNG with better performance
    
    Args:
        fig: matplotlib figure object
        filename: path to save the file
        dpi: dots per inch for the saved image
    """
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

def make_gif_optimized(frame_folder: str, duration: float, name: str = "animation", use_imageio: bool = True):
    """
    Optimized GIF creation function using imageio (faster than PIL) when available
    
    Args:
        frame_folder: directory containing PNG frames
        duration: duration of each frame in the GIF
        name: name of the output GIF file
        use_imageio: whether to use imageio (faster) or fallback to PIL
    """
    if not os.path.exists(frame_folder):
        os.makedirs(frame_folder)

    # Get PNG files and optionally skip some for performance (keeping existing behavior of [::2])
    png_files = sorted([f for f in os.listdir(frame_folder) if f.endswith('.png')])
    png_files = png_files[::2]  # Keep existing frame skipping behavior
    
    print(f"Found {len(png_files)} PNG files for GIF creation")
    
    if not png_files:
        print("No PNG files found for GIF creation")
        return

    if use_imageio and IMAGEIO_AVAILABLE:
        # Use imageio which is typically faster than PIL for GIF creation
        images = []
        for filename in png_files:
            img_path = os.path.join(frame_folder, filename)
            try:
                images.append(imageio.imread(img_path))
            except Exception as e:
                print(f"Error reading {img_path}: {e}")
        
        gif_path = os.path.join(frame_folder, f"{name}.gif")
        start_time = time.time()
        imageio.mimsave(gif_path, images, duration=duration)
        end_time = time.time()
        print(f"Created GIF with {len(images)} frames at {gif_path} in {end_time - start_time:.3f} seconds")
    else:
        # Fallback to PIL method
        start_time = time.time()
        frames = [Image.open(os.path.join(frame_folder, image)) for image in png_files]
        print(f"Loaded {len(frames)} frames")
        
        if frames:
            frame_one = frames[0]
            gif_path = os.path.join(frame_folder, f"{name}.gif")
            frame_one.save(
                gif_path, 
                format="GIF", 
                append_images=frames[1:],  # Pass remaining frames as append_images
                save_all=True, 
                duration=duration, 
                loop=0
            )
            end_time = time.time()
            print(f"Created GIF with {len(frames)} frames at {gif_path} in {end_time - start_time:.3f} seconds")
        else:
            print("No frames loaded for GIF creation")

def batch_save_frames(figures, filenames, dpi: int = 150, batch_size: int = 5):
    """
    Batch save multiple figures to improve I/O performance
    
    Args:
        figures: list of matplotlib figure objects
        filenames: list of corresponding filenames
        dpi: dots per inch for saved images
        batch_size: number of figures to process in each batch
    """
    if len(figures) != len(filenames):
        raise ValueError("Number of figures must match number of filenames")
    
    total = len(figures)
    for i in range(0, total, batch_size):
        batch_end = min(i + batch_size, total)
        batch_figures = figures[i:batch_end]
        batch_filenames = filenames[i:batch_end]
        
        print(f"Processing batch {i//batch_size + 1}/{(total-1)//batch_size + 1}")
        
        for fig, fname in zip(batch_figures, batch_filenames):
            save_frame_optimized(fig, fname, dpi)
            plt.close(fig)  # Free memory immediately

def optimize_matplotlib_backend():
    """
    Configure matplotlib for optimal performance
    """
    # Set backend for best performance
    plt.switch_backend('Agg')
    
    # Optimize rcParams for faster rendering
    matplotlib.rcParams['figure.max_open_warning'] = 0  # Disable figure max warning
    matplotlib.rcParams['font.size'] = 10  # Smaller font for faster rendering during animation
    matplotlib.rcParams['axes.linewidth'] = 0.5  # Thinner lines for faster rendering
    matplotlib.rcParams['lines.linewidth'] = 1.0  # Thinner lines for faster rendering
    
    print("Matplotlib configured for optimized performance")

# Example usage functions that could be integrated into the notebook:

def setup_optimized_rendering():
    """
    Setup function to call at the beginning of the notebook for optimized rendering
    """
    optimize_matplotlib_backend()
    print("Optimized rendering setup complete")
    
    # Check if imageio is available for GIF creation
    if IMAGEIO_AVAILABLE:
        print("imageio is available for optimized GIF creation")
    else:
        print("imageio not available, GIF creation will use PIL")
    
    return IMAGEIO_AVAILABLE

if __name__ == "__main__":
    # Example usage
    print("Testing optimized functions...")
    
    # Test figure creation and saving
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    ax.set_title("Test Plot")
    
    save_frame_optimized(fig, "/workspace/test_frame.png", dpi=100)
    plt.close(fig)
    
    print("Functions created successfully!")