import numba as nb
import numpy as np
from numba import cuda, jit, prange, int32, float32
import math

import matplotlib.pyplot as plt
from typing import Tuple

from .helper.Helperfunctions import * 

### cuda kernel ###


@cuda.jit(device=True)
def bresenham_ray_cuda(
    x0: int32,
    y0: int32,
    x1: int32,
    y1: int32,
    stop_array: np.ndarray,
    max_distance: float32,
    shape: tuple,
) -> tuple[int32, int32]:
    """
    CUDA kernel for performing bresenham's line based raycasting.
    Optimized version with early termination and reduced branching.

    Args:
        x0 (int32): The starting x-coordinate.
        y0 (int32): The starting y-coordinate.
        x1 (int32): The ending x-coordinate.
        y1 (int32): The ending y-coordinate

    Returns:
        hit_coordinate (Tuple[int32, int32]): The hit x and y coordinates of the ray.
    """
    # Pre-computed constant for diagonal movement distance
    SQRT2 = float32(1.4142135623730951)  # sqrt(2)
    shape_w = shape[1]
    shape_h = shape[0]
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    x, y = x0, y0
    distance = float32(0.0)
    last_x, last_y = x0, y0

    while distance <= max_distance:
        # Optimized bounds check
        if x >= 0 and x < shape_w and y >= 0 and y < shape_h:
            if stop_array[y, x] != 0:
                break
            last_x, last_y = x, y
            # Early exit if reached target
            if x == x1 and y == y1:
                break
        elif x == x1 and y == y1:
            break
        
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
        
        # Calculate distance: diagonal if both moved, otherwise 1.0
        if moved_x and moved_y:
            distance += SQRT2
        elif moved_x or moved_y:
            distance += float32(1.0)

    return last_x, last_y


@cuda.jit
def raycast_kernel(
    obstacle_array: np.ndarray,
    start_positions: np.ndarray,
    result_array: np.ndarray,
    max_distance: float32,
    iteration: int32,
) -> np.ndarray:
    """
    CUDA kernel for performing raycasting.
    Optimized with spatial distance checks and early termination.

    Args:
        obstacle_array (np.ndarray): 2D numpy array with obstacles (0: free, 1: obstacle)
        start_positions (np.ndarray): 2D array of starting positions, each row containing [x, y] coordinates
        result_array (np.ndarray): 2D array to store raycast results (0: not visible, 1+: iteration when became visible)
        max_distance (float32): Maximum distance to perform raycast
        iteration (int32): Current iteration number

    Returns:
        result (np.ndarray): 2D array with raycast results (0: not visible, 1+: iteration when became visible)
    """
    x, y = cuda.grid(2)
    width = obstacle_array.shape[1]
    height = obstacle_array.shape[0]
    
    if x < width and y < height:
        # Early exit if already processed
        if result_array[y, x] != 0:
            return
        
        num_starts = start_positions.shape[0]
        # Pre-compute squared max distance for faster comparison (avoid sqrt)
        max_dist_sq = max_distance * max_distance
        # Pre-compute conservative Manhattan threshold (sqrt(2) ≈ 1.414 for diagonal)
        manhattan_threshold = max_distance * float32(1.42)
        
        for i in range(num_starts):
            start_x, start_y = start_positions[i, 0], start_positions[i, 1]
            
            # Quick check for exact match
            if x == start_x and y == start_y:
                result_array[y, x] = iteration
                return
            
            # Fast distance check using Manhattan distance first (cheaper than Euclidean)
            dx = abs(x - start_x)
            dy = abs(y - start_y)
            manhattan_dist = dx + dy
            
            # Skip if Manhattan distance exceeds threshold (fast rejection)
            if manhattan_dist > manhattan_threshold:
                continue
            
            # More accurate check: skip if Euclidean distance squared exceeds max
            # Only compute if Manhattan check passed (saves expensive multiply for far points)
            dist_sq = float32(dx * dx + dy * dy)
            if dist_sq > max_dist_sq:
                continue
            
            # Perform raycast only if within reasonable distance
            hit_x, hit_y = bresenham_ray_cuda(
                int32(start_x),
                int32(start_y),
                int32(x),
                int32(y),
                obstacle_array,
                float32(max_distance),
                obstacle_array.shape,
            )
            
            if hit_x == x and hit_y == y:
                result_array[y, x] = iteration
                return


@cuda.jit
def find_border_pixels_kernel(
    result_array: np.ndarray,
    obstacle_array: np.ndarray,
    new_start_positions: np.ndarray,
    counter: np.ndarray,
) -> None:
    """
    CUDA kernel for finding border pixels.
    This function is executed on the GPU.

    Args:
        result_array (np.ndarray): 2D array with raycast results (0: not visible, 1+: iteration when became visible)
        obstacle_array (np.ndarray): 2D numpy array with obstacles (0: free, 1: obstacle)
        new_start_positions (np.ndarray): 2D array to store new starting positions, each row containing [x, y] coordinates
        counter (np.ndarray): 1D array to store the number of new starting positions found

    Returns:
        None (None): results are stored in new_start_positions and counter
    """
    x, y = cuda.grid(2)
    if x < result_array.shape[1] and y < result_array.shape[0]:
        # Only process visible pixels
        if result_array[y, x] == 0:
            return
        
        # Check all 8 neighbors for unvisited free pixels
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                
                # Bounds check
                if nx < 0 or nx >= result_array.shape[1] or ny < 0 or ny >= result_array.shape[0]:
                    continue
                
                # Check if neighbor is unvisited and free
                if result_array[ny, nx] == 0 and obstacle_array[ny, nx] == 0:
                    idx = cuda.atomic.add(counter, 0, 1)
                    if idx < new_start_positions.shape[0]:
                        new_start_positions[idx, 0] = nx
                        new_start_positions[idx, 1] = ny
                    return  # Exit after finding the first border pixel


def gpu_iterative_raycast(
    obstacle_array: np.ndarray,
    start_positions: np.ndarray,
    max_iterations: int,
    threads_per_block=(16, 16),
) -> np.ndarray:
    """
    Perform iterative raycasting on GPU using CUDA with expanding frontier.
    Optimized for large images with spatial distance checks and efficient memory usage.

    Args:
        obstacle_array (np.ndarray): 2D numpy array with obstacles (0: free, 1: obstacle)
        start_positions (np.ndarray): 2D array of initial starting positions, each row containing [x, y] coordinates
        max_iterations (int): Maximum number of iterations to perform
        threads_per_block (tuple): Threads per block configuration (default: (16, 16))

    Returns:
        result (np.ndarray): 2D array with raycast results (0: not visible, 1+: iteration when became visible)
    """
    result_array = np.zeros_like(obstacle_array, dtype=np.int32)

    # Convert arrays to CUDA device arrays (keep on device)
    d_obstacle_array = cuda.to_device(obstacle_array)
    d_result_array = cuda.to_device(result_array)

    # Set up the grid and block dimensions
    # Use larger blocks for better GPU utilization on large images
    if obstacle_array.size > 1000000:  # For images > 1M pixels
        if threads_per_block == (16, 16):
            threads_per_block = (32, 32)  # Use larger blocks for big images
    
    blocks_per_grid = (
        (obstacle_array.shape[1] + threads_per_block[0] - 1) // threads_per_block[0],
        (obstacle_array.shape[0] + threads_per_block[1] - 1) // threads_per_block[1],
    )

    # Calculate max_distance (diagonal of the array)
    max_distance = float32(np.sqrt(obstacle_array.shape[0] ** 2 + obstacle_array.shape[1] ** 2))

    # Estimate border pixel count more conservatively
    # Border pixels are typically 4-8x the perimeter, but we use a reasonable upper bound
    # For expanding frontier, border grows but typically much less than all pixels
    height, width = obstacle_array.shape
    perimeter = 2 * (height + width)
    # Estimate: 4x perimeter is usually enough, but cap at reasonable size
    estimated_border_size = min(perimeter * 4, obstacle_array.size // 4)
    estimated_border_size = max(estimated_border_size, 1000)  # Minimum allocation
    
    # Allocate device memory for border pixels (reused across iterations)
    d_new_start_positions = cuda.device_array((estimated_border_size, 2), dtype=np.int32)
    d_counter = cuda.to_device(np.array([0], dtype=np.int32))
    
    # Keep start_positions on device to avoid repeated transfers
    start_positions = np.asarray(start_positions, dtype=np.int32)
    d_start_positions = cuda.to_device(start_positions)

    for iteration in range(1, max_iterations + 1):
        # Perform raycast
        raycast_kernel[blocks_per_grid, threads_per_block](
            d_obstacle_array, d_start_positions, d_result_array, max_distance, int32(iteration)
        )

        # Find new border pixels
        cuda.synchronize()
        # Reset counter
        d_counter[0] = 0
        find_border_pixels_kernel[blocks_per_grid, threads_per_block](
            d_result_array, d_obstacle_array, d_new_start_positions, d_counter
        )

        # Check if we have new starting positions
        cuda.synchronize()
        new_start_count = d_counter.copy_to_host()[0]
        
        if new_start_count == 0:
            break
        
        # Handle case where we exceeded estimated size
        if new_start_count > estimated_border_size:
            # Fallback: copy what we have and continue with reduced set
            new_start_count = estimated_border_size
        
        # Update start_positions on device for next iteration
        if new_start_count > 0:
            # Copy only the needed portion to host, then back to device
            # This is still more efficient than allocating new device array each time
            temp_positions = d_new_start_positions[:new_start_count].copy_to_host()
            d_start_positions = cuda.to_device(temp_positions)

    # Copy the final result back to the host
    result_array = d_result_array.copy_to_host()

    return result_array


### cpu kernel ###


@jit(nopython=True)
def bresenham_ray_cpu(
    x0: int32,
    y0: int32,
    x1: int32,
    y1: int32,
    stop_array: np.ndarray,
    max_distance: float32,
    shape: tuple,
) -> Tuple[int32, int32]:
    """
    CPU function for calculating bresenham's line based raycasting.
    This function is executed on the CPU in parallel.

    Args:
        x0 (int32): The starting x-coordinate.
        y0 (int32): The starting y-coordinate.
        x1 (int32): The ending x-coordinate.
        y1 (int32): The ending y-coordinate
        stop_array (np.ndarray): A 2D array representing the input mask as np array where with obstacles 1 and free space as 0.
        max_distance (float32): The maximum distance that the rays can travel.
        shape (tuple): The shape of the input mask.

    Returns:
        hit_coordinate (Tuple[int32, int32]): The hit x and y coordinates of the ray.
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = int32(1) if x0 < x1 else int32(-1)
    sy = int32(1) if y0 < y1 else int32(-1)
    err = dx - dy

    x, y = x0, y0
    distance = float32(0.0)
    last_x, last_y = x0, y0

    while distance <= max_distance:
        if int32(0) <= x < int32(shape[1]) and int32(0) <= y < int32(shape[0]):
            if stop_array[int32(y), int32(x)] != 0:
                break
            last_x, last_y = x, y
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
            distance += float32(1.0) if dy <= dx else float32(np.sqrt(2.0) / 2.0)
        if e2 < dx:
            err += dx
            y += sy
            distance += float32(1.0) if dx < dy else float32(np.sqrt(2.0) / 2.0)

    return last_x, last_y


@jit(nopython=True, parallel=True)
def raycast_cpu(
    obstacle_array: np.ndarray,
    start_positions: np.ndarray,
    result_array: np.ndarray,
    max_distance: float,
    iteration: int,
) -> None:
    """
    CPU function for performing raycasting.
    This function is executed on the CPU in parallel.

    Args:
        obstacle_array (np.ndarray): 2D numpy array with obstacles (0: free, 1: obstacle)
        start_positions (np.ndarray): 2D array of starting positions, each row containing [x, y] coordinates
        result_array (np.ndarray): 2D array to store raycast results (0: not visible, 1+: iteration when became visible)
        max_distance (float): Maximum distance to perform raycast
        iteration (int): Current iteration number

    Returns:
        None (None): results are stored in result_array
    """
    for y in prange(obstacle_array.shape[0]):
        for x in range(obstacle_array.shape[1]):
            for i in range(start_positions.shape[0]):
                start_x, start_y = start_positions[i]
                if x == start_x and y == start_y:
                    if result_array[y, x] == 0:
                        result_array[y, x] = iteration
                    break
                hit_x, hit_y = bresenham_ray_cpu(
                    int(start_x),
                    int(start_y),
                    int(x),
                    int(y),
                    obstacle_array,
                    float(max_distance),
                    obstacle_array.shape,
                )
                if hit_x == x and hit_y == y and result_array[y, x] == 0:
                    result_array[y, x] = iteration
                    break


@jit(nopython=True)
def find_border_pixels_cpu(
    result_array: np.ndarray, obstacle_array: np.ndarray
) -> np.ndarray:
    """
    CPU function for finding border pixels.
    This function is executed on the CPU in parallel.

    Args:
        result_array (np.ndarray): 2D array with raycast results (0: not visible, 1+: iteration when became visible)
        obstacle_array (np.ndarray): 2D numpy array with obstacles (0: free, 1: obstacle)

    Returns:
        result (np.ndarray): 2D array with new starting positions (x, y) coordinates
    """
    height, width = result_array.shape
    new_start_positions = np.empty((height * width, 2), dtype=np.int32)
    counter = 0

    for y in range(height):
        for x in range(width):
            if result_array[y, x] != 0:
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < width
                            and 0 <= ny < height
                            and result_array[ny, nx] == 0
                            and obstacle_array[ny, nx] == 0
                        ):
                            new_start_positions[counter, 0] = nx
                            new_start_positions[counter, 1] = ny
                            counter += 1
                            break
                    if (
                        counter > 0
                        and new_start_positions[counter - 1, 0] == nx
                        and new_start_positions[counter - 1, 1] == ny
                    ):
                        break

    return new_start_positions[:counter]


def cpu_iterative_raycast(
    obstacle_array: np.ndarray, start_positions: np.ndarray, max_iterations: int
) -> np.ndarray:
    """
    Perform iterative raycasting on CPU with expanding frontier.

    Args:
        obstacle_array (np.ndarray): 2D numpy array with obstacles (0: free, 1: obstacle)
        start_positions (np.ndarray): 2D array of initial starting positions, each row containing [x, y] coordinates
        max_iterations (int): Maximum number of iterations to perform

    Returns:
        result (np.ndarray): 2D array with raycast results (0: not visible, 1+: iteration when became visible)
    """
    result_array = np.zeros_like(obstacle_array, dtype=np.int32)
    max_distance = np.sqrt(obstacle_array.shape[0] ** 2 + obstacle_array.shape[1] ** 2)

    for iteration in range(1, max_iterations + 1):
        raycast_cpu(
            obstacle_array, start_positions, result_array, max_distance, iteration
        )
        new_start_positions = find_border_pixels_cpu(result_array, obstacle_array)

        if len(new_start_positions) == 0:
            break

        start_positions = new_start_positions

    return result_array
