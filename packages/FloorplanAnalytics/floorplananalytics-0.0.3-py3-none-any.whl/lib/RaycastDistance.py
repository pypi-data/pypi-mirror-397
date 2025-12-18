import numba as nb
import numpy as np
from numba import cuda, int32, float32, jit, prange
import math

from typing import Tuple

from .helper.Helperfunctions import * 


### cuda kernel ###

# Constants for better performance
INF_FLOAT = float32(3.4028235e+38)  # Approximate float32 max
SQRT2 = float32(1.4142135623730951)  # math.sqrt(2)

@cuda.jit(device=True)
def bresenham_ray_distance_cuda(x0: int32, y0: int32, x1: int32, y1: int32, mask: np.ndarray, obstacle_array: np.ndarray, max_distance: float32, shape: tuple) -> float32:
    """
    CUDA device function for performing bresenham's line based raycasting and returning distance to obstacle hit.
    Optimized version with reduced branching and faster distance calculation.
    This function is executed on the GPU.

    Args:
        x0 (int32): The starting x-coordinate.
        y0 (int32): The starting y-coordinate.
        x1 (int32): The ending x-coordinate.
        y1 (int32): The ending y-coordinate.
        mask (np.ndarray): A 2D array where 1 means obstacle (blocking), 0 means free space.
        obstacle_array (np.ndarray): A 2D array where 1 means target obstacle, 0 means free space.
        max_distance (float32): The maximum distance that the rays can travel.
        shape (tuple): The shape of the input array.

    Returns:
        distance (float32): The distance to the target obstacle hit, or 0.0 if mask obstacle hit or no obstacle was hit.
    """
    shape_w = shape[1]
    shape_h = shape[0]
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    x, y = x0, y0
    distance = float32(0.0)

    while distance <= max_distance:
        # Early exit if reached target
        if x == x1 and y == y1:
            break
        
        # Check obstacles at current position BEFORE moving (matching VisibleObstacle.py pattern)
        # This ensures we check every position, including boundary pixels, before moving
        if x >= 0 and x < shape_w and y >= 0 and y < shape_h:
            # First check if we hit a mask obstacle (blocking obstacle) - return 0 immediately
            if mask[y, x] == 1:
                return float32(0.0)
            # Then check if we hit a target obstacle (obstacle_array) - return distance immediately
            if obstacle_array[y, x] == 1:
                return distance
        
        # Bresenham step - optimized with moved flags
        e2 = 2 * err
        moved_x = False
        moved_y = False
        
        if e2 > -dy:
            err -= dy
            x += sx
            moved_x = True
        if e2 < dx:
            err += dx
            y += sy
            moved_y = True
        
        # Optimized distance calculation: diagonal if both moved, otherwise 1.0
        if moved_x and moved_y:
            distance += SQRT2
        elif moved_x or moved_y:
            distance += float32(1.0)
        else:
            break  # No movement, exit loop
        
        # Check if ray went out of bounds after moving
        # We've already checked obstacles at all valid positions before moving
        if x < 0 or x >= shape_w or y < 0 or y >= shape_h:
            # Ray hit the image boundary - we've checked all valid positions
            # Boundary is not an obstacle, return 0
            break

    # No obstacle hit within max_distance (boundary is not an obstacle)
    return float32(0.0)

@cuda.jit
def raycast_min_distance_cuda(mask: np.ndarray, obstacle_array: np.ndarray, num_rays: int32, max_distance: float32, output: np.ndarray):
    """
    CUDA kernel for performing ray casting and calculating minimum distance to obstacles for all pixels.
    Optimized version with cached shape values and improved minimum tracking.
    This function is executed on the GPU.

    Args:
        mask (np.ndarray): A 2D array representing the input mask where 0 is valid and 1 is excluded.
        obstacle_array (np.ndarray): A 2D array where obstacles are 1 and free space is 0.
        num_rays (int32): The number of rays to be shot from each pixel.
        max_distance (float32): The maximum distance that the rays can travel.
        output (np.ndarray): A 2D array to store the minimum distance for each pixel.

    Returns:
        None (None):
        The minimum distance for each pixel is stored in the output array.
    """
    x, y = cuda.grid(2)
    
    # Cache shape dimensions locally to avoid repeated memory accesses
    shape_h = mask.shape[0]
    shape_w = mask.shape[1]
    shape = (shape_h, shape_w)
    
    if x < shape_w and y < shape_h:
        # If mask pixel is 0 (valid), process it; if mask is 1 (excluded), skip
        if mask[y, x] == 0:
            # Process this pixel - cast rays and find minimum distance
            # Use INF_FLOAT as initial value for easier minimum tracking
            min_distance = INF_FLOAT
            
            # Precompute constants to avoid repeated calculations
            angle_step = float32(2.0 * math.pi / num_rays)
            max_dist_int = int32(max_distance)

            for i in range(num_rays):
                angle = angle_step * i
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)
                # Use integer arithmetic where possible
                end_x = int32(x + max_dist_int * cos_angle)
                end_y = int32(y + max_dist_int * sin_angle)
                
                # Cast ray and get distance to obstacle
                ray_distance = bresenham_ray_distance_cuda(x, y, end_x, end_y, mask, obstacle_array, max_distance, shape)
                
                # Update minimum distance (only if obstacle was hit, i.e., distance > 0)
                if ray_distance > float32(0.0) and ray_distance < min_distance:
                    min_distance = ray_distance
                    # Early exit optimization: if we find a hit at minimum possible distance (orthogonal neighbor = 1.0),
                    # we can stop since no closer hit is possible
                    if min_distance <= float32(1.0):
                        break

            # Store minimum distance (0.0 if no obstacle was hit, otherwise minimum distance)
            if min_distance < INF_FLOAT:
                output[y, x] = min_distance
            else:
                output[y, x] = float32(0.0)
        else:
            # Mask pixel is 1 (excluded), return 0
            output[y, x] = float32(0.0)

def raycast_min_distance_cuda_wrapper(mask: np.ndarray, obstacle_array: np.ndarray, num_rays: int32, max_distance: float32, threads_per_block: Tuple[int, int]=(16, 16)) -> np.ndarray:
    """
    Wrapper function for performing ray casting and calculating minimum distance to obstacles for all pixels.
    This function is executed on the GPU.

    Args:
        mask (np.ndarray): A 2D array representing the input mask where 0 is valid and 1 is excluded.
        obstacle_array (np.ndarray): A 2D array where obstacles are 1 and free space is 0.
        num_rays (int32): The number of rays to be shot from each pixel.
        max_distance (float32): The maximum distance that the rays can travel.
        threads_per_block (Tuple[int, int]): The number of threads per block. Defaults to (16, 16).

    Returns:
        result (np.ndarray):
        A 2D array representing the minimum distance to obstacles for each pixel.
    """
    shape = mask.shape
    mask_gpu = cuda.to_device(mask)
    obstacle_array_gpu = cuda.to_device(obstacle_array)
    output_gpu = cuda.to_device(np.zeros(shape, dtype=np.float32))

    blocks_per_grid = (
        (shape[1] + threads_per_block[0] - 1) // threads_per_block[0],
        (shape[0] + threads_per_block[1] - 1) // threads_per_block[1]
    )

    raycast_min_distance_cuda[blocks_per_grid, threads_per_block](
        mask_gpu, obstacle_array_gpu, num_rays, max_distance, output_gpu
    )
    
    # Synchronize is implicit in copy_to_host, but explicit sync can help with timing
    # Remove explicit sync for better performance (copy_to_host will sync anyway)
    return output_gpu.copy_to_host()


### cpu kernel ###

@jit(nopython=True)
def bresenham_ray_distance_cpu(x0: int32, y0: int32, x1: int32, y1: int32, mask: np.ndarray, obstacle_array: np.ndarray, max_distance: float32, shape: tuple) -> float32:
    """
    CPU function for calculating bresenham's line based raycasting and returning distance to obstacle hit.
    This function is executed on the CPU.

    Args:
        x0 (int32): The starting x-coordinate.
        y0 (int32): The starting y-coordinate.
        x1 (int32): The ending x-coordinate.
        y1 (int32): The ending y-coordinate.
        mask (np.ndarray): A 2D array where 1 means obstacle (blocking), 0 means free space.
        obstacle_array (np.ndarray): A 2D array where 1 means target obstacle, 0 means free space.
        max_distance (float32): The maximum distance that the rays can travel.
        shape (tuple): The shape of the input array.

    Returns:
        distance (float32): The distance to the target obstacle hit, or 0.0 if mask obstacle hit or no obstacle was hit.
    """
    shape_w = int32(shape[1])
    shape_h = int32(shape[0])
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = int32(1) if x0 < x1 else int32(-1)
    sy = int32(1) if y0 < y1 else int32(-1)
    err = dx - dy

    x, y = x0, y0
    distance = float32(0.0)
    
    SQRT2_CPU = float32(1.4142135623730951)  # sqrt(2)

    while distance <= max_distance:
        if x == x1 and y == y1:
            break
        
        # Check obstacles at current position BEFORE moving
        # This ensures we check every position, including boundary pixels before they go out of bounds
        if x >= int32(0) and x < shape_w and y >= int32(0) and y < shape_h:
            # First check if we hit a mask obstacle (blocking obstacle) - return 0 immediately
            if mask[int32(y), int32(x)] == 1:
                return float32(0.0)
            # Then check if we hit a target obstacle (obstacle_array) - return distance
            if obstacle_array[int32(y), int32(x)] == 1:
                return distance
        
        # Store current position before moving (in case next move goes out of bounds)
        prev_x, prev_y = x, y
        prev_distance = distance
        
        # Bresenham step - optimized with moved flags
        e2 = 2 * err
        moved_x = False
        moved_y = False
        
        if e2 > -dy:
            err -= dy
            x += sx
            moved_x = True
        if e2 < dx:
            err += dx
            y += sy
            moved_y = True
        
        # Optimized distance calculation: diagonal if both moved, otherwise 1.0
        if moved_x and moved_y:
            distance += SQRT2_CPU
        elif moved_x or moved_y:
            distance += float32(1.0)
        else:
            break  # No movement, exit loop
        
        # Check if ray went out of bounds after moving
        if x < int32(0) or x >= shape_w or y < int32(0) or y >= shape_h:
            # Ray hit the image boundary
            # We already checked obstacles at the previous position (prev_x, prev_y) above
            # If we found an obstacle there, we would have returned already
            # Boundary is not an obstacle, return 0
            break

    # No obstacle hit within max_distance (boundary is not an obstacle)
    return float32(0.0)

@jit(nopython=True, parallel=True)
def raycast_min_distance_cpu(mask: np.ndarray, obstacle_array: np.ndarray, num_rays: int32, max_distance: float32) -> np.ndarray:
    """
    CPU function for performing ray casting and calculating minimum distance to obstacles for all pixels.
    This function is executed on the CPU in parallel.

    Args:
        mask (np.ndarray): A 2D array representing the input mask where 0 is valid and 1 is excluded.
        obstacle_array (np.ndarray): A 2D array where obstacles are 1 and free space is 0.
        num_rays (int32): The number of rays to be shot from each pixel.
        max_distance (float32): The maximum distance that the rays can travel.

    Returns:
        result (np.ndarray):
        A 2D array representing the minimum distance to obstacles for each pixel.
    """
    shape = mask.shape
    output = np.zeros(shape, dtype=np.float32)

    for y in prange(shape[0]):
        for x in range(shape[1]):
            # If mask pixel is 0 (valid), process it; if mask is 1 (excluded), skip
            if mask[y, x] == 0:
                min_distance = float32(0.0)
                found_hit = False
                
                for i in range(num_rays):
                    angle = 2 * np.pi * i / num_rays
                    end_x = int32(x + max_distance * np.cos(angle))
                    end_y = int32(y + max_distance * np.sin(angle))
                    
                    # Cast ray and get distance to obstacle
                    ray_distance = bresenham_ray_distance_cpu(x, y, end_x, end_y, mask, obstacle_array, max_distance, shape)
                    
                    # Update minimum distance (only if obstacle was hit, i.e., distance > 0)
                    if ray_distance > float32(0.0):
                        found_hit = True
                        if min_distance == float32(0.0) or ray_distance < min_distance:
                            min_distance = ray_distance

                # Store minimum distance (0.0 if no obstacle was hit, otherwise minimum distance)
                if found_hit:
                    output[y, x] = min_distance
                else:
                    output[y, x] = 0.0
            else:
                # Mask pixel is 1 (excluded), return 0
                output[y, x] = 0.0

    return output

