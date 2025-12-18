import numpy as np
import numba as nb

from PIL import Image
import PIL.Image

from scipy.ndimage import zoom



def resize_image(img: PIL.Image, size: int) -> PIL.Image:
    """
    Resize an image according to the smaller dimension.
    
    Args:
        img (PIL.Image): Image to be resized.
        size (int): Size of the smaller dimension.
        
    Returns:
        img (PIL.Image): Resized
    """
    h, w = img.size
    if h < w:
        new_h = size
        new_w = int(w * size / h)
    else:
        new_h = int(h * size / w)
        new_w = size

    img = img.resize((new_h, new_w), Image.LANCZOS)
    return img


def resize_array(array: np.ndarray, new_size: int, rescale_by_larger: bool = True) -> np.ndarray:
    """
    Resize a 2D NumPy array to a new size specified by a single dimension.
    
    Args:
        array (np.ndarray): 2D NumPy array to resize.
        new_size (int): New size of the array.
        
    Returns:
        array (np.ndarray): Resized 2D NumPy array.
    """
    height, width = array.shape
    aspect_ratio = width / height

    if rescale_by_larger:
        if width >= height:
            new_width = new_size
            new_height = int(new_size / aspect_ratio)
        else:
            new_height = new_size
            new_width = int(new_size * aspect_ratio)
    else:
        if width >= height:
            new_height = new_size
            new_width = int(new_size * aspect_ratio)
        else:
            new_width = new_size
            new_height = int(new_size / aspect_ratio)


    zoom_factors = (new_height / height, new_width / width)
    return zoom(array, zoom_factors, order=1)


def resize_array_xy(array: np.ndarray, new_size: np.ndarray, order: int = 1) -> np.ndarray:
    """
    Resize a 2D NumPy array to a new size specified by x and y dimensions.

    Args:
        array (np.ndarray): 2D NumPy array to resize
        new_size (np.ndarray): New size of the array
        order (int): Interpolation order. 0=nearest-neighbor, 1=bilinear. Default is 1.
                    Use 0 for discrete count data, 1 for continuous values.
        
    Returns:
        array (np.ndarray): Resized 2D NumPy array.
    """
    height, width = array.shape
    new_height, new_width = new_size

    # For nearest-neighbor (order=0), use custom implementation that preserves boundary pixels correctly
    if order == 0:
        return _resize_nearest_neighbor(array, (new_height, new_width))
    
    # For bilinear (order=1), use scipy zoom
    zoom_factors = (new_height / height, new_width / width)
    return zoom(array, zoom_factors, order=order)


def _resize_nearest_neighbor(array: np.ndarray, new_size: tuple) -> np.ndarray:
    """
    Custom nearest-neighbor upscaling that correctly preserves boundary pixels.
    This ensures that boundary pixels in the source map correctly to boundary pixels in the target.
    Uses vectorized numpy operations for performance.
    
    The mapping ensures:
    - First pixel (0,0) maps to first pixel (0,0)
    - Last pixel (h-1, w-1) maps to last pixel (new_h-1, new_w-1)
    - Boundary pixels are preserved correctly
    
    Args:
        array (np.ndarray): 2D array to resize
        new_size (tuple): (new_height, new_width)
        
    Returns:
        array (np.ndarray): Resized array using nearest-neighbor interpolation
    """
    height, width = array.shape
    new_height, new_width = new_size
    
    # Create coordinate grids for target pixels
    y_coords = np.arange(new_height, dtype=np.float32)
    x_coords = np.arange(new_width, dtype=np.float32)
    
    # Map target coordinates to source coordinates
    # Use mapping that preserves boundaries: first->first, last->last
    if new_height > 1:
        src_y = y_coords * (height - 1) / (new_height - 1)
    else:
        src_y = np.array([0.0], dtype=np.float32)
    
    if new_width > 1:
        src_x = x_coords * (width - 1) / (new_width - 1)
    else:
        src_x = np.array([0.0], dtype=np.float32)
    
    # Round to nearest integer (nearest neighbor)
    src_y_int = np.round(src_y).astype(np.int32)
    src_x_int = np.round(src_x).astype(np.int32)
    
    # Clamp to array bounds (safety check)
    src_y_int = np.clip(src_y_int, 0, height - 1)
    src_x_int = np.clip(src_x_int, 0, width - 1)
    
    # Use advanced indexing to create result
    # Create meshgrid for indexing
    y_grid, x_grid = np.meshgrid(src_y_int, src_x_int, indexing='ij')
    
    return array[y_grid, x_grid]


def convert_2d_to_3d(image_2d: np.ndarray) -> np.ndarray:
    """
    Convert a 2D image to a 3D image by repeating the 2D image along a new axis.
    
    Args:
        image_2d (np.ndarray): 2D NumPy array representing the image.
    
    Returns:
        image_3d (np.ndarray): 3D NumPy array representing the image.
    """
    # Ensure the input is a 2D numpy array
    if len(image_2d.shape) != 2:
        raise ValueError("Input must be a 2D numpy array")

    # Create a 3D array by repeating the 2D array along a new axis
    image_3d = np.repeat(image_2d[:, :, np.newaxis], 3, axis=2)

    return image_3d


def convert_3d_to_2d(image_3d: np.ndarray) -> np.ndarray:
    """
    CUDA kernel for flood fill algorithm.
    This function is executed on the GPU.

    Parameters:
        image_3d (np.ndarray): 3D NumPy array representing the image.

    Returns:
        changes (np.ndarray): 2D NumPy array representing the image.
    """
    image_3d = np.array(image_3d)

    # Check if the input is 3D
    if len(image_3d.shape) != 3:
        raise ValueError("Input must be a 3D image array")

    # Calculate the mean across the depth dimension
    avg_values = np.mean(image_3d, axis=2)
    # Normalize the values to [0, 1] range
    normalized_values = (avg_values - np.min(avg_values)) / (np.max(avg_values) - np.min(avg_values))
    # Round the values to either 0 or 1
    image_2d = np.round(normalized_values).astype(int)

    return image_2d


def scale_coordinates(coordinates: np.ndarray, original_size: np.ndarray, new_size: np.ndarray) -> np.ndarray:  
    """
    Scale coordinates from the original size to the new size.

    Parameters:
        coordinates (np.ndarray): 1D NumPy array representing the coordinates to be scaled.
        original_size (np.ndarray): 1D NumPy array representing the original size.
        new_size (np.ndarray): 1D NumPy array representing the new size.
        
    Returns:
        scaled_coordinates (np.ndarray): 1D NumPy array representing the scaled coordinates.
    """
    return [int(coordinate * new_size / original_size) for coordinate in coordinates]
