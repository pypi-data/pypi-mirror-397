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

from src.FloorplanAnalytics import run_stepDepth_SuperSeeded

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
obstacle_array[0:400, 0:1200] = 1  # Create a square obstacle
obstacle_array[800:1200, 0:1000] = 1  # Create a square obstacle

#start_points = np.array([[50, 50], [200, 800]])
start_points = np.array([[1900, 1900]])


# %%
########## Define the parameters ##########

use_cuda = False

resize = True
max_size = 200


# %% ########## Run the computation ##########

%%time
geodesicDistancesResults = run_stepDepth_SuperSeeded(obstacle_array=obstacle_array, start_positions=start_points, threads_per_block=(32,32), resize_for_compute=resize, max_size=max_size, max_iterations=100, use_cuda=use_cuda)

# %% 
# ########## Visualize the result ##########

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

im1 = ax1.imshow(obstacle_array, cmap='gray_r')
ax1.set_title('Input Grid with Obstacles')
fig.colorbar(im1, ax=ax1)

im2 = ax2.imshow(geodesicDistancesResults, cmap='Blues', interpolation='lanczos')
ax2.set_title('Connectivity Area for Each Pixel')
fig.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show()
# %%

