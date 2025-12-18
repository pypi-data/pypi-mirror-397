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

from src.FloorplanAnalytics import run_geodesicRange_SuperSeeded

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

# Parameters for ray shooting
max_distance = 300  # Maximum distance to walk

resize = True
max_size = 200


# %% ########## Run the computation ##########

%%time
area_results = run_geodesicRange_SuperSeeded(array=obstacle_array, max_distance=max_distance, threads_per_block=(32,32), resize_for_compute=resize, max_size=max_size, use_cuda=use_cuda)

# %% 
########## Create the color map ##########

from src.FloorplanAnalytics import create_gradient_cmap

colors = np.array([[88, 0, 57], [94, 34, 38], [187, 104, 129], [244, 207, 184], [249, 243, 205]])
positions = np.array([0.0, 0.25, 0.5, 0.75, 1])

customcmp = create_gradient_cmap(colors, positions)

# %% 
########## Visualize the result ##########


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

im1 = ax1.imshow(obstacle_array, cmap='gray_r')
ax1.set_title('Input Grid with Obstacles')
fig.colorbar(im1, ax=ax1)

im2 = ax2.imshow(area_results, cmap=customcmp, interpolation='lanczos')
ax2.set_title('Local connectivity')
fig.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show()

# %%
