import numpy as np
from numba import cuda, njit, prange
import math
from typing import Tuple

### CPU implementation using two-pass distance transform ###

@njit
def _distance_transform_pass_1(dist: np.ndarray) -> None:
    """First pass: top-left to bottom-right."""
    h, w = dist.shape
    for y in range(h):
        for x in range(w):
            d = dist[y, x]
            if y > 0:
                d = min(d, dist[y-1, x] + 1.0)
            if x > 0:
                d = min(d, dist[y, x-1] + 1.0)
            if y > 0 and x > 0:
                d = min(d, dist[y-1, x-1] + math.sqrt(2.0))
            if y < h - 1 and x > 0:
                d = min(d, dist[y+1, x-1] + math.sqrt(2.0))
            dist[y, x] = d

@njit
def _distance_transform_pass_2(dist: np.ndarray) -> None:
    """Second pass: bottom-right to top-left."""
    h, w = dist.shape
    for y in range(h - 1, -1, -1):
        for x in range(w - 1, -1, -1):
            d = dist[y, x]
            if y < h - 1:
                d = min(d, dist[y+1, x] + 1.0)
            if x < w - 1:
                d = min(d, dist[y, x+1] + 1.0)
            if y < h - 1 and x < w - 1:
                d = min(d, dist[y+1, x+1] + math.sqrt(2.0))
            if y > 0 and x < w - 1:
                d = min(d, dist[y-1, x+1] + math.sqrt(2.0))
            dist[y, x] = d

@njit(parallel=True)
def cpu_signed_distance_function(mask: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """
    Calculate signed distance field using two-pass distance transform.

    Args:
        mask: 0 = open space, 1 = ignored
        reference: 0 = ignored, >0 = target points

    Returns:
        Signed distance field (positive for open space, negative for obstacles)
    """
    h, w = mask.shape
    dist = np.full((h, w), float('inf'), dtype=np.float32)
    output = np.zeros((h, w), dtype=np.float32)
    
    # Initialize: set target points to 0
    for y in prange(h):
        for x in prange(w):
            if reference[y, x] > 0:
                dist[y, x] = 0.0
    
    # Two-pass distance transform (through all space)
    _distance_transform_pass_1(dist)
    _distance_transform_pass_2(dist)
    
    # Apply sign based on mask
    for y in prange(h):
        for x in prange(w):
            if mask[y, x] == 0:  # Open space
                output[y, x] = dist[y, x]
            else:  # Ignored/obstacle
                output[y, x] = -dist[y, x] if dist[y, x] < float('inf') else -1.0
    
    return output


### CUDA implementation using Jump Flood Algorithm (JFA) ###

@cuda.jit
def jfa_init_kernel(reference: np.ndarray, seed_x: np.ndarray, seed_y: np.ndarray) -> None:
    """Initialize seed coordinates for JFA. Each pixel stores the coordinates of its nearest seed."""
    x, y = cuda.grid(2)
    h, w = reference.shape
    
    if x < w and y < h:
        if reference[y, x] > 0:
            # This pixel is a seed - store its own coordinates
            seed_x[y, x] = x
            seed_y[y, x] = y
        else:
            # Not a seed - initialize to invalid (-1)
            seed_x[y, x] = -1
            seed_y[y, x] = -1

@cuda.jit
def jfa_step_kernel(seed_x_in: np.ndarray, seed_y_in: np.ndarray, 
                    seed_x_out: np.ndarray, seed_y_out: np.ndarray, 
                    step_size: int) -> None:
    """One step of Jump Flood Algorithm."""
    x, y = cuda.grid(2)
    h, w = seed_x_in.shape
    
    if x < w and y < h:
        best_x = seed_x_in[y, x]
        best_y = seed_y_in[y, x]
        
        # Calculate current best distance
        if best_x >= 0 and best_y >= 0:
            best_dist = (x - best_x) * (x - best_x) + (y - best_y) * (y - best_y)
        else:
            best_dist = 1e18  # Very large number
        
        # Check 8 neighbors at step_size distance
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx = x + dx * step_size
                ny = y + dy * step_size
                
                if 0 <= nx < w and 0 <= ny < h:
                    neighbor_seed_x = seed_x_in[ny, nx]
                    neighbor_seed_y = seed_y_in[ny, nx]
                    
                    if neighbor_seed_x >= 0 and neighbor_seed_y >= 0:
                        # Calculate distance to this neighbor's seed
                        dist = (x - neighbor_seed_x) * (x - neighbor_seed_x) + (y - neighbor_seed_y) * (y - neighbor_seed_y)
                        
                        if dist < best_dist:
                            best_dist = dist
                            best_x = neighbor_seed_x
                            best_y = neighbor_seed_y
        
        seed_x_out[y, x] = best_x
        seed_y_out[y, x] = best_y

@cuda.jit
def jfa_compute_distance_kernel(seed_x: np.ndarray, seed_y: np.ndarray, 
                                 mask: np.ndarray, output: np.ndarray) -> None:
    """Compute final signed distance from seed coordinates."""
    x, y = cuda.grid(2)
    h, w = seed_x.shape
    
    if x < w and y < h:
        sx = seed_x[y, x]
        sy = seed_y[y, x]
        
        if sx >= 0 and sy >= 0:
            # Euclidean distance to nearest seed
            dist = math.sqrt(float((x - sx) * (x - sx) + (y - sy) * (y - sy)))
        else:
            dist = -1.0  # No seed found
        
        # Apply sign based on mask
        if mask[y, x] == 0:  # Open space
            output[y, x] = dist
        else:  # Obstacle
            output[y, x] = -dist

def cuda_signed_distance_function(mask: np.ndarray, reference: np.ndarray, threads_per_block: Tuple[int, int] = (16, 16)) -> np.ndarray:
    """
    Calculate signed distance field on GPU using Jump Flood Algorithm.

    Args:
        mask: 0 = open space, 1 = ignored
        reference: 0 = ignored, >0 = target points
        threads_per_block: CUDA thread block size

    Returns:
        Signed distance field
    """
    h, w = mask.shape
    blocks_per_grid = (
        (w + threads_per_block[0] - 1) // threads_per_block[0],
        (h + threads_per_block[1] - 1) // threads_per_block[1]
    )
    
    # Allocate device arrays for seed coordinates
    d_seed_x = cuda.device_array((h, w), dtype=np.int32)
    d_seed_y = cuda.device_array((h, w), dtype=np.int32)
    d_seed_x_temp = cuda.device_array((h, w), dtype=np.int32)
    d_seed_y_temp = cuda.device_array((h, w), dtype=np.int32)
    d_reference = cuda.to_device(reference)
    d_mask = cuda.to_device(mask)
    d_output = cuda.device_array((h, w), dtype=np.float32)
    
    # Initialize seeds
    jfa_init_kernel[blocks_per_grid, threads_per_block](d_reference, d_seed_x, d_seed_y)
    cuda.synchronize()

    # Jump Flood passes: start with step size = max dimension / 2, halve each iteration
    max_dim = max(h, w)
    step_size = 1
    while step_size < max_dim:
        step_size *= 2
    step_size //= 2
    
    # Ping-pong between buffers
    use_temp = False
    while step_size >= 1:
        if use_temp:
            jfa_step_kernel[blocks_per_grid, threads_per_block](
                d_seed_x_temp, d_seed_y_temp, d_seed_x, d_seed_y, step_size
            )
        else:
            jfa_step_kernel[blocks_per_grid, threads_per_block](
                d_seed_x, d_seed_y, d_seed_x_temp, d_seed_y_temp, step_size
            )
        cuda.synchronize()
        use_temp = not use_temp
        step_size //= 2
    
    # Use the correct output buffer
    if use_temp:
        final_seed_x = d_seed_x_temp
        final_seed_y = d_seed_y_temp
    else:
        final_seed_x = d_seed_x
        final_seed_y = d_seed_y
    
    # Compute final distances
    jfa_compute_distance_kernel[blocks_per_grid, threads_per_block](
        final_seed_x, final_seed_y, d_mask, d_output
    )
    cuda.synchronize()
    
    return d_output.copy_to_host()
