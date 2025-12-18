"""
Geodesic Range computation with support for unlimited distance and large images.

Optimized algorithms:
- Unlimited distance: scipy Connected Components (O(N)) - fastest
- Small distances (<=128): Original local-memory kernel - fastest for small distances
- Large distances (>128): Global memory kernel - scalable for large distances
"""

import numpy as np
import math
from numba import cuda, int32, float32, jit, prange
from typing import Tuple, Optional

try:
    from scipy import ndimage
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


### CUDA kernels ###


@cuda.jit
def bfs_global_memory_kernel(
    array: np.ndarray, max_distance: float32, result: np.ndarray,
    visited_pool: np.ndarray, queue_pool_x: np.ndarray, queue_pool_y: np.ndarray,
    queue_pool_dist: np.ndarray, visited_size: int32, queue_size: int32,
    pixel_indices_x: np.ndarray, pixel_indices_y: np.ndarray, num_pixels: int32
) -> None:
    """Fast BFS kernel using global memory. Each thread processes one pixel independently.
    
    Uses 8-connected neighbor traversal (same as bfs_eachToEach_kernel):
    - Cardinal directions (up, down, left, right): distance = 1.0
    - Diagonal directions: distance = 1.4142135623730951 (√2)
    
    Neighbor pattern:
    [[1, 1, 1],
     [1, 0, 1],
     [1, 1, 1]]
    """
    thread_idx = cuda.grid(1)
    if thread_idx >= num_pixels:
        return
    
    start_x = int(pixel_indices_x[thread_idx])
    start_y = int(pixel_indices_y[thread_idx])
    rows = int(array.shape[0])
    cols = int(array.shape[1])
    
    if array[start_x, start_y] == 1:
        result[start_x, start_y] = 0
        return
    
    vs = int(visited_size)
    qs = int(queue_size)
    visited_offset = int(thread_idx) * vs * vs
    queue_offset = int(thread_idx) * qs
    
    half_size = vs // 2
    max_radius = int(max_distance) + 2
    min_idx = max(0, half_size - max_radius)
    max_idx_val = min(vs, half_size + max_radius + 1)
    
    for i in range(min_idx, max_idx_val):
        row_offset = visited_offset + i * vs
        for j in range(min_idx, max_idx_val):
            visited_pool[row_offset + j] = 0
    
    queue_pool_x[queue_offset] = start_x
    queue_pool_y[queue_offset] = start_y
    queue_pool_dist[queue_offset] = float32(0.0)
    visited_pool[visited_offset + half_size * vs + half_size] = 1
    
    queue_start, queue_end, count = 0, 1, 1
    
    while queue_start < queue_end:
        q_idx = queue_offset + queue_start
        cx = int(queue_pool_x[q_idx])
        cy = int(queue_pool_y[q_idx])
        current_dist = queue_pool_dist[q_idx]
        queue_start += 1
        
        if current_dist >= max_distance:
            continue
        
        for di in range(-1, 2):
            for dj in range(-1, 2):
                if di == 0 and dj == 0:
                    continue
                
                nx, ny = cx + di, cy + dj
                if nx < 0 or nx >= rows or ny < 0 or ny >= cols:
                    continue
                if array[nx, ny] == 1:
                    continue
                
                local_x = nx - start_x + half_size
                local_y = ny - start_y + half_size
                if local_x < 0 or local_x >= vs or local_y < 0 or local_y >= vs:
                    continue
                
                visited_idx = visited_offset + local_x * vs + local_y
                if visited_pool[visited_idx] != 0:
                    continue
                
                step = float32(1.4142135623730951) if (di != 0 and dj != 0) else float32(1.0)
                new_dist = current_dist + step
                
                if new_dist > max_distance:
                    continue
                
                visited_pool[visited_idx] = 1
                count += 1
                
                if queue_end < qs:
                    new_q_idx = queue_offset + queue_end
                    queue_pool_x[new_q_idx] = nx
                    queue_pool_y[new_q_idx] = ny
                    queue_pool_dist[new_q_idx] = new_dist
                    queue_end += 1
    
    result[start_x, start_y] = count


@cuda.jit
def bfs_sum_distance_kernel(
    array: np.ndarray, max_distance: float32, result: np.ndarray,
    visited_pool: np.ndarray, queue_pool_x: np.ndarray, queue_pool_y: np.ndarray,
    queue_pool_dist: np.ndarray, visited_size: int32, queue_size: int32,
    pixel_indices_x: np.ndarray, pixel_indices_y: np.ndarray, num_pixels: int32
) -> None:
    """BFS kernel that sums distances instead of counting."""
    thread_idx = cuda.grid(1)
    if thread_idx >= num_pixels:
        return
    
    start_x = int(pixel_indices_x[thread_idx])
    start_y = int(pixel_indices_y[thread_idx])
    rows = int(array.shape[0])
    cols = int(array.shape[1])
    
    if array[start_x, start_y] == 1:
        result[start_x, start_y] = float32(0.0)
        return
    
    vs = int(visited_size)
    qs = int(queue_size)
    visited_offset = int(thread_idx) * vs * vs
    queue_offset = int(thread_idx) * qs
    
    half_size = vs // 2
    max_radius = int(max_distance) + 2
    min_idx = max(0, half_size - max_radius)
    max_idx_val = min(vs, half_size + max_radius + 1)
    
    for i in range(min_idx, max_idx_val):
        row_offset = visited_offset + i * vs
        for j in range(min_idx, max_idx_val):
            visited_pool[row_offset + j] = 0
    
    queue_pool_x[queue_offset] = start_x
    queue_pool_y[queue_offset] = start_y
    queue_pool_dist[queue_offset] = float32(0.0)
    visited_pool[visited_offset + half_size * vs + half_size] = 1
    
    queue_start, queue_end = 0, 1
    total_distance = float32(0.0)
    
    while queue_start < queue_end:
        q_idx = queue_offset + queue_start
        cx = int(queue_pool_x[q_idx])
        cy = int(queue_pool_y[q_idx])
        current_dist = queue_pool_dist[q_idx]
        queue_start += 1
        
        if current_dist >= max_distance:
            continue
        
        for di in range(-1, 2):
            for dj in range(-1, 2):
                if di == 0 and dj == 0:
                    continue
                
                nx, ny = cx + di, cy + dj
                if nx < 0 or nx >= rows or ny < 0 or ny >= cols:
                    continue
                if array[nx, ny] == 1:
                    continue
                
                local_x = nx - start_x + half_size
                local_y = ny - start_y + half_size
                if local_x < 0 or local_x >= vs or local_y < 0 or local_y >= vs:
                    continue
                
                visited_idx = visited_offset + local_x * vs + local_y
                if visited_pool[visited_idx] != 0:
                    continue
                
                step = float32(1.4142135623730951) if (di != 0 and dj != 0) else float32(1.0)
                new_dist = current_dist + step
                
                if new_dist > max_distance:
                    continue
                
                visited_pool[visited_idx] = 1
                total_distance += new_dist
                
                if queue_end < qs:
                    new_q_idx = queue_offset + queue_end
                    queue_pool_x[new_q_idx] = nx
                    queue_pool_y[new_q_idx] = ny
                    queue_pool_dist[new_q_idx] = new_dist
                    queue_end += 1
    
    result[start_x, start_y] = total_distance


def run_bfs_global_memory_cuda(
    array: np.ndarray, max_distance: float, batch_size: int = 4096, threads_per_block: int = 256
) -> np.ndarray:
    """Fast BFS using global memory pooling for large distances."""
    rows, cols = array.shape
    result = np.zeros((rows, cols), dtype=np.int32)
    
    walkable_mask = array == 0
    walkable_coords = np.argwhere(walkable_mask)
    num_walkable = len(walkable_coords)
    
    if num_walkable == 0:
        return result
    
    # Calculate memory requirements
    visited_size = min(1024, max(64, int(max_distance * 2) + 4))
    queue_size = min(65536, max(1024, visited_size * visited_size // 2))
    bytes_per_thread = visited_size * visited_size + queue_size * 12
    max_memory = 1 * 1024 * 1024 * 1024  # 1GB limit
    max_batch = max(1, max_memory // bytes_per_thread)
    actual_batch_size = min(batch_size, max_batch, num_walkable, 1024)
    
    if actual_batch_size == 0:
        actual_batch_size = 1
    
    try:
        # Allocate device arrays once and reuse
        d_array = cuda.to_device(array.astype(np.int32))
        d_result = cuda.to_device(result)
        d_visited_pool = cuda.device_array(actual_batch_size * visited_size * visited_size, dtype=np.int8)
        d_queue_x = cuda.device_array(actual_batch_size * queue_size, dtype=np.int32)
        d_queue_y = cuda.device_array(actual_batch_size * queue_size, dtype=np.int32)
        d_queue_dist = cuda.device_array(actual_batch_size * queue_size, dtype=np.float32)
    except Exception:
        from .GeodesicRange import bfs_cpu
        return bfs_cpu(array, float32(max_distance))
    
    num_batches = (num_walkable + actual_batch_size - 1) // actual_batch_size
    max_dist_float32 = np.float32(max_distance)
    
    for batch_idx in range(num_batches):
        start_idx = batch_idx * actual_batch_size
        end_idx = min(start_idx + actual_batch_size, num_walkable)
        if start_idx >= num_walkable:
            break
        
        batch_coords = walkable_coords[start_idx:end_idx]
        current_batch_size = len(batch_coords)
        if current_batch_size == 0:
            continue
        
        try:
            # Reuse device arrays for pixel indices (allocate once per batch)
            d_pixel_x = cuda.to_device(batch_coords[:, 0].astype(np.int32))
            d_pixel_y = cuda.to_device(batch_coords[:, 1].astype(np.int32))
            blocks = max(1, (current_batch_size + threads_per_block - 1) // threads_per_block)
            
            bfs_global_memory_kernel[blocks, threads_per_block](
                d_array, max_dist_float32, d_result, d_visited_pool,
                d_queue_x, d_queue_y, d_queue_dist, np.int32(visited_size),
                np.int32(queue_size), d_pixel_x, d_pixel_y, np.int32(current_batch_size)
            )
            cuda.synchronize()
        except Exception:
            from .GeodesicRange import bfs_cpu
            return bfs_cpu(array, float32(max_distance))
    
    return d_result.copy_to_host()


def run_bfs_sum_distance_cuda(
    array: np.ndarray, max_distance: float, batch_size: int = 4096, threads_per_block: int = 256
) -> np.ndarray:
    """Fast aggregated distance using global memory pooling."""
    rows, cols = array.shape
    result = np.zeros((rows, cols), dtype=np.float32)
    
    walkable_mask = array == 0
    walkable_coords = np.argwhere(walkable_mask)
    num_walkable = len(walkable_coords)
    
    if num_walkable == 0:
        return result
    
    visited_size = min(1024, max(64, int(max_distance * 2) + 4))
    queue_size = min(65536, max(1024, visited_size * visited_size // 2))
    bytes_per_thread = visited_size * visited_size + queue_size * 12
    max_memory = 1 * 1024 * 1024 * 1024
    max_batch = max(1, max_memory // bytes_per_thread)
    actual_batch_size = min(batch_size, max_batch, num_walkable, 1024)
    
    if actual_batch_size == 0:
        actual_batch_size = 1
    
    try:
        d_array = cuda.to_device(array.astype(np.int32))
        d_result = cuda.to_device(result)
        d_visited_pool = cuda.device_array(actual_batch_size * visited_size * visited_size, dtype=np.int8)
        d_queue_x = cuda.device_array(actual_batch_size * queue_size, dtype=np.int32)
        d_queue_y = cuda.device_array(actual_batch_size * queue_size, dtype=np.int32)
        d_queue_dist = cuda.device_array(actual_batch_size * queue_size, dtype=np.float32)
    except Exception:
        return run_aggregated_distance_cpu(array, max_distance)
    
    num_batches = (num_walkable + actual_batch_size - 1) // actual_batch_size
    max_dist_float32 = np.float32(max_distance)
    
    for batch_idx in range(num_batches):
        start_idx = batch_idx * actual_batch_size
        end_idx = min(start_idx + actual_batch_size, num_walkable)
        if start_idx >= num_walkable:
            break
        
        batch_coords = walkable_coords[start_idx:end_idx]
        current_batch_size = len(batch_coords)
        if current_batch_size == 0:
            continue
        
        try:
            d_pixel_x = cuda.to_device(batch_coords[:, 0].astype(np.int32))
            d_pixel_y = cuda.to_device(batch_coords[:, 1].astype(np.int32))
            blocks = max(1, (current_batch_size + threads_per_block - 1) // threads_per_block)
            
            bfs_sum_distance_kernel[blocks, threads_per_block](
                d_array, max_dist_float32, d_result, d_visited_pool,
                d_queue_x, d_queue_y, d_queue_dist, np.int32(visited_size),
                np.int32(queue_size), d_pixel_x, d_pixel_y, np.int32(current_batch_size)
            )
            cuda.synchronize()
        except Exception:
            return run_aggregated_distance_cpu(array, max_distance)
    
    return d_result.copy_to_host()


### CPU kernels ###


@jit(nopython=True)
def bfs_sum_cpu_single(array: np.ndarray, start_x: int, start_y: int, max_distance: float) -> float:
    """Single-source BFS returning sum of distances (CPU only, for aggregated distance)."""
    rows, cols = array.shape
    if array[start_x, start_y] == 1:
        return 0.0
    
    visited = np.zeros((rows, cols), dtype=np.int32)
    visited[start_x, start_y] = 1
    queue_x = np.zeros(rows * cols, dtype=np.int32)
    queue_y = np.zeros(rows * cols, dtype=np.int32)
    queue_dist = np.zeros(rows * cols, dtype=np.float32)
    
    queue_start, queue_end = 0, 1
    queue_x[0] = start_x
    queue_y[0] = start_y
    queue_dist[0] = 0.0
    total_distance = 0.0
    
    while queue_start < queue_end:
        cx = queue_x[queue_start]
        cy = queue_y[queue_start]
        current_dist = queue_dist[queue_start]
        queue_start += 1
        
        if current_dist >= max_distance:
            continue
        
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = cx + dx, cy + dy
                if nx < 0 or nx >= rows or ny < 0 or ny >= cols:
                    continue
                if array[nx, ny] == 1 or visited[nx, ny] == 1:
                    continue
                
                step = 1.4142135623730951 if (dx != 0 and dy != 0) else 1.0
                new_dist = current_dist + step
                
                if new_dist <= max_distance:
                    visited[nx, ny] = 1
                    total_distance += new_dist
                    if queue_end < rows * cols:
                        queue_x[queue_end] = nx
                        queue_y[queue_end] = ny
                        queue_dist[queue_end] = new_dist
                        queue_end += 1
    
    return total_distance


@jit(nopython=True, parallel=True)
def run_aggregated_distance_cpu(array: np.ndarray, max_distance: float) -> np.ndarray:
    """CPU fallback for aggregated distance."""
    rows, cols = array.shape
    result = np.zeros((rows, cols), dtype=np.float32)
    for idx in prange(rows * cols):
        result[idx // cols, idx % cols] = bfs_sum_cpu_single(array, idx // cols, idx % cols, max_distance)
    return result


### Scipy connected components ###


def run_connected_components_scipy(array: np.ndarray) -> np.ndarray:
    """Fast connected components using scipy.ndimage.label."""
    walkable = array == 0
    structure = np.ones((3, 3), dtype=np.int32)
    labeled, _ = ndimage.label(walkable, structure=structure)
    component_sizes = np.bincount(labeled.ravel())
    result = component_sizes[labeled]
    result[~walkable] = 0
    return result.astype(np.int32)


### Main interfaces ###


def run_geodesic_range_unlimited(
    array: np.ndarray,
    max_distance: Optional[float] = None,
    batch_size: int = 4096,
    threads_per_block: Tuple[int, int] = (16, 16),
    use_cuda: bool = True
) -> np.ndarray:
    """Compute geodesic range (reachable pixel count) from each pixel.
    
    Algorithm selection:
    - max_distance=None: scipy Connected Components (fastest, O(N))
    - max_distance <= 128: Original local-memory kernel (fastest for small distances)
    - max_distance > 128: Global memory kernel (scalable for large distances)
    """
    input_array = array.astype(np.int32)
    
    if max_distance is None:
        if SCIPY_AVAILABLE:
            return run_connected_components_scipy(input_array)
        else:
            raise RuntimeError("scipy is required for unlimited distance computation")
    
    if cuda.is_available() and use_cuda:
        # Use original fast local-memory kernel for small distances on small images
        # Original kernel uses 256x256 visited array, so avoid for images >= 256x256
        rows, cols = input_array.shape
        if max_distance <= 128 and rows < 256 and cols < 256:
            from .GeodesicRange import run_bfs_cuda
            return run_bfs_cuda(input_array, float32(max_distance), threads_per_block)
        # Use global memory kernel for large distances or large images
        return run_bfs_global_memory_cuda(input_array, max_distance, batch_size)
    
    # CPU fallback - use existing fast CPU implementation for all distances
    from .GeodesicRange import bfs_cpu
    return bfs_cpu(input_array, float32(max_distance))


def run_geodesic_distance_aggregated(
    array: np.ndarray,
    max_distance: Optional[float] = None,
    batch_size: int = 4096,
    threads_per_block: Tuple[int, int] = (16, 16),
    use_cuda: bool = True
) -> np.ndarray:
    """Compute sum of geodesic distances from each pixel to all reachable pixels."""
    rows, cols = array.shape
    if max_distance is None:
        max_distance = math.sqrt(rows**2 + cols**2)
    
    input_array = array.astype(np.int32)
    
    if cuda.is_available() and use_cuda:
        return run_bfs_sum_distance_cuda(input_array, max_distance, batch_size)
    return run_aggregated_distance_cpu(input_array, max_distance)
