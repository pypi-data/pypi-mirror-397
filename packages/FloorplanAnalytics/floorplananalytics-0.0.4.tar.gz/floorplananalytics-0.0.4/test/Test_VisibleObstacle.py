# %%
########## |Tested successfully| ##########

########## Import packages ##########

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import os
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

from src.FloorplanAnalytics import run_visibleObstacle

# %%
########## Define the test grid ##########

# Define the shape of the grid
shape = (1000, 1000)

# Create a stop array with some obstacles
obstacle_array = np.zeros(shape, dtype=np.int32)
obstacle_array[300:1000, 300:1000] = 1  # Create a square obstacle
obstacle_array[300:700, 300:550] = 0  # Create a square obstacle
obstacle_array[500:625, 500:1000] = 0  # Create a square obstacle
obstacle_array[500:1000, 900:1000] = 0  # Create a square obstacle

# %%
########## Define the target array ##########

# "lines" along 3 outsides of the array
target_array = np.zeros(shape, dtype=np.int32)
target_array[0:10, 0:1000] = 1
target_array[0:1000, 0:10] = 1
#target_array[990:1000, 0:1000] = 1

# %%
########## Define the parameters ##########

use_cuda = True

# Parameters for ray shooting
num_rays = 360  # One ray per degree
max_distance = 1000  # Maximum distance to shoot rays

resize = False
max_size = 200


# %% ########## Run the computation ##########

%%time
hit_count_results = run_visibleObstacle(stop_array=obstacle_array, target_array=target_array, num_rays=num_rays, max_distance=max_distance, threads_per_block=(32,32), resize_for_compute=resize, max_size=max_size, use_cuda=use_cuda)

# %%
########## Create the color map ##########

from src.FloorplanAnalytics import create_gradient_cmap

colors = np.array([[255, 128, 0], [255, 255, 0], [150, 207, 10], [66, 160, 14]])
positions = np.array([0, 0.33, 0.66, 1])

# %%
########## Visualize the result ##########

customcmp = create_gradient_cmap(colors, positions)

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(30, 10))

im1 = ax1.imshow(obstacle_array, cmap='gray_r')
ax1.set_title('Input Grid with Obstacles')
fig.colorbar(im1, ax=ax1)

im2 = ax2.imshow(target_array, cmap='hot')
ax2.set_title('Target Points')
fig.colorbar(im2, ax=ax2)

im3 = ax3.imshow(hit_count_results, cmap=customcmp)
ax3.set_title('Number of Rays Hitting Targets for Each Pixel')
fig.colorbar(im3, ax=ax3)

plt.tight_layout()
plt.show()

# %%

