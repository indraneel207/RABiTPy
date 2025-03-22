# Capture Class Documentation

## Overview

The `Capture` class is responsible for loading video files or image sequences and converting them into frames for further processing. It provides functionality to validate and load videos, extract frames at a given capture speed, and load images from a folder. In addition, it manages working directories and provides key video properties such as frame rate and pixel scale.

## Workflow

![Workflow Diagram](./flow_charts/capture.png)

1. **Initialization:**  
   The class is instantiated with an optional working directory (defaulting to `'input_files'`). It prepares internal paths, supported file types, and storage for captured frames.
2. **Video Loading and Processing:**  
   - `load_video`: Validates and loads a video file, printing out its properties (FPS, dimensions, etc.).
   - `process_video_into_frames`: Extracts frames from the loaded video based on a provided pixel scale factor and capture speed. Optionally, the frames can be saved as images.
3. **Image Loading:**  
   The `load_images_as_frames` method allows loading all images from a specified folder as frames, sorted in a natural order.
4. **Property Access:**  
   Methods like `get_captured_frames`, `get_directory`, `get_frame_rate`, and `get_pixel_scale_factor` provide access to the stored frames and video properties.
5. **Configuration:**  
   The `set_properties` method allows updating the pixel scale factor, scale units, and capture speed after initialization.

## Class Attributes

| Attribute                            | Description                                                         | Default Value                                |
|--------------------------------------|---------------------------------------------------------------------|----------------------------------------------|
| `DEFAULT_FILE_DIRECTORY`             | Default directory for input files.                                  | `'input_files'`                              |
| `DEFAULT_STORE_IMAGE_FILE_DIRECTORY` | Default directory to store images extracted from the video.         | `'frames_from_video'`                        |
| `SUPPORTED_INPUT_VIDEO_FILE_TYPES`   | Supported video file types (`avi`, `mp4`, `mpg`, `mpeg`).             | `['avi', 'mp4', 'mpg', 'mpeg']`              |
| `DEFAULT_PIXEL_SCALE_FACTOR`         | Default conversion factor from pixels to physical units (e.g., microns). | `1`                                        |
| `DEFAULT_SCALE_UNITS`                | Default scale units for the pixel scale factor.                     | `'units'`                                    |
| `DEFAULT_CAPTURE_SPEED_IN_FPS`       | Default capture speed in frames per second.                         | `15`                                         |

---

## Public Methods

### `__init__(working_directory: str = DEFAULT_FILE_DIRECTORY) -> None`

**Description:**  
Initializes the `Capture` object with the specified working directory. The constructor processes the working directory path and initializes internal attributes including supported file types and placeholders for video-related properties.

**Arguments:**

| Name                | Type  | Explanation                                           | Optional | Default Value               |
|---------------------|-------|-------------------------------------------------------|----------|-----------------------------|
| `working_directory` | `str` | The working directory for input files.              | Yes      | `DEFAULT_FILE_DIRECTORY`    |

**Returns:**

- `None`

---

### `load_video(file_name: str = '') -> str`

**Description:**  
Loads a video file based on the given file name. This method validates the file name and type, constructs the full file path, and prints video information (such as dimensions, FPS, and duration).

**Arguments:**

| Name       | Type  | Explanation                                        | Optional | Default Value |
|------------|-------|----------------------------------------------------|----------|---------------|
| `file_name`| `str` | The name of the video file to load.                | Yes      | `''`          |

**Returns:**

- `str`: The validated file path.

**Errors:**

- **`FileNotFoundError`**: Raised if the specified video file does not exist.

---

### `process_video_into_frames(pixel_scale_factor: float = DEFAULT_PIXEL_SCALE_FACTOR, scale_units: str = DEFAULT_SCALE_UNITS, capture_speed_in_fps: int = None, is_store_video_frames: bool = False, store_images_path: str = DEFAULT_STORE_IMAGE_FILE_DIRECTORY) -> list`

**Description:**  
Processes the loaded video into frames based on the provided pixel scale factor, scale units, and capture speed. Optionally, the frames can be saved as images in a specified directory.

**Arguments:**

| Name                   | Type  | Explanation                                                                                  | Optional | Default Value                              |
|------------------------|-------|----------------------------------------------------------------------------------------------|----------|--------------------------------------------|
| `pixel_scale_factor`   | `float`| Conversion factor from pixels to physical units (e.g., microns). Must be a non-zero value.      | Yes      | `DEFAULT_PIXEL_SCALE_FACTOR`               |
| `scale_units`          | `str` | Units corresponding to the pixel scale factor.                                               | Yes      | `DEFAULT_SCALE_UNITS`                      |
| `capture_speed_in_fps` | `int` | Capture speed in frames per second. If not provided, the video's default FPS is used.          | Yes      | `DEFAULT_CAPTURE_SPEED_IN_FPS` (or video FPS)|
| `is_store_video_frames`| `bool`| Flag indicating whether to save the extracted frames as images.                               | Yes      | `False`                                    |
| `store_images_path`    | `str` | Directory path where the frames should be stored if saving is enabled.                         | Yes      | `DEFAULT_STORE_IMAGE_FILE_DIRECTORY`       |

**Returns:**

- `list`: A list of captured frames as NumPy arrays.

**Errors:**

- **`ValueError`**: Raised if the `pixel_scale_factor` is not provided (or is 0).

---

### `get_captured_frames() -> list`

**Description:**  
Retrieves the list of frames captured from the video.

**Arguments:**

- None

**Returns:**

- `list`: The list of captured frames as NumPy arrays.

---

### `get_directory() -> str`

**Description:**  
Retrieves the working directory used by the Capture object.

**Arguments:**

- None

**Returns:**

- `str`: The working directory path.

---

### `get_frame_rate() -> dict`

**Description:**  
Retrieves the frame rate information for the video. Returns a dictionary containing both the user-provided FPS (if set) and the default FPS extracted from the video.

**Arguments:**

- None

**Returns:**

- `dict`: Dictionary with keys `'user_provided_fps'` and `'default_fps'`.

---

### `get_pixel_scale_factor() -> float`

**Description:**  
Retrieves the pixel scale factor (conversion factor from pixels to physical units).

**Arguments:**

- None

**Returns:**

- `float`: The pixel scale factor.

---

### `load_images_as_frames(folder_path: str, capture_speed_in_fps: int = DEFAULT_CAPTURE_SPEED_IN_FPS, pixel_scale_factor: float = DEFAULT_PIXEL_SCALE_FACTOR, scale_units: str = DEFAULT_SCALE_UNITS) -> list`

**Description:**  
Loads all images from the specified folder as frames. The images are loaded in alphabetical order, and the capture speed, pixel scale factor, and scale units are set for further processing.

**Arguments:**

| Name                   | Type  | Explanation                                                                                       | Optional | Default Value                             |
|------------------------|-------|---------------------------------------------------------------------------------------------------|----------|-------------------------------------------|
| `folder_path`          | `str` | The path to the folder containing the image files.                                              | No       | N/A                                       |
| `capture_speed_in_fps` | `int` | Frame capture speed for the image sequence.                                                     | Yes      | `DEFAULT_CAPTURE_SPEED_IN_FPS`            |
| `pixel_scale_factor`   | `float`| Conversion factor from pixels to physical units.                                                | Yes      | `DEFAULT_PIXEL_SCALE_FACTOR`              |
| `scale_units`          | `str` | Scale units corresponding to the pixel scale factor.                                            | Yes      | `DEFAULT_SCALE_UNITS`                     |

**Returns:**

- `list`: A list of loaded frames as NumPy arrays.

**Errors:**

- **`FileNotFoundError`**: Raised if the specified folder is not found.

---

### `set_properties(pixel_scale_factor: float = DEFAULT_PIXEL_SCALE_FACTOR, scale_units: str = DEFAULT_SCALE_UNITS, capture_speed_in_fps: int = None) -> None`

**Description:**  
Sets or updates the properties of the Capture object, including the pixel scale factor, scale units, and the capture speed (frames per second).

**Arguments:**

| Name                   | Type  | Explanation                                                        | Optional | Default Value                    |
|------------------------|-------|--------------------------------------------------------------------|----------|----------------------------------|
| `pixel_scale_factor`   | `float`| Conversion factor from pixels to physical units.                  | Yes      | `DEFAULT_PIXEL_SCALE_FACTOR`     |
| `scale_units`          | `str` | Units corresponding to the pixel scale factor.                    | Yes      | `DEFAULT_SCALE_UNITS`            |
| `capture_speed_in_fps` | `int` | Frame capture speed in frames per second.                         | Yes      | `DEFAULT_CAPTURE_SPEED_IN_FPS`   |

**Returns:**

- `None`

---

## Example Workflow

```python
# Initialize the Capture object (working directory defaults to 'input_files')
capture = Capture()

# Load a video file
video_path = capture.load_video("sample_video.mp4")

# Process the video into frames with a given pixel scale factor and scale units,
# and optionally store the frames in a folder named 'frames'
frames = capture.process_video_into_frames(
    pixel_scale_factor=0.166666,
    scale_units="µm",
    is_store_video_frames=True,
    store_images_path='frames'
)

# Retrieve captured frames
captured_frames = capture.get_captured_frames()

# Get the working directory
working_dir = capture.get_directory()
print("Working Directory:", working_dir)

# Retrieve frame rate information
frame_rate = capture.get_frame_rate()
print("Frame Rate:", frame_rate)

# Retrieve the pixel scale factor
scale_factor = capture.get_pixel_scale_factor()
print("Pixel Scale Factor:", scale_factor)

# Load images from a folder as frames (e.g., from a previously saved 'frames' folder)
frames_from_images = capture.load_images_as_frames(
    folder_path='frames',
    capture_speed_in_fps=15,
    pixel_scale_factor=0.166666,
    scale_units="µm"
)
```
