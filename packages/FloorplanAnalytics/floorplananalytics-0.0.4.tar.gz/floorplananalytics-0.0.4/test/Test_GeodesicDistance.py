# %%

########## Import packages ##########

import numpy as np
import pandas as pd
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

from src.FloorplanAnalytics import run_geodesicDistance


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

start_points = np.zeros(shape, dtype=np.int32)
start_points[50:60, 50:60] = 1
start_points[200:210, 800:810] = 1

# %%
########## Define the parameters ##########

use_cuda = True

resize = True
max_size = 200

# %%
########## Define the parameters ##########
import math

if resize:
    max_iterations = int(math.sqrt((max_size+max_size)**2))
else:
    shape_max = np.max(shape)
    max_iterations = int(math.sqrt((shape_max+shape_max)**2))


# %% ########## Run the computation ##########

%%time
results = run_geodesicDistance(mask=obstacle_array, start_points=start_points, threads_per_block=(32,32), resize_for_compute=resize, max_size=max_size, max_iterations=max_iterations, use_cuda=use_cuda)

# %%
########## Visualize result ##########


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

im1 = ax1.imshow(obstacle_array, cmap='gray_r')
ax1.set_title('Input Grid with Obstacles')
fig.colorbar(im1, ax=ax1)

im2 = ax2.imshow(results, cmap='Reds', interpolation='lanczos')
ax2.set_title('Connectivity Distance for Each Pixel')
fig.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show()
# %%

