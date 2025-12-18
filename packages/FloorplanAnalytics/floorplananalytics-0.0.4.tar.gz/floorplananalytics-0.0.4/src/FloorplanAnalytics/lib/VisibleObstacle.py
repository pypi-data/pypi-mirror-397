
import numba as nb
import numpy as np
from numba import cuda, int32, int16, float32, jit, prange
import math

from typing import Tuple

from .helper.Helperfunctions import * 


### cuda kernel ###

@cuda.jit(device=True)
def bresenham_ray_cuda(x0: int32, y0: int32, x1: int32, y1: int32, stop_array: np.ndarray, max_distance: float32, shape: tuple) -> Tuple[int32, int32]:
  """
  CUDA kernel for performing bresenham's line based raycasting.
  This function is executed on the GPU.

  Args:
    x0 (int32): The starting x-coordinate.
    y0 (int32): The starting y-coordinate.
    x1 (int32): The ending x-coordinate.
    y1 (int32): The ending y-coordinate

  Returns:
    result (Tuple[int32, int32]): The hit x and y coordinates of the ray.
  """
  # Precompute constants
  SQRT2_HALF = float32(0.7071067811865476)  # math.sqrt(2) / 2
  shape_w = shape[1]
  shape_h = shape[0]
  
  dx = abs(x1 - x0)
  dy = abs(y1 - y0)
  sx = 1 if x0 < x1 else -1
  sy = 1 if y0 < y1 else -1
  err = dx - dy
  
  # Precompute distance increment values based on line direction
  # Original logic: x move adds 1 if dy <= dx else sqrt(2)/2, y move adds 1 if dx < dy else sqrt(2)/2
  dist_x_move = float32(1.0) if dy <= dx else SQRT2_HALF
  dist_y_move = float32(1.0) if dx < dy else SQRT2_HALF

  x, y = x0, y0
  distance = float32(0.0)
  last_x, last_y = x0, y0

  while distance <= max_distance:
      # Early exit if reached target
      if x == x1 and y == y1:
          break
          
      # Only check bounds and obstacle when inside bounds
      if 0 <= x < shape_w and 0 <= y < shape_h:
          if stop_array[y, x] != 0:
              break
          last_x, last_y = x, y
      
      # Bresenham step
      e2 = 2 * err
      if e2 > -dy:
          err -= dy
          x += sx
          distance += dist_x_move
      if e2 < dx:
          err += dx
          y += sy
          distance += dist_y_move

  return last_x, last_y

@cuda.jit
def raycast_hit_count_cuda(mask: np.ndarray, target_array: np.ndarray, num_rays: int32, max_distance: float32, hit_count_output: np.ndarray):
  """
  CUDA kernel for performing ray casting and hit count calculation for all pixels.
  This function is executed on the GPU.

  Args:
    mask (np.ndarray): A 2D array representing the input mask as np array where with obstacles 1 and free space as 0.
    target_array (np.ndarray): A 2D array representing the target points as np array where with points of interest 1 and free space as 0.
    num_rays (int32): The number of rays to be shot from each pixel.
    max_distance (float32): The maximum distance that the rays can travel.
    hit_count_output (np.ndarray): A 2D array to store the hit count for each pixel.

  Returns:
    None (None):
    The hit count for each pixel is stored in the hit_count_output array.
  """
  x, y = cuda.grid(2)
  if x < hit_count_output.shape[1] and y < hit_count_output.shape[0]:
      hit_count = int32(0)
      
      # Precompute angle step to avoid repeated division
      angle_step = float32(2.0 * math.pi / num_rays)

      for i in range(num_rays):
          angle = angle_step * i
          cos_angle = math.cos(angle)
          sin_angle = math.sin(angle)
          end_x = int(x + max_distance * cos_angle)
          end_y = int(y + max_distance * sin_angle)
          last_x, last_y = bresenham_ray_cuda(x, y, end_x, end_y, mask, max_distance, mask.shape)

          if target_array[last_y, last_x] != 0:
              hit_count += 1

      hit_count_output[y, x] = hit_count

def raycast_hit_count_cuda_wrapper(mask: np.ndarray, target_array: np.ndarray, num_rays: int32, max_distance: float32, threads_per_block: Tuple[int, int]=(16, 16)) -> np.ndarray:
  """
  Wrapper function for performing ray casting and hit count calculation for all pixels.
  This function is executed on the GPU.

  Args:
    stop_array (np.ndarray): A 2D array representing the input mask as np array where with obstacles 1 and free space as 0.
    target_array (np.ndarray): A 2D array representing the target points as np array where with points of interest 1 and free space as 0.
    num_rays (int32): The number of rays to be shot from each pixel.
    max_distance (float32): The maximum distance that the rays can travel.

  Returns:
    hit_count (np.ndarray):
    A 2D array representing the hit count for each pixel.
  """
  shape = mask.shape
  mask_gpu = cuda.to_device(mask)
  target_array_gpu = cuda.to_device(target_array)
  hit_count_output = cuda.to_device(np.zeros(shape, dtype=np.int32))

  blocks_per_grid = (
      (shape[1] + threads_per_block[0] - 1) // threads_per_block[0],
      (shape[0] + threads_per_block[1] - 1) // threads_per_block[1]
  )

  raycast_hit_count_cuda[blocks_per_grid, threads_per_block](
      mask_gpu, target_array_gpu, num_rays, max_distance, hit_count_output
  )

  return hit_count_output.copy_to_host()


### cpu kernel ###

@jit(nopython=True)
def bresenham_ray_cpu(x0: int32, y0: int32, x1: int32, y1: int32, stop_array: np.ndarray, max_distance: float32, shape: tuple) -> Tuple[int32, int32]:
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
def raycast_hit_count_cpu(stop_array: np.ndarray, target_array: np.ndarray, num_rays: int32, max_distance: float32) -> np.ndarray:
  """
  CPU function for performing ray casting and hit count calculation for all pixels.
  This function is executed on the CPU in parallel.

  Args:
    stop_array (np.ndarray): A 2D array representing the input mask as np array where with obstacles 1 and free space as 0.
    target_array (np.ndarray): A 2D array representing the target points as np array where with points of interest 1 and free space as 0.
    num_rays (int32): The number of rays to be shot from each pixel.
    max_distance (float32): The maximum distance that the rays can travel.

  Returns:
    result (np.ndarray):
    A 2D array representing the hit count for each pixel.
  """
  shape = stop_array.shape
  hit_count_output = np.zeros(shape, dtype=np.int32)

  for y in prange(shape[0]):
      for x in range(shape[1]):
          hit_count = 0
          for i in range(num_rays):
              angle = 2 * np.pi * i / num_rays
              end_x = int32(x + max_distance * np.cos(angle))
              end_y = int32(y + max_distance * np.sin(angle))
              last_x, last_y = bresenham_ray_cpu(x, y, end_x, end_y, stop_array, max_distance, shape)

              if target_array[int(last_y), int(last_x)] != 0:
                  hit_count += 1

          hit_count_output[y, x] = hit_count

  return hit_count_output
