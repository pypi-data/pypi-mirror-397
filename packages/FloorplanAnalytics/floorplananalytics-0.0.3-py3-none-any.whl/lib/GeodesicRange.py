import numpy as np
import math
from numba import cuda, int32, int16, float32, jit, prange

from typing import List, Tuple

from .helper.Helperfunctions import * 

### cuda kernel ###


@cuda.jit
def bfs_eachToEach_kernel(array: np.ndarray, max_distance: float32, result: np.ndarray) -> None:
    """
    Optimized CUDA kernel for Breadth-First Search (BFS) from each point to each in a given maximum euclidian distance on a 2D array with obstacles.
    This version uses less memory per thread and is more efficient.
    The maximum search radius is limited by the visited array size (256x256 = 128 pixel radius).
    The maximum queue length is 4096 (reduced from 8192 to save memory).
    These are hard coded in the kernel because they need to be constant to compile.
    The result is the number of visited pixels for each point.
    The algorithm walks the grid in euclidean distance (8-directional).
    This function is executed on the GPU.

    Args:
        array (numpy.ndarray): The input 2D array with obstacles.
        max_distance (float): The maximum distance to travel.
        result (numpy.ndarray): The output 2D array to store the number of visited pixels for each point.

    Returns:
        None (None): The result is stored in the output array.
    """
    x, y = cuda.grid(2)
    if x >= array.shape[0] or y >= array.shape[1]:
        return

    # After inversion in wrapper: 0 = free space (walkable), 1 = obstacles (not walkable)
    if array[x, y] == 1:
        result[x, y] = 0
        return

    rows, cols = array.shape
    # Use int16 instead of int32 for visited array to save memory (256KB -> 128KB per thread)
    # Local coordinates are always in range [0, 256), so int16 is sufficient
    visited = cuda.local.array((256, 256), dtype=int16)
    # Reduced queue size from 8192 to 4096 to save memory
    # Queue stores (x, y, distance) - using int32 for x,y (global coordinates) and float32 for distance
    # Total queue memory: 4096 * (4 + 4 + 4) = 48KB per thread (vs 96KB with 8192 size)
    queue_x = cuda.local.array(4096, dtype=int32)
    queue_y = cuda.local.array(4096, dtype=int32)
    queue_dist = cuda.local.array(4096, dtype=float32)

    # Initialize visited array more efficiently using memset-like pattern
    # Only initialize the region we'll actually use (based on max_distance)
    max_radius = int(max_distance) + 1
    center = 128
    min_idx = max(0, center - max_radius)
    max_idx = min(256, center + max_radius + 1)
    for i in range(min_idx, max_idx):
        for j in range(min_idx, max_idx):
            visited[i, j] = 0

    queue_start, queue_end = 0, 1
    queue_x[0] = x
    queue_y[0] = y
    queue_dist[0] = 0.0
    visited[128, 128] = 1
    count = 1

    # Pre-compute direction offsets (compile-time constants)
    # Cardinal directions (distance = 1.0)
    # Diagonal directions (distance = 1.414)
    dx_offsets = cuda.local.array(8, dtype=int32)
    dy_offsets = cuda.local.array(8, dtype=int32)
    dist_offsets = cuda.local.array(8, dtype=float32)
    
    # Cardinal: (-1,0), (1,0), (0,-1), (0,1)
    dx_offsets[0], dy_offsets[0], dist_offsets[0] = -1, 0, 1.0
    dx_offsets[1], dy_offsets[1], dist_offsets[1] = 1, 0, 1.0
    dx_offsets[2], dy_offsets[2], dist_offsets[2] = 0, -1, 1.0
    dx_offsets[3], dy_offsets[3], dist_offsets[3] = 0, 1, 1.0
    # Diagonal: (-1,-1), (-1,1), (1,-1), (1,1)
    dx_offsets[4], dy_offsets[4], dist_offsets[4] = -1, -1, 1.4142135623730951
    dx_offsets[5], dy_offsets[5], dist_offsets[5] = -1, 1, 1.4142135623730951
    dx_offsets[6], dy_offsets[6], dist_offsets[6] = 1, -1, 1.4142135623730951
    dx_offsets[7], dy_offsets[7], dist_offsets[7] = 1, 1, 1.4142135623730951

    while queue_start < queue_end:
        cx = int(queue_x[queue_start])
        cy = int(queue_y[queue_start])
        current_distance = queue_dist[queue_start]
        queue_start += 1

        # Early termination: if current distance already exceeds max, skip
        if current_distance >= max_distance:
            continue

        for i in range(8):
            nx = cx + int(dx_offsets[i])
            ny = cy + int(dy_offsets[i])
            
            # Bounds check
            if nx < 0 or nx >= rows or ny < 0 or ny >= cols:
                continue
            
            # Check if cell is walkable (0 = free space, 1 = obstacle)
            if array[nx, ny] == 1:
                continue
            
            # Calculate local coordinates for visited array
            local_x = nx - x + 128
            local_y = ny - y + 128
            
            # Check if within visited array bounds
            if local_x < 0 or local_x >= 256 or local_y < 0 or local_y >= 256:
                continue
            
            # Check if already visited
            if visited[local_x, local_y] != 0:
                continue
            
            # Calculate new distance
            new_distance = current_distance + dist_offsets[i]
            
            # Check if within max distance
            if new_distance > max_distance:
                continue
            
            # Mark as visited and add to queue
            visited[local_x, local_y] = 1
            count += 1
            
            if queue_end < 4096:
                queue_x[queue_end] = nx
                queue_y[queue_end] = ny
                queue_dist[queue_end] = new_distance
                queue_end += 1

    result[x, y] = count


def run_bfs_cuda(
    array: np.ndarray,
    max_distance: float,
    threads_per_block: Tuple[int, int] = (32, 32),
):
    """
    Runs the Breadth-First Search (BFS) kernel on the GPU.

    Args:
        array (numpy.ndarray): The input 2D array with obstacles.
        max_distance (float): The maximum distance to travel.
        threads_per_block (tuple): The number of threads per block. Default is (4, 4).

    Returns:
        result (numpy.ndarray): The output 2D array with the number of visited pixels for each point.
    """
    result = np.zeros_like(array, dtype=np.int32)
    d_array = cuda.to_device(array)
    d_result = cuda.to_device(result)

    blocks_per_grid_x = math.ceil(array.shape[0] / threads_per_block[0])
    blocks_per_grid_y = math.ceil(array.shape[1] / threads_per_block[1])
    blocks_per_grid = (blocks_per_grid_x, blocks_per_grid_y)

    # Ensure max_distance is float32 for the kernel
    max_dist_float32 = float32(max_distance)
    bfs_eachToEach_kernel[blocks_per_grid, threads_per_block](
        d_array, max_dist_float32, d_result
    )

    result = d_result.copy_to_host()
    return result


### cpu kernel ###


@jit(nopython=True)
def bfs_eachToEach_cpu_single(array: np.ndarray, max_distance: float32, x: int, y: int):
    """
    CPU function for Breadth-First Search (BFS) from each point to each in a given maximum euclidian distance on a 2D array with obstacles.
    The result is the number of visited pixels for each point.
    The algorithm walks the grid in manhatten distance.
    This function is executed on the CPU.

    Args:
        array (numpy.ndarray): The input 2D array with obstacles.
        max_distance (float): The maximum distance to travel.
        x (int): The x-coordinate of the starting point.
        y (int): The y-coordinate of the starting point.

    Returns:
        visited (int): The number of visited pixels for the starting point.
    """
    rows, cols = array.shape
    # After inversion in wrapper: 0 = free space (walkable), 1 = obstacles (not walkable)
    if array[x, y] == 1:
        return 0

    halfx, halfy = (int(256 / 2), int(256 / 2))
    max_size = rows * cols

    visited = np.zeros((rows, cols), dtype=np.int32)
    queue = np.zeros((max_size, 3), dtype=np.int32)
    queue_start, queue_end = 0, 1
    queue[0, 0] = x
    queue[0, 1] = y
    queue[0, 2] = 0  # Initial distance is 0
    visited[halfx, halfy] = 1  # Center of the local array
    count = 1

    directions = np.array(
        [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)],
        dtype=np.int32,
    )

    while queue_start < queue_end and queue_start < max_size:
        cx, cy, current_distance = queue[queue_start]
        queue_start += 1

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                local_x, local_y = nx - x + halfx, ny - y + halfy
                if 0 <= local_x < rows and 0 <= local_y < cols:
                    # Check if cell is walkable (0 = free space, 1 = obstacle)
                    if visited[local_x, local_y] == 0 and array[nx, ny] == 0:

                        if dx != 0 and dy != 0:
                            new_distance = current_distance + 1.414
                        else:
                            new_distance = current_distance + 1

                        if new_distance <= max_distance:
                            visited[local_x, local_y] = 1
                            count += 1
                            if queue_end < max_size:
                                queue[queue_end, 0] = nx
                                queue[queue_end, 1] = ny
                                queue[queue_end, 2] = new_distance
                                queue_end += 1
                        else:
                            queue_start = queue_end  # Stop BFS
                            break

    return count


@jit(nopython=True, parallel=True)
def bfs_cpu(array: np.ndarray, max_distance: float32):
    """
    CPU function for Breadth-First Search (BFS) from each point to each in a given maximum euclidian distance on a 2D array with obstacles.
    The result is the number of visited pixels for each point.
    The algorithm walks the grid in manhatten distance.
    This function is executed on the CPU.

    Args:
        array (numpy.ndarray): The input 2D array with obstacles.
        max_distance (float): The maximum distance to travel.

    Returns:
        numpy.ndarray: The output 2D array with the number of visited pixels for each point.
    """
    rows, cols = array.shape
    result = np.zeros_like(array, dtype=np.int32)

    for x in prange(rows):
        for y in prange(cols):
            result[x, y] = bfs_eachToEach_cpu_single(array, max_distance, x, y)

    return result

