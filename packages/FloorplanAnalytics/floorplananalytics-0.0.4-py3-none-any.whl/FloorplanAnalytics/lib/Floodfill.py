import numpy as np
import numba
from numba import cuda, prange, int32, float32

from typing import Tuple

from .helper.Helperfunctions import * 

### cuda kernel ###

@cuda.jit
def flood_fill_kernel_cuda(image: np.ndarray, mask: np.ndarray, old_color: np.ndarray, new_color: np.ndarray, tolerance: int32, changes: np.ndarray) -> None:
  """
  CUDA kernel for flood fill algorithm.
  This function is executed on the GPU.

  Parameters:
    image (np.ndarray): 3D NumPy array representing the image.
    mask (np.ndarray): 2D NumPy array representing the mask.
    old_color (np.ndarray): 1D NumPy array representing the old color.
    new_color (np.ndarray): 1D NumPy array representing the new color.
    tolerance (int32): Integer representing the tolerance for color difference.
    changes (np.ndarray): 1D NumPy array representing the changes flag.

  Returns:
    None (None):
    The function modifies the image, mask and change array in place.
  """
  x, y = cuda.grid(2)
  if x < image.shape[0] and y < image.shape[1]:
      if mask[x, y] == 2:
          mask[x, y] = 1
          changes[0] = 1
          for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
              nx, ny = x + dx, y + dy
              if 0 <= nx < image.shape[0] and 0 <= ny < image.shape[1] and mask[nx, ny] == 0:
                  is_within_tolerance = True
                  for c in range(image.shape[2]):
                      if abs(int(image[nx, ny, c]) - int(old_color[c])) > tolerance:
                          is_within_tolerance = False
                          break
                  if is_within_tolerance:
                      for c in range(image.shape[2]):
                          image[nx, ny, c] = new_color[c]
                      mask[nx, ny] = 2

def flood_fill_cuda(image: np.ndarray, start_coords: Tuple[int, int], new_color: np.ndarray, tolerance: int32, threads_per_block: Tuple[int,int] = (32, 32)) -> Tuple[np.ndarray, np.ndarray]:
  """
  Main function to perform flood fill.
  This function is executed on the CPU.

  Parameters:
    image (np.ndarray): 3D NumPy array representing the image.
    start_coords (Tuple[int, int]): Tuple representing the starting coordinates (x, y).
    new_color (np.ndarray): 1D NumPy array representing the new color.
    tolerance (int32): Integer representing the tolerance for color difference.
    threads_per_block (Tuple[int,int]): A tuple representing the number of threads per block in the grid.

  Returns:
    results (Tuple[np.ndarray, np.ndarray]): Tuple of modified 3D NumPy array representing the image and 2D NumPy array representing the mask.
  """
  start_x, start_y = start_coords
  old_color = image[start_x, start_y].copy()

  if np.array_equal(old_color, new_color):
    return image, np.zeros(image.shape[:2], dtype=np.int32)

  mask = np.zeros(image.shape[:2], dtype=np.int32)
  mask[start_x, start_y] = 2

  d_image = cuda.to_device(image)
  d_mask = cuda.to_device(mask)
  d_changes = cuda.to_device(np.array([1], dtype=np.int32))

  threads_per_block = (32, 32)
  blocks_per_grid = (
      (image.shape[0] + threads_per_block[0] - 1) // threads_per_block[0],
      (image.shape[1] + threads_per_block[1] - 1) // threads_per_block[1]
  )

  max_iterations = image.shape[0] * image.shape[1]
  for _ in range(max_iterations):
      d_changes[0] = 0
      flood_fill_kernel_cuda[blocks_per_grid, threads_per_block](
          d_image, d_mask, old_color, new_color, tolerance, d_changes
      )
      if d_changes.copy_to_host()[0] == 0:
          break

  return d_image.copy_to_host(), d_mask.copy_to_host()


### cpu kernel ###

@numba.njit(parallel=True)
def flood_fill_kernel_cpu(image: np.ndarray, mask: np.ndarray, old_color: np.ndarray, new_color: np.ndarray, tolerance: int32) -> np.ndarray:
  """
  CPU kernel for flood fill algorithm.
  This function is executed on the CPU.

  Parameters:
    image (np.ndarray): 3D NumPy array representing the image.
    mask (np.ndarray): 2D NumPy array representing the mask.
    old_color (np.ndarray): 1D NumPy array representing the old color.
    new_color (np.ndarray): 13D NumPy array representing the new color.
    tolerance (int32): Integer representing the tolerance for color difference

  Returns:
    changes (np.ndarray): 1D NumPy array representing the changes flag.
  """
  height, width = image.shape[:2]
  changes = np.zeros(1, dtype=np.int32)
  for x in prange(height):
      for y in prange(width):
          if mask[x, y] == 2:
              mask[x, y] = 1
              changes[0] = 1
              for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                  nx, ny = x + dx, y + dy
                  if 0 <= nx < height and 0 <= ny < width and mask[nx, ny] == 0:
                      is_within_tolerance = True
                      for c in range(image.shape[2]):
                          if abs(int(image[nx, ny, c]) - int(old_color[c])) > tolerance:
                              is_within_tolerance = False
                              break
                      if is_within_tolerance:
                          for c in range(image.shape[2]):
                              image[nx, ny, c] = new_color[c]
                          mask[nx, ny] = 2
  return changes[0]

@numba.njit
def flood_fill_cpu(image: np.ndarray, start_coords: Tuple[int, int], new_color: np.ndarray, tolerance: int32) -> Tuple[np.ndarray, np.ndarray]:
  """
  Main function to perform flood fill.
  This function is executed on the CPU.

  Parameters:
    image (np.ndarray): 3D NumPy array representing the image.
    start_coords (np.ndarray): Tuple representing the starting coordinates (x, y).
    new_color (np.ndarray): 1D NumPy array representing the new color.
    tolerance (int32): Integer representing the tolerance for color difference

  Returns:
    results (Tuple[np.ndarray, np.ndarray]): Tuple of modified 3D NumPy array representing the image and 2D NumPy array representing the mask.

  """
  start_x, start_y = start_coords
  old_color = image[start_x, start_y].copy()

  if np.array_equal(old_color, new_color):
      return image, np.zeros(image.shape[:2], dtype=np.int32)

  mask = np.zeros(image.shape[:2], dtype=np.int32)
  mask[start_x, start_y] = 2

  max_iterations = image.shape[0] * image.shape[1]
  for _ in range(max_iterations):
      changes = flood_fill_kernel_cpu(image, mask, old_color, new_color, tolerance)
      if changes == 0:
          break

  return image, mask