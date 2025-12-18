# %%
########## |Tested successfully| ##########

########## Import packages ##########

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import os
import shutil
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# %%
########## Check GPU availability ##########

!nvidia-smi

# %%
########## Import functions ##########

from src.FloorplanAnalytics import run_geodesicRange, run_geodesicDistance_Aggregated

# %%
########## Define the test grid ##########

# Define the shape of the grid
shape = (2000, 2000)

# Create a stop array with some obstacles
obstacle_array = np.zeros(shape, dtype=np.int32)
obstacle_array[600:2000, 600:2000] = 1  # Create a square obstacle
obstacle_array[600:1400, 600:1100] = 0  # Create a square obstacle
obstacle_array[1000:1250, 1000:2000] = 0  # Create a square obstacle
obstacle_array[1000:2000, 1800:2000] = 0  # Create a square obstacle

# %%
########## Define the parameters ##########

use_cuda = True

# Parameters for geodesic range
max_distance = None  # None = unlimited (all reachable pixels)

resize = True
max_size = 512

batch_size = 4096  # Pixels per GPU batch for large distances (higher = faster but more memory)

# %% ########## Run the computation (Unlimited Range) ##########

%%time
range_results = run_geodesicRange(
    array=obstacle_array, 
    max_distance=max_distance,  # None = unlimited distance
    batch_size=batch_size,
    threads_per_block=(16, 16), 
    resize_for_compute=resize, 
    max_size=max_size, 
    use_cuda=use_cuda
)

# %% 
########## Create the color map ##########

from src.FloorplanAnalytics import create_gradient_cmap

colors = np.array([[88, 0, 57], [94, 34, 38], [187, 104, 129], [244, 207, 184], [249, 243, 205]])
positions = np.array([0.0, 0.25, 0.5, 0.75, 1])

customcmp = create_gradient_cmap(colors, positions)

# %% 
########## Visualize the result (Unlimited Range) ##########

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

im1 = ax1.imshow(obstacle_array, cmap='gray_r')
ax1.set_title('Input Grid with Obstacles')
fig.colorbar(im1, ax=ax1)

im2 = ax2.imshow(range_results, cmap=customcmp, interpolation='lanczos')
ax2.set_title(f'Geodesic Range (max_distance={max_distance})')
fig.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show()

# %%

max_distance_limited = 300  # Same as original test


# %% ########## Run with limited distance for comparison ##########

%%time
range_results_limited = run_geodesicRange(
    array=obstacle_array, 
    max_distance=max_distance_limited,
    batch_size=batch_size,
    threads_per_block=(16, 16), 
    resize_for_compute=resize, 
    max_size=max_size, 
    use_cuda=use_cuda
)

# %% 
########## Visualize limited range result ##########

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

im1 = ax1.imshow(obstacle_array, cmap='gray_r')
ax1.set_title('Input Grid with Obstacles')
fig.colorbar(im1, ax=ax1)

im2 = ax2.imshow(range_results_limited, cmap=customcmp, interpolation='lanczos')
ax2.set_title(f'Geodesic Range (max_distance={max_distance_limited})')
fig.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show()

# %% ########## Run aggregated distance computation ##########

%%time
distance_results = run_geodesicDistance_Aggregated(
    array=obstacle_array, 
    max_distance=300,  # Limit for performance
    batch_size=batch_size,
    threads_per_block=(16, 16), 
    resize_for_compute=resize, 
    max_size=max_size, 
    use_cuda=use_cuda
)

# %% 
########## Visualize aggregated distance result ##########

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

im1 = ax1.imshow(obstacle_array, cmap='gray_r')
ax1.set_title('Input Grid with Obstacles')
fig.colorbar(im1, ax=ax1)

im2 = ax2.imshow(distance_results, cmap=customcmp, interpolation='lanczos')
ax2.set_title('Aggregated Geodesic Distance (Integration)')
fig.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show()

# %%
########## Compare all three results side by side ##########

fig, axes = plt.subplots(2, 2, figsize=(20, 20))

# Input
axes[0, 0].imshow(obstacle_array, cmap='gray_r')
axes[0, 0].set_title('Input Grid with Obstacles')

# Unlimited range
im1 = axes[0, 1].imshow(range_results, cmap=customcmp, interpolation='lanczos')
axes[0, 1].set_title('Geodesic Range (Unlimited)')
fig.colorbar(im1, ax=axes[0, 1])

# Limited range
im2 = axes[1, 0].imshow(range_results_limited, cmap=customcmp, interpolation='lanczos')
axes[1, 0].set_title(f'Geodesic Range (max_distance={max_distance_limited})')
fig.colorbar(im2, ax=axes[1, 0])

# Aggregated distance
im3 = axes[1, 1].imshow(distance_results, cmap=customcmp, interpolation='lanczos')
axes[1, 1].set_title('Aggregated Distance')
fig.colorbar(im3, ax=axes[1, 1])

plt.tight_layout()
plt.show()

# %%
