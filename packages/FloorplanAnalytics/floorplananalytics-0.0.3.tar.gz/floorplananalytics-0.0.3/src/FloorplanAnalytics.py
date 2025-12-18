import numpy as np
import numba
from numba import cuda, prange, int32, float32

from typing import Tuple
from PIL import Image

from .lib.helper.Helperfunctions import *
from .lib.helper.Colorhelper import *


# eventually only expose the functions that are needed below for PyPI package
from .lib.Floodfill import *    
from .lib.GeodesicDistanceMulti import *
from .lib.GeodesicRange import *
from .lib.GeodesicRangeUnlimited import *
from .lib.RaycastDistance import *
from .lib.SignedDistance import *
from .lib.StepDepth import *
from .lib.StepDepthIsovist import *
from .lib.VisibleArea import *
from .lib.VisibleObstacle import *



def run_floodFill(
    image: np.ndarray, 
    start_coords: Tuple[int, int], 
    new_color: np.ndarray, 
    tolerance: int32, 
    use_cuda: bool=False
    ) -> Tuple[np.ndarray, np.ndarray]:
    """
        Wrapper function for flood fill algorithm.
        This function is executed on the CPU or GPU depending on the availability of CUDA.
        
        Parameters:
        image (np.ndarray): 3D NumPy array representing the image.
        start_coords (np.ndarray): Tuple representing the starting coordinates (x, y).
        new_color (np.ndarray): 1D NumPy array representing the new color.
        tolerance (int32): Integer representing the tolerance for color difference.
        use_cuda (bool): Whether to use the CUDA GPU. Default is False.
            
        Returns:
        Modified 3D NumPy array representing the image and 2D NumPy array representing the mask.
        
    """
    if not isinstance(image, np.ndarray) or image.ndim != 3:
        raise ValueError("Input must be a 3D NumPy array")

    
    if cuda.is_available() and use_cuda:
        print("CUDA is available. Using GPU implementation.")
        return flood_fill_cuda(image, start_coords, new_color, tolerance)
    else:
        print("Using CPU parallel implementation.")
        return flood_fill_cpu(image, start_coords, new_color, tolerance)


def run_geodesicDistance(
    mask: np.ndarray, 
    start_points: np.ndarray, 
    resize_for_compute:bool=False,
    max_size:int=1024,
    threads_per_block: Tuple[int, int]=(32, 32), 
    max_iterations:int=1000, 
    use_cuda:bool=True
    ) -> np.ndarray:
    """
    Perform the Breadth-First Search (BFS) algorithm on a grid with multiple start points.

    Args:
        mask (np.ndarray): The input 2D array with obstacles.
        start_points (np.ndarray): The input 2D array with start points.
        threads_per_block (Tuple[int, int], optional): A tuple representing the number of threads per block. Defaults to (32, 32).
        max_iterations (int, optional): The maximum number of iterations for the BFS algorithm. Defaults to 1000.
        use_cuda (bool, optional): Whether to use the CUDA GPU. Defaults to True.

    Returns:
        np.ndarray: The output 2D array with the geodesic distances from the start points.
    """
    original_shape = mask.shape
    
    #scale array before computation
    if resize_for_compute:
        mask = resize_array(mask, max_size, rescale_by_larger=True)
        start_points = resize_array(start_points, max_size, rescale_by_larger=True)
        # Binarize start_points after resize (resize can create fractional values)
        start_points = (start_points > 0.5).astype(np.int32)
        print(f"Resized compute array from shape {original_shape} to shape: {mask.shape}")
        
    #perform computation
    if cuda.is_available() and use_cuda:
        print("CUDA is available. Using CUDA for computation")
        result = bfs_multi_cuda(mask, start_points, threads_per_block, max_iterations)
    else:
        print("CUDA not available. Using CPU with Numba")
        result = bfs_multi_cpu_wrapper(mask, start_points, max_iterations)
    
    #rescale array after computation
    if resize_for_compute:
        # Use nearest-neighbor (order=0) to preserve boundary pixels correctly
        result = resize_array_xy(result, original_shape, order=0) 
        # Use actual zoom factor from resize operation
        zoom_factor = max(original_shape) / max(mask.shape)
        result = result * zoom_factor

    return result


def run_geodesicRange(
        array: np.ndarray,
        max_distance: float = None,
        resize_for_compute: bool = False,
        max_size: int = 1024,
        batch_size: int = 4096,
        threads_per_block: Tuple[int, int] = (16, 16),
        use_cuda: bool = True,
    ):
    """
    Compute geodesic range (reachable pixel count) from each pixel with support
    for unlimited distance and large images.
    
    This function automatically selects the optimal algorithm:
    - max_distance=None: Uses scipy Connected Components - very fast O(N)
    - max_distance <= 128: Uses original fast local-memory BFS kernel
    - max_distance > 128: Uses fast parallel global-memory BFS kernel
    
    Performance notes:
    - Unlimited distance is very fast (scipy O(N))
    - Small distances (<=128) use the original fast kernel
    - Large distances use parallel BFS with global memory pooling
    
    Args:
        array (np.ndarray): Input 2D array (0=walkable/free space, 1=obstacle).
        max_distance (float): Maximum geodesic distance. None = unlimited (all reachable pixels).
        resize_for_compute (bool): Whether to resize for computation. Default False.
        max_size (int): Maximum size for resizing. Default 1024.
        batch_size (int): Pixels per GPU batch for large distances. Default 4096.
        threads_per_block (tuple): CUDA thread block dimensions. Default (16, 16).
        use_cuda (bool): Whether to use GPU acceleration. Default True.
    
    Returns:
        np.ndarray: 2D array where each pixel contains the count of reachable pixels.
    
    Example:
        # Count all reachable pixels (unlimited distance) - VERY FAST
        result = run_geodesicRangeUnlimited(mask, max_distance=None)
        
        # Count pixels within small distance - FAST (uses original kernel)
        result = run_geodesicRangeUnlimited(mask, max_distance=100)
        
        # Count pixels within large distance - uses parallel global memory BFS
        result = run_geodesicRangeUnlimited(mask, max_distance=500)
    """
    original_shape = array.shape
    zoom_factor = 1.0
    
    # Scale array before computation
    if resize_for_compute:
        array = resize_array(array, max_size)
        # Re-binarize after resize (bilinear interpolation creates intermediate values)
        array = (array > 0.5).astype(np.int32)
        # Calculate zoom factor from actual resize (for result scaling)
        zoom_factor = max(original_shape) / max(array.shape)
        # Scale max_distance: smaller image = smaller distance
        if max_distance is not None:
            max_distance = max_distance * max(array.shape) / max(original_shape)
    
    # Perform computation
    result = run_geodesic_range_unlimited(
        array,
        max_distance=max_distance,
        batch_size=batch_size,
        threads_per_block=threads_per_block,
        use_cuda=use_cuda
    )
    
    # Rescale array after computation
    if resize_for_compute:
        # Log pre-scaling statistics for debugging
        valid_before = result[result > 0]
        if len(valid_before) > 0:
            print(f"  Pre-scaling geodesic range - shape: {result.shape}, zoom_factor: {zoom_factor:.4f}")
            print(f"    min: {valid_before.min():.2f}, max: {valid_before.max():.2f}, mean: {valid_before.mean():.2f}")
        
        # Scale area-based values (count of pixels) BEFORE resizing
        # This ensures correct scaling: count in smaller image -> equivalent count in original image
        result = result * zoom_factor ** 2
        
        # Log post-scaling, pre-resize statistics
        valid_after_scale = result[result > 0]
        if len(valid_after_scale) > 0:
            print(f"  Post-scaling (pre-resize) geodesic range:")
            print(f"    min: {valid_after_scale.min():.2f}, max: {valid_after_scale.max():.2f}, mean: {valid_after_scale.mean():.2f}")
        
        # Use nearest-neighbor interpolation for count data (order=0)
        # to avoid averaging discrete count values
        result = resize_array_xy(result, original_shape, order=0)
        
        # Log final statistics
        valid_final = result[result > 0]
        if len(valid_final) > 0:
            print(f"  Final geodesic range - shape: {result.shape}")
            print(f"    min: {valid_final.min():.2f}, max: {valid_final.max():.2f}, mean: {valid_final.mean():.2f}")
    
    return result


def run_geodesicRange_SuperSeeded(
        array: np.ndarray,
        max_distance: float32,
        resize_for_compute:bool=False,
        max_size:int=1024,
        threads_per_block=(32, 32),
        use_cuda: bool = True,
    ):
    """
    Runs the Breadth-First Search (BFS) kernel on the GPU if available, otherwise on
    the CPU.
    The result is the number of visited pixels for each point.
    The algorithm walks the grid in euclidean manhattan distance.

    Args:
        array (numpy.ndarray): The input 2D array with obstacles.
        max_distance (float): The maximum distance to travel.
        threads_per_block (tuple): The number of threads per block. Default is (4, 4).
        use_cuda (bool): Whether to use the CUDA GPU. Default is True.

    Returns:
        result (numpy.ndarray): The output 2D array with the number of visited pixels for each point.
    """
    original_shape = array.shape
    zoom_factor = 1.0
    
    #scale array before computation
    if resize_for_compute:
        array = resize_array(array, max_size)
        # Re-binarize after resize (bilinear interpolation creates intermediate values)
        array = (array > 0.5).astype(np.int32)
        # Calculate zoom factor from actual resize (for result scaling)
        zoom_factor = max(original_shape) / max(array.shape)
        # Scale max_distance: smaller image = smaller distance
        max_distance = float32(max_distance * max(array.shape) / max(original_shape))
        print(f"Resized compute array from shape {original_shape} to shape: {array.shape}")
    else:
        # Ensure max_distance is float32 even when not resizing
        max_distance = float32(max_distance)

        
    # perform computation
    # Note: Original kernel uses 256x256 visited array, may have issues with images >= 256x256
    # For large images, consider using run_geodesicRange instead
    if cuda.is_available() and use_cuda:
        print("Using CUDA GPU")
        rows, cols = array.shape
        # Check if image is too large for original kernel (256x256 visited array limit)
        if rows >= 256 or cols >= 256:
            print(f"Warning: Image size ({rows}x{cols}) may cause issues with original kernel. Consider using run_geodesicRange for large images.")
        if threads_per_block[0] > 32 or threads_per_block[1] > 32:
            print(
                "There can't be more than 32 threads per block for this implementation. Using default (32, 32)"
            )
            result = run_bfs_cuda(array, max_distance)
        else:
            result = run_bfs_cuda(array, max_distance, threads_per_block)
    else:
        print("CUDA GPU not available. Using CPU with Numba")
        result =  bfs_cpu(array, max_distance)

    #rescale array after computation
    if resize_for_compute:
        # Scale area-based values (count of pixels) BEFORE resizing
        # This ensures correct scaling: count in smaller image -> equivalent count in original image
        result = result * zoom_factor ** 2
        # Use nearest-neighbor interpolation for count data (order=0)
        # to avoid averaging discrete count values
        result = resize_array_xy(result, original_shape, order=0)
        
    return result


def run_geodesicDistance_Aggregated(
        array: np.ndarray,
        max_distance: float = None,
        resize_for_compute: bool = False,
        max_size: int = 1024,
        batch_size: int = 4096,
        threads_per_block: Tuple[int, int] = (16, 16),
        use_cuda: bool = True,
    ):
    """
    Compute the sum of geodesic distances from each pixel to all reachable pixels.
    
    This computes an "integration" metric useful for understanding total travel
    costs from each location. Lower values indicate more central/accessible locations.
    
    Note: This computation is inherently O(N²) and slower than geodesic range.
    For best performance, use resize_for_compute=True.
    
    Args:
        array (np.ndarray): Input 2D array (0=walkable/free space, 1=obstacle).
        max_distance (float): Maximum distance. None = use image diagonal.
        resize_for_compute (bool): Whether to resize for computation. Default False.
        max_size (int): Maximum size for resizing. Default 1024.
        batch_size (int): Pixels per GPU batch. Default 4096.
        threads_per_block (tuple): CUDA thread block dimensions. Default (16, 16).
        use_cuda (bool): Whether to use GPU acceleration. Default True.
    
    Returns:
        np.ndarray: 2D array where each pixel contains sum of distances to all reachable pixels.
    
    Example:
        # Compute total distance (recommended: use resizing for speed)
        result = run_geodesicDistanceAggregated(mask, resize_for_compute=True, max_size=300)
        
        # Find most central pixel (lowest total distance)
        central = np.unravel_index(np.argmin(result[result > 0]), result.shape)
    """
    original_shape = array.shape
    zoom_factor = 1.0
    
    # Scale array before computation
    if resize_for_compute:
        array = resize_array(array, max_size)
        # Re-binarize after resize (bilinear interpolation creates intermediate values)
        array = (array > 0.5).astype(np.int32)
        # Calculate zoom factor from actual resize (for result scaling)
        zoom_factor = max(original_shape) / max(array.shape)
        # Scale max_distance: smaller image = smaller distance
        if max_distance is not None:
            max_distance = max_distance * max(array.shape) / max(original_shape)
    
    # Perform computation
    result = run_geodesic_distance_aggregated(
        array,
        max_distance=max_distance,
        batch_size=batch_size,
        threads_per_block=threads_per_block,
        use_cuda=use_cuda
    )
    
    # Rescale array after computation
    if resize_for_compute:
        # Log pre-scaling statistics for debugging
        valid_before = result[result > 0]
        if len(valid_before) > 0:
            print(f"  Pre-scaling aggregated distance - shape: {result.shape}, zoom_factor: {zoom_factor:.4f}")
            print(f"    min: {valid_before.min():.2f}, max: {valid_before.max():.2f}, mean: {valid_before.mean():.2f}")
        
        # Scale aggregated distance (sum of distances to all reachable pixels) BEFORE resizing
        # Aggregated distance scales by zoom_factor^3 because:
        # - When image size doubles, the raw aggregated distance values scale by zoom_factor^4
        # - To normalize to original image space, we need to scale by zoom_factor^3
        # - This accounts for: (number of pixels) * (average distance) where both scale with resolution
        # - Empirical data shows values double when size doubles with zoom_factor^2 scaling,
        #   indicating raw values scale by zoom_factor^4, requiring zoom_factor^3 compensation
        result = result * zoom_factor ** 3
        
        # Log post-scaling, pre-resize statistics
        valid_after_scale = result[result > 0]
        if len(valid_after_scale) > 0:
            print(f"  Post-scaling (pre-resize) aggregated distance:")
            print(f"    min: {valid_after_scale.min():.2f}, max: {valid_after_scale.max():.2f}, mean: {valid_after_scale.mean():.2f}")
        
        # Use nearest-neighbor interpolation for distance data (order=0)
        result = resize_array_xy(result, original_shape, order=0)
        
        # Log final statistics
        valid_final = result[result > 0]
        if len(valid_final) > 0:
            print(f"  Final aggregated distance - shape: {result.shape}")
            print(f"    min: {valid_final.min():.2f}, max: {valid_final.max():.2f}, mean: {valid_final.mean():.2f}")
        
    return result


def run_signedDistance(mask: np.ndarray, 
                                reference: np.ndarray, 
                                resize_for_compute: bool=False,
                                max_size: int=1024,
                                threads_per_block: Tuple[int, int]=(16, 16), 
                                use_cuda: bool=True,
                                cap_at_zero: bool=True
                                ) -> np.ndarray:
    """
    Wrapper function for calculating the signed distance field.
    This function is executed on the CPU or GPU depending on the availability of CUDA.


    Args:
        mask (np.array): A 2D array where 0 is open (used for calculations) and 1 is ignored.
        reference (np.array): A 2D array where 0 is ignored and >0 defines target points.
        blocks (Tuple[int, int]): A tuple representing the number of blocks in the grid if using CUDA.
        use_cuda (bool): A boolean indicating whether to use CUDA for computation
        cap_at_zero (bool): If True, caps negative values at 0 (default: True)

    Returns:
        result (np.array): 
        A 2D array representing the signed distance field.
    """
    # Ensure inputs are numpy arrays
    mask = np.array(mask, dtype=np.int32)
    reference = np.array(reference, dtype=np.int32)

    
    original_shape = mask.shape
    
    #scale array before computation
    if resize_for_compute:
        mask = resize_array(mask, max_size)
        reference = resize_array(reference, max_size)
        print(f"Resized compute array from shape {original_shape} to shape: {mask.shape}")

    # Perform computation
    if cuda.is_available() and use_cuda:
        print("CUDA is available. Using CUDA for computation")
        result = cuda_signed_distance_function(mask, reference, threads_per_block)
    else:
        print("CUDA not available. Using CPU with Numba (parallel)")
        result =  cpu_signed_distance_function(mask, reference)

    #rescale array after computation
    if resize_for_compute:
        # Use nearest-neighbor (order=0) to preserve boundary pixels correctly
        result = resize_array_xy(result, original_shape, order=0)
        result = result * max(original_shape) / max_size
    
    # Cap negative values at 0 if requested
    if cap_at_zero:
        result = np.maximum(result, 0)
        
    return result


def run_stepDepth(
        obstacle_array: np.ndarray,
        start_positions: np.ndarray,
        max_iterations: int,
        num_rays: int = 360,
        resize_for_compute: bool = False,
        max_size: int = 1024,
        threads_per_block: Tuple[int, int] = (16, 16),
        use_cuda: bool = True,
    ) -> np.ndarray:
    """
    Perform iterative isovist-based raycasting with expanding frontier.
    This algorithm casts rays in all directions from start positions to form isovist polygons,
    then fills those polygons to mark visible pixels. This approach is typically faster for
    large images compared to the standard raycasting approach.
    
    This algorithm is used to calculate the visible step depth from given starting positions.
    This can give a sense of the visible depth of the environment from given points.
    It can be executed on CPU or GPU using CUDA.

    Args:
        obstacle_array (np.ndarray): A 2D array representing the input mask as np array where with obstacles 1 and free space as 0.
        start_positions (np.ndarray): A 2D array of initial starting positions, each row containing [x, y] coordinates.
        max_iterations (int): Maximum number of iterations to perform.
        num_rays (int): Number of rays to cast in all directions from each start position (default: 360).
        resize_for_compute (bool): Whether to resize the input arrays for computation (default: False).
        max_size (int): Maximum side length for resizing (default: 1024).
        threads_per_block (Tuple[int, int]): Threads per block configuration (default: (16, 16)).
        use_cuda (bool): Whether to use CUDA for GPU acceleration (default: True).

    Returns:
        np.ndarray: A 2D array with raycast results (0: not visible, 1+: iteration when became visible).
    """
    original_shape = obstacle_array.shape
    
    #scale array before computation
    if resize_for_compute:
        obstacle_array = resize_array(obstacle_array, max_size)
        # Scale coordinates properly using actual zoom factors for x and y separately
        resized_shape = obstacle_array.shape
        zoom_y = resized_shape[0] / original_shape[0]
        zoom_x = resized_shape[1] / original_shape[1]
        start_positions = [[int(point[0] * zoom_x), int(point[1] * zoom_y)] for point in start_positions]
        print(f"Resized compute array from shape {original_shape} to shape: {obstacle_array.shape}")
    
    # Perform computation
    if use_cuda and cuda.is_available():
        print("CUDA is available. Using CUDA for isovist-based computation")
        result = gpu_iterative_isovist_raycast(
            obstacle_array, start_positions, max_iterations, num_rays, threads_per_block
        )
    else:
        print("CUDA not available. Using CPU with Numba (parallel) for isovist-based computation")
        result = cpu_iterative_isovist_raycast(
            obstacle_array, start_positions, max_iterations, num_rays
        )

    if resize_for_compute:
        # Use nearest-neighbor (order=0) to preserve boundary pixels correctly
        result = resize_array_xy(result, original_shape, order=0)
        
    return result


def run_stepDepth_SuperSeeded(
        obstacle_array: np.ndarray,
        start_positions: np.ndarray,
        max_iterations: int,
        resize_for_compute: bool = False,
        max_size: int = 1024,
        threads_per_block: Tuple[int, int] = (8, 8),
        use_cuda: bool = True,
    ) -> np.ndarray:
    """
    Perform iterative raycasting with expanding frontier.
    This algorithm is used to calculate the visible step depth from given starting positions.
    This can give a sense of the visible depth of the environment from given points.
    It can be executed on CPU or GPU using CUDA.

    Args:
        obstacle_array (np.ndarray): A 2D array representing the input mask as np array where with obstacles 1 and free space as 0.
        start_positions (np.ndarray): A 2D array of initial starting positions, each row containing [x, y] coordinates.
        max_iterations (int): Maximum number of iterations to perform.
        use_cuda (bool): Whether to use CUDA for GPU acceleration.

    Returns:
        np.ndarray: A 2D array with raycast results (0: not visible, 1+: iteration when became visible).
    """
    original_shape = obstacle_array.shape
    
    #scale array before computation
    if resize_for_compute:
        obstacle_array = resize_array(obstacle_array, max_size)
        # Scale coordinates properly using actual zoom factors for x and y separately
        resized_shape = obstacle_array.shape
        zoom_y = resized_shape[0] / original_shape[0]
        zoom_x = resized_shape[1] / original_shape[1]
        start_positions = [[int(point[0] * zoom_x), int(point[1] * zoom_y)] for point in start_positions]
        print(f"Resized compute array from shape {original_shape} to shape: {obstacle_array.shape}")
    
    # Perform computation
    if use_cuda and cuda.is_available():
        print("CUDA is available. Using CUDA for computation")
        result = gpu_iterative_raycast(
            obstacle_array, start_positions, max_iterations, threads_per_block
        )
    else:
        print("CUDA not available. Using CPU with Numba (parallel)")
        result = cpu_iterative_raycast(obstacle_array, start_positions, max_iterations)

    if resize_for_compute:
        # Use nearest-neighbor (order=0) to preserve boundary pixels correctly
        result = resize_array_xy(result, original_shape, order=0)
        
    return result


def run_visibleArea(
        obstacle_array: np.ndarray,
        max_distance: float = None,
        num_rays: int = 360,
        resize_for_compute: bool = False,  
        max_size: int = 1024,
        threads_per_block=(16, 16),
        use_cuda: bool = True,
    ) -> np.ndarray:
    """
    Wrapper function for performing bresenham's line based raycasting in all directions and calculating the area between the endpoints of the rays.
    This function is executed on the CPU or GPU depending on the availability of CUDA.

    Args:
        obstacle_array (np.ndarray): A 2D array representing the input mask as np array where with obstacles 1 and free space as 0.
        num_rays (int): The number of rays to be cast from each pixel.
        max_distance (float): The maximum distance that the rays can travel. None = use image diagonal.
        resize_for_compute (bool): Whether to resize the input arrays for the computation.
        max_size (int): An integer representing the maximum side length for resizing the input arrays. Default is 1024.
        threads_per_block (tuple): A tuple representing the number of threads per block. Default is (16, 16).
        use_cuda (bool): Whether to use the CUDA GPU. Default is True.

        Returns:
        result (np.ndarray): 
        A 2D array representing the visibility area for each pixel.
    """
    import math
    
    original_shape = obstacle_array.shape
    zoom_factor = 1.0
    
    # Set max_distance to diagonal if not provided
    if max_distance is None:
        max_distance = math.sqrt(original_shape[0]**2 + original_shape[1]**2)
    
    if resize_for_compute:
        obstacle_array = resize_array(obstacle_array, max_size, rescale_by_larger=True)
        # Calculate zoom factor from actual resize (for result scaling)
        zoom_factor = max(original_shape) / max(obstacle_array.shape)
        # Scale max_distance: smaller image = smaller distance
        max_distance = max_distance * max(obstacle_array.shape) / max(original_shape)
        print(f"Resized compute array from shape {original_shape} to shape: {obstacle_array.shape}")

    
    #scale array before computation
    shape = obstacle_array.shape
    area_output = np.zeros(shape, dtype=np.float32)
    
    #perform computation
    if cuda.is_available() and use_cuda:
        print("CUDA is available. Using CUDA for computation")
        obstacle_array_gpu = cuda.to_device(obstacle_array)
        area_output_gpu = cuda.to_device(area_output)

        blocks_per_grid = (
            (shape[1] + threads_per_block[0] - 1) // threads_per_block[0],
            (shape[0] + threads_per_block[1] - 1) // threads_per_block[1],
        )
        raycast_and_area_cuda[blocks_per_grid, threads_per_block](
            obstacle_array_gpu, num_rays, max_distance, area_output_gpu
        )

        area_output = area_output_gpu.copy_to_host()
    else:
        print("CUDA not available. Using CPU with Numba (parallel)")
        raycast_and_area_cpu(
            obstacle_array, int32(num_rays), float32(max_distance), area_output
        )

    #rescale array after computation
    if resize_for_compute:
        # Scale area-based values BEFORE resizing
        # This ensures correct scaling: area in smaller image -> equivalent area in original image
        area_output = area_output * zoom_factor ** 2
        # Use nearest-neighbor interpolation for area data (order=0)
        area_output = resize_array_xy(area_output, original_shape, order=0)
    
    return area_output


def run_visibleObstacle(stop_array: np.ndarray, 
                        target_array: np.ndarray, 
                        num_rays: int32, 
                        max_distance: float32 = None, 
                        resize_for_compute:bool=False,
                        max_size:int=1024,
                        threads_per_block:Tuple[int, int]=(16,16), 
                        use_cuda:bool=True
                        ) -> np.ndarray:
    """
    Function for performing ray casting and hit count calculation for all pixels.
    This function is executed on the CPU or GPU.

    Args:
        stop_array (np.ndarray): A 2D array representing the input mask as np array where with obstacles 1 and free space as 0.
        target_array (np.ndarray): A 2D array representing the target points as np array where with points of interest 1 and free space as 0.
        num_rays (int32): The number of rays to be shot from each pixel.
        max_distance (float32): The maximum distance that the rays can travel. None = use image diagonal.
        threads_per_block (tuple): A tuple representing the number of threads per block. Default is (16, 16).
        use_cuda (bool): Whether to use the CUDA GPU. Default is True.
    
    Returns:
        result (np.ndarray): 
        A 2D array representing the hit count for each pixel.
    """
    import math
    
    original_shape = stop_array.shape
    zoom_factor = 1.0
    
    # Set max_distance to diagonal if not provided
    if max_distance is None:
        max_distance = float32(math.sqrt(original_shape[0]**2 + original_shape[1]**2))
    else:
        max_distance = float32(max_distance)
    
    #scale array before computation
    if resize_for_compute:
        stop_array = resize_array(stop_array, max_size, rescale_by_larger=True)
        target_array = resize_array(target_array, max_size, rescale_by_larger=True )
        # Calculate zoom factor from actual resize (for result scaling)
        zoom_factor = max(original_shape) / max(stop_array.shape)
        # Scale max_distance: smaller image = smaller distance
        max_distance = float32(max_distance * max(stop_array.shape) / max(original_shape))
        print(f"Resized compute array from shape {original_shape} to shape: {stop_array.shape}")

    
    #perform computation
    if cuda.is_available() and use_cuda:
        print("CUDA is available. Using CUDA for computation")
        result = raycast_hit_count_cuda_wrapper(stop_array, target_array, num_rays, max_distance, threads_per_block)
    else:
        print("CUDA not available. Using CPU with Numba (parallel)")
        result = raycast_hit_count_cpu(stop_array, target_array, num_rays, max_distance)
    
    #rescale array after computation
    if resize_for_compute:
        # Use nearest-neighbor interpolation for count data (order=0)
        # Note: Absolute counts (number of ray hits) should NOT be scaled
        result = resize_array_xy(result, original_shape, order=0)
        
    return result


def run_visibleObstacleDistance(mask: np.ndarray, 
                        obstacle_array: np.ndarray, 
                        num_rays: int32, 
                        max_distance: float32 = None, 
                        resize_for_compute:bool=False,
                        max_size:int=1024,
                        threads_per_block:Tuple[int, int]=(16,16), 
                        use_cuda:bool=True
                        ) -> np.ndarray:
    """
    Function for performing ray casting and calculating minimum distance to obstacles for all pixels.
    This function casts rays from each pixel and returns the minimum distance to obstacles that the rays hit.
    This function is executed on the CPU or GPU.

    Args:
        mask (np.ndarray): A 2D array representing the input mask where 0 is valid and 1 is excluded.
        obstacle_array (np.ndarray): A 2D array where obstacles are 1 and free space is 0.
        num_rays (int32): The number of rays to be shot from each pixel.
        max_distance (float32): The maximum distance that the rays can travel. None = use image diagonal.
        resize_for_compute (bool): Whether to resize the input arrays for computation. Defaults to False.
        max_size (int): Maximum side length for resizing. Defaults to 1024.
        threads_per_block (Tuple[int, int]): A tuple representing the number of threads per block. Default is (16, 16).
        use_cuda (bool): Whether to use the CUDA GPU. Default is True.
    
    Returns:
        result (np.ndarray): 
        A 2D array representing the minimum distance to obstacles for each pixel.
    """
    import math
    
    original_shape = mask.shape
    zoom_factor = 1.0
    
    # Set max_distance to diagonal if not provided
    if max_distance is None:
        max_distance = float32(math.sqrt(original_shape[0]**2 + original_shape[1]**2))
    else:
        max_distance = float32(max_distance)
    
    #scale array before computation
    if resize_for_compute:
        mask = resize_array(mask, max_size, rescale_by_larger=True)
        obstacle_array = resize_array(obstacle_array, max_size, rescale_by_larger=True)
        # Binarize the resized arrays (resize can create fractional values)
        mask = (mask > 0.5).astype(np.int32)
        obstacle_array = (obstacle_array > 0.5).astype(np.int32)
        # Calculate zoom factor from actual resize (for result scaling)
        zoom_factor = max(original_shape) / max(mask.shape)
        # Scale max_distance: smaller image = smaller distance
        max_distance = float32(max_distance * max(mask.shape) / max(original_shape))
        print(f"Resized compute array from shape {original_shape} to shape: {mask.shape}")

    
    #perform computation
    if cuda.is_available() and use_cuda:
        print("CUDA is available. Using CUDA for computation")
        result = raycast_min_distance_cuda_wrapper(mask, obstacle_array, num_rays, max_distance, threads_per_block)
    else:
        print("CUDA not available. Using CPU with Numba (parallel)")
        result = raycast_min_distance_cpu(mask, obstacle_array, num_rays, max_distance)
    
    #rescale array after computation
    if resize_for_compute:
        # Scale distance values BEFORE resizing
        # This ensures correct scaling: distance in smaller image -> equivalent distance in original image
        result = result * zoom_factor
        # Use nearest-neighbor interpolation for distance data (order=0)
        result = resize_array_xy(result, original_shape, order=0)
        
    return result
