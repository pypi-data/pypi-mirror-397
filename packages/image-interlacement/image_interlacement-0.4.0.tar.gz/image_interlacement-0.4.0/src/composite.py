"""Image compositing module for creating alternating row/column composites."""

from PIL import Image
import numpy as np
from typing import Literal, List


def create_solid_image(color: str, width: int, height: int) -> np.ndarray:
    """
    Create a solid color image array.
    
    Args:
        color: 'white' or 'black'
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        RGB image array filled with the solid color
        
    Raises:
        ValueError: If color is not 'white' or 'black'
    """
    if color.lower() not in ('white', 'black'):
        raise ValueError(f"Color must be 'white' or 'black', got '{color}'")
    
    color_value = 255 if color.lower() == 'white' else 0
    return np.full((height, width, 3), color_value, dtype=np.uint8)


def tile_image(image_array: np.ndarray, target_height: int, target_width: int) -> np.ndarray:
    """
    Tile an image to match target dimensions.
    
    Args:
        image_array: The image array to tile
        target_height: Target height in pixels
        target_width: Target width in pixels
        
    Returns:
        Tiled image array with exact target dimensions
    """
    current_height, current_width = image_array.shape[:2]
    
    # Calculate how many times to tile in each direction
    tiles_y = (target_height + current_height - 1) // current_height
    tiles_x = (target_width + current_width - 1) // current_width
    
    # Tile the image
    if len(image_array.shape) == 3:
        tiled = np.tile(image_array, (tiles_y, tiles_x, 1))
    else:
        tiled = np.tile(image_array, (tiles_y, tiles_x))
    
    # Crop to exact target dimensions
    return tiled[:target_height, :target_width]


# Define a maximum size for input images
MAX_IMAGE_SIZE = (2000, 2000)  # (width, height)

def validate_image_size(image: Image.Image) -> None:
    """
    Validate that the image does not exceed the maximum allowed size.

    Args:
        image: PIL Image object to validate.

    Raises:
        ValueError: If the image exceeds the maximum size.
    """
    if image.width > MAX_IMAGE_SIZE[0] or image.height > MAX_IMAGE_SIZE[1]:
        raise ValueError(
            f"Image size {image.width}x{image.height} exceeds the maximum allowed size of {MAX_IMAGE_SIZE[0]}x{MAX_IMAGE_SIZE[1]} pixels."
        )


def validate_and_load_images(image_paths: List[str]) -> List[np.ndarray]:
    """
    Load and validate multiple images (supports 'white'/'black'), then tile to match.

    - Accepts file paths and the strings 'white' or 'black' for solid colors.
    - Enforces per-image maximum size (2000x2000) for file-based images.
    - Requires at least one real image to define target dimensions.

    Args:
        image_paths: List of image file paths or 'white'/'black'.

    Returns:
        List of image arrays with matching dimensions.

    Raises:
        ValueError: If any file image exceeds max size or if no real image is provided.
    """
    real_images: List[np.ndarray] = []
    color_flags: List[str] = []
    max_width, max_height = 0, 0

    # First pass: load real images, remember color placeholders
    for path in image_paths:
        if isinstance(path, str) and path.lower() in ("white", "black"):
            color_flags.append(path.lower())
            continue
        img = Image.open(path)
        validate_image_size(img)
        img = img.convert("RGB")
        arr = np.array(img)
        real_images.append(arr)
        max_width = max(max_width, img.width)
        max_height = max(max_height, img.height)

    if max_width == 0 or max_height == 0:
        raise ValueError("At least one input must be a real image file (not all 'white'/'black').")

    # Build final list following original order, creating solids where requested
    result_images: List[np.ndarray] = []
    real_iter = iter(real_images)
    for path in image_paths:
        if isinstance(path, str) and path.lower() in ("white", "black"):
            result_images.append(create_solid_image(path, max_width, max_height))
        else:
            # Next real image (tile if smaller than target)
            arr = next(real_iter)
            if arr.shape[0] != max_height or arr.shape[1] != max_width:
                arr = tile_image(arr, max_height, max_width)
            result_images.append(arr)

    return result_images


def composite_rows(image1_path: str, image2_path: str, output_path: str) -> None:
    """
    Create a composite image by interleaving rows from two images.
    
    Output structure:
    - Row 0: from image1 row 0
    - Row 1: from image2 row 0
    - Row 2: from image1 row 1
    - Row 3: from image2 row 1
    - etc.
    
    The output image height will be 2x the input height.
    
    Args:
        image1_path: Path to the first input image
        image2_path: Path to the second input image
        output_path: Path to save the output composite image
    """
    images = validate_and_load_images([image1_path, image2_path])
    img1_array, img2_array = images[0], images[1]
    
    height, width = img1_array.shape[:2]
    
    # Create output array with 2x height (interleaved rows)
    if len(img1_array.shape) == 3:
        output = np.zeros((height * 2, width, img1_array.shape[2]), dtype=img1_array.dtype)
    else:
        output = np.zeros((height * 2, width), dtype=img1_array.dtype)
    
    # Interleave rows: odd rows from img1, even rows from img2
    output[::2] = img1_array   # Rows 0, 2, 4, ... from image1
    output[1::2] = img2_array  # Rows 1, 3, 5, ... from image2
    
    # Save the result
    result_image = Image.fromarray(output)
    result_image.save(output_path)


def composite_columns(image1_path: str, image2_path: str, output_path: str) -> None:
    """
    Create a composite image by interleaving columns from two images.
    
    Output structure:
    - Column 0: from image1 column 0
    - Column 1: from image2 column 0
    - Column 2: from image1 column 1
    - Column 3: from image2 column 1
    - etc.
    
    The output image width will be 2x the input width.
    
    Args:
        image1_path: Path to the first input image
        image2_path: Path to the second input image
        output_path: Path to save the output composite image
    """
    images = validate_and_load_images([image1_path, image2_path])
    img1_array, img2_array = images[0], images[1]
    
    height, width = img1_array.shape[:2]
    
    # Create output array with 2x width (interleaved columns)
    if len(img1_array.shape) == 3:
        output = np.zeros((height, width * 2, img1_array.shape[2]), dtype=img1_array.dtype)
    else:
        output = np.zeros((height, width * 2), dtype=img1_array.dtype)
    
    # Interleave columns: odd columns from img1, even columns from img2
    output[:, ::2] = img1_array   # Columns 0, 2, 4, ... from image1
    output[:, 1::2] = img2_array  # Columns 1, 3, 5, ... from image2
    
    # Save the result
    result_image = Image.fromarray(output)
    result_image.save(output_path)


def composite(
    image1_path: str, 
    image2_path: str, 
    output_path: str, 
    mode: Literal['rows', 'columns'] = 'rows'
) -> None:
    """
    Create a composite image by alternating rows or columns from two images.
    
    Args:
        image1_path: Path to the first input image
        image2_path: Path to the second input image
        output_path: Path to save the output composite image
        mode: 'rows' to alternate rows, 'columns' to alternate columns
        
    Raises:
        ValueError: If mode is not 'rows' or 'columns', or if images don't match
    """
    if mode not in ('rows', 'columns'):
        raise ValueError(f"Mode must be 'rows' or 'columns', got '{mode}'")
    
    if mode == 'rows':
        composite_rows(image1_path, image2_path, output_path)
    else:
        composite_columns(image1_path, image2_path, output_path)


def interlace_rows(image1_path: str, image2_path: str, output_path: str) -> None:
    """
    Create a same-size interlaced image by taking alternating rows from two images.

    Behavior:
    - Output has the same height/width as the (tiled) input images
    - Output rows at even indices come from `image1`'s corresponding even rows
    - Output rows at odd indices come from `image2`'s corresponding odd rows

    Args:
        image1_path: Path to the first input image
        image2_path: Path to the second input image
        output_path: Path to save the output interlaced image
    """
    images = validate_and_load_images([image1_path, image2_path])
    img1_array, img2_array = images[0], images[1]

    height, width = img1_array.shape[:2]

    # Create output array with same shape
    if len(img1_array.shape) == 3:
        output = np.zeros((height, width, img1_array.shape[2]), dtype=img1_array.dtype)
    else:
        output = np.zeros((height, width), dtype=img1_array.dtype)

    # Interlace rows in-place using corresponding row indices
    output[::2] = img1_array[::2]
    output[1::2] = img2_array[1::2]

    result_image = Image.fromarray(output)
    result_image.save(output_path)


def interlace_columns(image1_path: str, image2_path: str, output_path: str) -> None:
    """
    Create a same-size interlaced image by taking alternating columns from two images.

    Behavior:
    - Output has the same height/width as the (tiled) input images
    - Output columns at even indices come from `image1`'s corresponding even columns
    - Output columns at odd indices come from `image2`'s corresponding odd columns
    
    Args:
        image1_path: Path to the first input image
        image2_path: Path to the second input image
        output_path: Path to save the output interlaced image
    """
    images = validate_and_load_images([image1_path, image2_path])
    img1_array, img2_array = images[0], images[1]

    height, width = img1_array.shape[:2]

    # Create output array with same shape
    if len(img1_array.shape) == 3:
        output = np.zeros((height, width, img1_array.shape[2]), dtype=img1_array.dtype)
    else:
        output = np.zeros((height, width), dtype=img1_array.dtype)

    # Interlace columns in-place using corresponding column indices
    output[:, ::2] = img1_array[:, ::2]
    output[:, 1::2] = img2_array[:, 1::2]

    result_image = Image.fromarray(output)
    result_image.save(output_path)


def interlace(
    image1_path: str, 
    image2_path: str, 
    output_path: str, 
    mode: Literal['rows', 'columns'] = 'rows'
) -> None:
    """
    Wrapper to call interlace_rows or interlace_columns based on `mode`.
    """
    if mode not in ('rows', 'columns'):
        raise ValueError(f"Mode must be 'rows' or 'columns', got '{mode}'")

    if mode == 'rows':
        interlace_rows(image1_path, image2_path, output_path)
    else:
        interlace_columns(image1_path, image2_path, output_path)


def composite_n_images(image_paths: List[str], output_path: str, mode: Literal['rows', 'columns'] = 'rows') -> None:
    """
    Create a composite image by interleaving rows or columns from multiple images.

    Args:
        image_paths: List of input image paths (up to 6).
        output_path: Path to save the output composite image.
        mode: 'rows' to alternate rows, 'columns' to alternate columns.

    Raises:
        ValueError: If mode is not 'rows' or 'columns', or if more than 6 images are provided.
    """
    if len(image_paths) > 6:
        raise ValueError("A maximum of 6 images can be interleaved.")

    if mode not in ('rows', 'columns'):
        raise ValueError(f"Mode must be 'rows' or 'columns', got '{mode}'")

    # Load and validate images
    images = validate_and_load_images(image_paths)

    # Determine output dimensions
    height, width = images[0].shape[:2]
    if mode == 'rows':
        output_shape = (height * len(images), width, 3)
    else:
        output_shape = (height, width * len(images), 3)

    # Create output array
    output = np.zeros(output_shape, dtype=images[0].dtype)

    # Interleave rows or columns
    for i, img in enumerate(images):
        if mode == 'rows':
            output[i::len(images)] = img
        else:
            output[:, i::len(images)] = img

    # Save the result
    result_image = Image.fromarray(output)
    result_image.save(output_path)
