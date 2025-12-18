import numpy as np
from numba import cuda, jit, prange, int32, float32
import math
from typing import Tuple

from .helper.Helperfunctions import * 

### cuda kernel ###


@cuda.jit(device=True)
def bresenham_ray_cuda(
    x0: int32, y0: int32, x1: int32, y1: int32,
    stop_array: np.ndarray, max_distance: float32, shape: tuple,
) -> tuple[int32, int32]:
    """Bresenham's line algorithm for raycasting with early termination."""
    SQRT2 = float32(1.4142135623730951)  # sqrt(2)
    shape_w, shape_h = shape[1], shape[0]
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, x, y = dx - dy, x0, y0
    distance, last_x, last_y = float32(0.0), x0, y0

    while distance <= max_distance:
        if 0 <= x < shape_w and 0 <= y < shape_h:
            if stop_array[y, x] != 0:
                break
            last_x, last_y = x, y
            if x == x1 and y == y1:
                break
        elif x == x1 and y == y1:
            break
        
        e2 = 2 * err
        moved_x, moved_y = False, False
        if e2 > -dy:
            err -= dy
            x += sx
            moved_x = True
        if e2 < dx:
            err += dx
            y += sy
            moved_y = True
        
        if moved_x and moved_y:
            distance += SQRT2
        elif moved_x or moved_y:
            distance += float32(1.0)

    return last_x, last_y


@cuda.jit(device=True)
def point_in_polygon(px: int32, py: int32, polygon: np.ndarray, num_vertices: int32) -> bool:
    """Point-in-polygon test using ray casting algorithm."""
    inside = False
    j = num_vertices - 1
    
    for i in range(num_vertices):
        xi, yi = polygon[i, 0], polygon[i, 1]
        xj, yj = polygon[j, 0], polygon[j, 1]
        
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside


@cuda.jit
def compute_isovist_polygon_kernel(
    obstacle_array: np.ndarray,
    start_positions: np.ndarray,
    polygon_vertices: np.ndarray,
    polygon_bounds: np.ndarray,
    max_distance: float32,
    num_rays: int32,
    iteration: int32,
    result_array: np.ndarray,
) -> None:
    """Compute isovist polygons: cast rays, store vertices, and compute bounding boxes."""
    idx = cuda.grid(1)
    if idx >= start_positions.shape[0]:
        return
    
    start_x, start_y = start_positions[idx, 0], start_positions[idx, 1]
    width, height = obstacle_array.shape[1], obstacle_array.shape[0]
    
    if start_x < 0 or start_x >= width or start_y < 0 or start_y >= height:
        return
    
    # Mark start position if not already marked
    if result_array[start_y, start_x] == 0:
        result_array[start_y, start_x] = iteration
    
    angle_step = float32(2.0 * math.pi / num_rays)
    min_x = max_x = start_x
    min_y = max_y = start_y
    
    for i in range(num_rays):
        angle = angle_step * i
        end_x = int32(start_x + max_distance * math.cos(angle))
        end_y = int32(start_y + max_distance * math.sin(angle))
        
        hit_x, hit_y = bresenham_ray_cuda(
            int32(start_x), int32(start_y), end_x, end_y,
            obstacle_array, float32(max_distance), obstacle_array.shape
        )
        
        vertex_idx = idx * num_rays + i
        if vertex_idx < polygon_vertices.shape[0]:
            polygon_vertices[vertex_idx, 0] = idx
            polygon_vertices[vertex_idx, 1] = hit_x
            polygon_vertices[vertex_idx, 2] = hit_y
        
        if hit_x < min_x:
            min_x = hit_x
        elif hit_x > max_x:
            max_x = hit_x
        if hit_y < min_y:
            min_y = hit_y
        elif hit_y > max_y:
            max_y = hit_y
    
    if idx < polygon_bounds.shape[0]:
        polygon_bounds[idx, 0] = idx
        polygon_bounds[idx, 1] = min_x
        polygon_bounds[idx, 2] = min_y
        polygon_bounds[idx, 3] = max_x
        polygon_bounds[idx, 4] = max_y


@cuda.jit
def fill_isovist_polygon_kernel(
    obstacle_array: np.ndarray,
    start_positions: np.ndarray,
    polygon_vertices: np.ndarray,
    polygon_bounds: np.ndarray,
    result_array: np.ndarray,
    num_rays: int32,
    iteration: int32,
) -> None:
    """Fill isovist polygons using point-in-polygon test, only checking pixels within bounding boxes."""
    x, y = cuda.grid(2)
    width, height = obstacle_array.shape[1], obstacle_array.shape[0]
    
    if x >= width or y >= height or result_array[y, x] != 0 or obstacle_array[y, x] != 0:
        return
    
    num_starts = start_positions.shape[0]
    polygon = cuda.local.array((360, 2), dtype=int32)
    
    for idx in range(num_starts):
        start_x, start_y = start_positions[idx, 0], start_positions[idx, 1]
        
        if (start_x < 0 or start_x >= width or start_y < 0 or start_y >= height or
            result_array[start_y, start_x] != iteration):
            continue
        
        # Bounding box check
        if idx < polygon_bounds.shape[0]:
            if (x < polygon_bounds[idx, 1] or x > polygon_bounds[idx, 3] or
                y < polygon_bounds[idx, 2] or y > polygon_bounds[idx, 4]):
                continue
        
        # Collect vertices
        vertex_count = 0
        for i in range(num_rays):
            vertex_idx = idx * num_rays + i
            if vertex_idx < polygon_vertices.shape[0] and polygon_vertices[vertex_idx, 0] == idx:
                polygon[vertex_count, 0] = polygon_vertices[vertex_idx, 1]
                polygon[vertex_count, 1] = polygon_vertices[vertex_idx, 2]
                vertex_count += 1
        
        if vertex_count > 0 and point_in_polygon(int32(x), int32(y), polygon, vertex_count):
            result_array[y, x] = iteration
            return


@cuda.jit
def find_border_pixels_kernel(
    result_array: np.ndarray,
    obstacle_array: np.ndarray,
    new_start_positions: np.ndarray,
    counter: np.ndarray,
) -> None:
    """Find border pixels (visible pixels with unvisited neighbors)."""
    x, y = cuda.grid(2)
    width, height = result_array.shape[1], result_array.shape[0]
    
    if x >= width or y >= height or result_array[y, x] == 0:
        return
    
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            
            if (0 <= nx < width and 0 <= ny < height and
                result_array[ny, nx] == 0 and obstacle_array[ny, nx] == 0):
                idx = cuda.atomic.add(counter, 0, 1)
                if idx < new_start_positions.shape[0]:
                    new_start_positions[idx, 0] = nx
                    new_start_positions[idx, 1] = ny
                return


def gpu_iterative_isovist_raycast(
    obstacle_array: np.ndarray,
    start_positions: np.ndarray,
    max_iterations: int,
    num_rays: int = 360,
    threads_per_block=(16, 16),
) -> np.ndarray:
    """Iterative isovist-based raycasting: casts rays to form polygons, fills them, expands frontier."""
    result_array = np.zeros_like(obstacle_array, dtype=np.int32)
    d_obstacle_array = cuda.to_device(obstacle_array)
    d_result_array = cuda.to_device(result_array)
    
    if obstacle_array.size > 1000000 and threads_per_block == (16, 16):
        threads_per_block = (32, 32)
    
    blocks_per_grid_2d = (
        (obstacle_array.shape[1] + threads_per_block[0] - 1) // threads_per_block[0],
        (obstacle_array.shape[0] + threads_per_block[1] - 1) // threads_per_block[1],
    )
    
    max_distance = float32(np.sqrt(obstacle_array.shape[0] ** 2 + obstacle_array.shape[1] ** 2))
    height, width = obstacle_array.shape
    estimated_border_size = max(min(2 * (height + width) * 4, obstacle_array.size // 4), 1000)
    
    d_new_start_positions = cuda.device_array((estimated_border_size, 2), dtype=np.int32)
    d_counter = cuda.to_device(np.array([0], dtype=np.int32))
    start_positions = np.asarray(start_positions, dtype=np.int32)
    d_start_positions = cuda.to_device(start_positions)
    d_polygon_vertices = cuda.device_array((estimated_border_size * num_rays, 3), dtype=np.int32)
    d_polygon_bounds = cuda.device_array((estimated_border_size, 5), dtype=np.int32)

    for iteration in range(1, max_iterations + 1):
        blocks_per_grid_1d = ((d_start_positions.shape[0] + 255) // 256,)
        compute_isovist_polygon_kernel[blocks_per_grid_1d, 256](
            d_obstacle_array, d_start_positions, d_polygon_vertices, d_polygon_bounds,
            max_distance, int32(num_rays), int32(iteration), d_result_array
        )
        cuda.synchronize()
        
        fill_isovist_polygon_kernel[blocks_per_grid_2d, threads_per_block](
            d_obstacle_array, d_start_positions, d_polygon_vertices, d_polygon_bounds,
            d_result_array, int32(num_rays), int32(iteration)
        )
        cuda.synchronize()
        
        d_counter[0] = 0
        find_border_pixels_kernel[blocks_per_grid_2d, threads_per_block](
            d_result_array, d_obstacle_array, d_new_start_positions, d_counter
        )
        cuda.synchronize()
        
        new_start_count = min(d_counter.copy_to_host()[0], estimated_border_size)
        if new_start_count == 0:
            break
        
        d_start_positions = cuda.to_device(d_new_start_positions[:new_start_count].copy_to_host())

    return d_result_array.copy_to_host()


### cpu kernel ###


@jit(nopython=True)
def bresenham_ray_cpu(
    x0: int32, y0: int32, x1: int32, y1: int32,
    stop_array: np.ndarray, max_distance: float32, shape: tuple,
) -> Tuple[int32, int32]:
    """Bresenham's line algorithm for raycasting with early termination (CPU)."""
    SQRT2 = float32(1.4142135623730951)  # sqrt(2)
    shape_w, shape_h = int32(shape[1]), int32(shape[0])
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx, sy = (int32(1) if x0 < x1 else int32(-1)), (int32(1) if y0 < y1 else int32(-1))
    err, x, y = dx - dy, x0, y0
    distance, last_x, last_y = float32(0.0), x0, y0

    while distance <= max_distance:
        if int32(0) <= x < shape_w and int32(0) <= y < shape_h:
            if stop_array[y, x] != 0:
                break
            last_x, last_y = x, y
            if x == x1 and y == y1:
                break
        elif x == x1 and y == y1:
            break
        
        e2 = 2 * err
        moved_x, moved_y = False, False
        if e2 > -dy:
            err -= dy
            x += sx
            moved_x = True
        if e2 < dx:
            err += dx
            y += sy
            moved_y = True
        
        if moved_x and moved_y:
            distance += SQRT2
        elif moved_x or moved_y:
            distance += float32(1.0)

    return last_x, last_y


@jit(nopython=True)
def point_in_polygon_cpu(px: int32, py: int32, polygon: np.ndarray, num_vertices: int32) -> bool:
    """Point-in-polygon test using ray casting algorithm (CPU)."""
    inside = False
    j = num_vertices - 1
    
    for i in range(num_vertices):
        xi, yi = polygon[i, 0], polygon[i, 1]
        xj, yj = polygon[j, 0], polygon[j, 1]
        
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside


@jit(nopython=True)
def compute_isovist_polygon_cpu(
    obstacle_array: np.ndarray,
    start_positions: np.ndarray,
    polygon_vertices: np.ndarray,
    polygon_bounds: np.ndarray,
    max_distance: float32,
    num_rays: int32,
    iteration: int32,
    result_array: np.ndarray,
) -> None:
    """Compute isovist polygons: cast rays, store vertices, and compute bounding boxes (CPU)."""
    for idx in range(start_positions.shape[0]):
        start_x, start_y = start_positions[idx, 0], start_positions[idx, 1]
        width, height = obstacle_array.shape[1], obstacle_array.shape[0]
        
        if start_x < 0 or start_x >= width or start_y < 0 or start_y >= height:
            continue
        
        if result_array[start_y, start_x] == 0:
            result_array[start_y, start_x] = iteration
        
        angle_step = float32(2.0 * math.pi / num_rays)
        min_x = max_x = start_x
        min_y = max_y = start_y
        
        for i in range(num_rays):
            angle = angle_step * i
            end_x = int32(start_x + max_distance * math.cos(angle))
            end_y = int32(start_y + max_distance * math.sin(angle))
            
            hit_x, hit_y = bresenham_ray_cpu(
                int32(start_x), int32(start_y), end_x, end_y,
                obstacle_array, float32(max_distance), obstacle_array.shape
            )
            
            vertex_idx = idx * num_rays + i
            if vertex_idx < polygon_vertices.shape[0]:
                polygon_vertices[vertex_idx, 0] = idx
                polygon_vertices[vertex_idx, 1] = hit_x
                polygon_vertices[vertex_idx, 2] = hit_y
            
            if hit_x < min_x:
                min_x = hit_x
            elif hit_x > max_x:
                max_x = hit_x
            if hit_y < min_y:
                min_y = hit_y
            elif hit_y > max_y:
                max_y = hit_y
        
        if idx < polygon_bounds.shape[0]:
            polygon_bounds[idx, 0] = idx
            polygon_bounds[idx, 1] = min_x
            polygon_bounds[idx, 2] = min_y
            polygon_bounds[idx, 3] = max_x
            polygon_bounds[idx, 4] = max_y


@jit(nopython=True, parallel=True)
def fill_isovist_polygon_cpu(
    obstacle_array: np.ndarray,
    start_positions: np.ndarray,
    polygon_vertices: np.ndarray,
    polygon_bounds: np.ndarray,
    result_array: np.ndarray,
    num_rays: int32,
    iteration: int32,
) -> None:
    """Fill isovist polygons using point-in-polygon test, only checking pixels within bounding boxes (CPU)."""
    width, height = obstacle_array.shape[1], obstacle_array.shape[0]
    num_starts = start_positions.shape[0]
    
    for y in prange(height):
        for x in range(width):
            if result_array[y, x] != 0 or obstacle_array[y, x] != 0:
                continue
            
            for idx in range(num_starts):
                start_x, start_y = start_positions[idx, 0], start_positions[idx, 1]
                
                if (start_x < 0 or start_x >= width or start_y < 0 or start_y >= height or
                    result_array[start_y, start_x] != iteration):
                    continue
                
                if idx < polygon_bounds.shape[0]:
                    if (x < polygon_bounds[idx, 1] or x > polygon_bounds[idx, 3] or
                        y < polygon_bounds[idx, 2] or y > polygon_bounds[idx, 4]):
                        continue
                
                vertex_count = 0
                polygon = np.empty((num_rays, 2), dtype=np.int32)
                
                for i in range(num_rays):
                    vertex_idx = idx * num_rays + i
                    if vertex_idx < polygon_vertices.shape[0] and polygon_vertices[vertex_idx, 0] == idx:
                        polygon[vertex_count, 0] = polygon_vertices[vertex_idx, 1]
                        polygon[vertex_count, 1] = polygon_vertices[vertex_idx, 2]
                        vertex_count += 1
                
                if vertex_count > 0 and point_in_polygon_cpu(int32(x), int32(y), polygon, vertex_count):
                    result_array[y, x] = iteration
                    break


@jit(nopython=True)
def find_border_pixels_cpu(
    result_array: np.ndarray, obstacle_array: np.ndarray
) -> np.ndarray:
    """Find border pixels (visible pixels with unvisited neighbors) (CPU)."""
    height, width = result_array.shape
    new_start_positions = np.empty((height * width, 2), dtype=np.int32)
    counter = 0

    for y in range(height):
        for x in range(width):
            if result_array[y, x] == 0:
                continue
            
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    
                    if (0 <= nx < width and 0 <= ny < height and
                        result_array[ny, nx] == 0 and obstacle_array[ny, nx] == 0):
                        new_start_positions[counter, 0] = nx
                        new_start_positions[counter, 1] = ny
                        counter += 1
                        break
                if (counter > 0 and new_start_positions[counter - 1, 0] == nx and
                    new_start_positions[counter - 1, 1] == ny):
                    break

    return new_start_positions[:counter]


def cpu_iterative_isovist_raycast(
    obstacle_array: np.ndarray,
    start_positions: np.ndarray,
    max_iterations: int,
    num_rays: int = 360,
) -> np.ndarray:
    """Iterative isovist-based raycasting on CPU: casts rays to form polygons, fills them, expands frontier."""
    result_array = np.zeros_like(obstacle_array, dtype=np.int32)
    max_distance = float32(np.sqrt(obstacle_array.shape[0] ** 2 + obstacle_array.shape[1] ** 2))
    height, width = obstacle_array.shape
    estimated_border_size = max(min(2 * (height + width) * 4, obstacle_array.size // 4), 1000)
    
    start_positions = np.asarray(start_positions, dtype=np.int32)
    
    for iteration in range(1, max_iterations + 1):
        polygon_vertices = np.zeros((estimated_border_size * num_rays, 3), dtype=np.int32)
        polygon_bounds = np.zeros((estimated_border_size, 5), dtype=np.int32)
        
        compute_isovist_polygon_cpu(
            obstacle_array, start_positions, polygon_vertices, polygon_bounds,
            max_distance, int32(num_rays), int32(iteration), result_array
        )
        
        fill_isovist_polygon_cpu(
            obstacle_array, start_positions, polygon_vertices, polygon_bounds,
            result_array, int32(num_rays), int32(iteration)
        )
        
        new_start_positions = find_border_pixels_cpu(result_array, obstacle_array)
        
        if len(new_start_positions) == 0:
            break
        
        start_positions = new_start_positions

    return result_array

