# Capture Class Documentation

## Overview

The `Capture` class in the Microbe Vision package is responsible for loading video files or image sequences and converting them into frames for further processing.

## Workflow

![image](./images/capture.png)

## Class Attributes

| Attribute                           | Description                                                        | Default Value                                |
|-------------------------------------|--------------------------------------------------------------------|----------------------------------------------|
| `DEFAULT_FILE_DIRECTORY`            | Default directory for input files.                                 | `'input_files'`                              |
| `DEFAULT_STORE_IMAGE_FILE_DIRECTORY`| Default directory to store images from the video.                  | `'frames_from_video'`                        |
| `SUPPORTED_INPUT_VIDEO_FILE_TYPES`  | Supported video file types (`avi`, `mp4`, `mpg`, `mpeg`).          | `['avi', 'mp4', 'mpg', 'mpeg']`              |
| `DEFAULT_CAPTURE_SPEED_IN_FPS`      | Default capture speed in frames per second.                        | `15`                                         |
| `DEFAULT_PIXEL_TO_MICRON`           | Conversion factor from pixel to micron.                            | `0.166666666666666`                          |

## Methods

### `__init__`

**Description**:  
Initializes the `Capture` object with the specified working directory.

#### Arguments

| Name                | Type  | Explanation                                          | Optional | Default Value               |
|---------------------|-------|------------------------------------------------------|----------|-----------------------------|
| `working_directory` | `str` | The working directory for input files.               | Yes      | `DEFAULT_FILE_DIRECTORY`    |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `None` | The method does not return any value. |

---

### `load_video`

**Description**:  
Loads a video file and validates its path.

#### Arguments

| Name       | Type  | Explanation                                        | Optional | Default Value |
|------------|-------|----------------------------------------------------|----------|---------------|
| `file_name` | `str` | The name of the video file to load.                 | Yes      | `''`          |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `str` | The validated file path. |

#### Errors

- **`FileNotFoundError`**: Raised if the specified video file is not found.

---

### `process_video_into_frames`

**Description**:  
Processes the loaded video into frames and optionally stores them in a specified directory.

#### Arguments

| Name                  | Type  | Explanation                                                       | Optional | Default Value                              |
|-----------------------|-------|-------------------------------------------------------------------|----------|--------------------------------------------|
| `pixel_to_um`         | `float`| Conversion factor from pixels to micrometers.                     | No       | N/A                                        |
| `capture_speed_in_fps`| `int`  | Frame capture speed in frames per second.                         | Yes      | `DEFAULT_CAPTURE_SPEED_IN_FPS`             |
| `is_store_video_frames`| `bool`| Whether to store the extracted frames as images.                  | Yes      | `False`                                    |
| `store_images_path`   | `str`  | Directory path where frames should be stored if `is_store_video_frames` is `True`. | Yes      | `DEFAULT_STORE_IMAGE_FILE_DIRECTORY`       |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `list` | A list of captured frames as NumPy arrays. |

#### Errors

- **`ValueError`**: Raised if the `pixel_to_um` conversion factor is not provided.

---

### `get_captured_frames`

**Description**:  
Retrieves the frames captured from the video.

#### Arguments

| Name  | Type | Explanation | Optional | Default Value |
|-------|------|-------------|----------|---------------|
| None  | None | This method does not require any arguments. | N/A | N/A |

#### Returns

| Type   | Explanation  |
|--------|--------------|
| `list` | The list of captured frames as NumPy arrays. |

---

### `get_directory`

**Description**:  
Retrieves the working directory for the `Capture` object.

#### Arguments

| Name  | Type | Explanation | Optional | Default Value |
|-------|------|-------------|----------|---------------|
| None  | None | This method does not require any arguments. | N/A | N/A |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `str` | The working directory path. |

---

### `get_frame_rate`

**Description**:  
Retrieves the frame rate at which the video is processed.

#### Arguments

| Name  | Type | Explanation | Optional | Default Value |
|-------|------|-------------|----------|---------------|
| None  | None | This method does not require any arguments. | N/A | N/A |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `int` | The frame rate in frames per second. |

---

### `get_pixel_to_um`

**Description**:  
Retrieves the pixel-to-micron conversion factor.

#### Arguments

| Name  | Type | Explanation | Optional | Default Value |
|-------|------|-------------|----------|---------------|
| None  | None | This method does not require any arguments. | N/A | N/A |

#### Returns

| Type   | Explanation  |
|--------|--------------|
| `float` | The conversion factor from pixel to micron. |

---

### `load_images_as_frames`

**Description**:  
Loads images from a specified folder as frames.

#### Arguments

| Name                | Type  | Explanation                                                       | Optional | Default Value                             |
|---------------------|-------|-------------------------------------------------------------------|----------|-------------------------------------------|
| `folder_path`       | `str`  | Path to the folder containing the image files.                    | No       | N/A                                       |
| `capture_speed_in_fps` | `int` | Frame capture speed in frames per second for the image sequence. | Yes      | `DEFAULT_CAPTURE_SPEED_IN_FPS`            |
| `pixel_to_um`       | `float`| Conversion factor from pixels to micrometers.                     | Yes      | `DEFAULT_PIXEL_TO_MICRON`                 |

#### Returns

| Type   | Explanation  |
|--------|--------------|
| `list` | A list of loaded frames as NumPy arrays. |

#### Errors

- **`FileNotFoundError`**: Raised if the specified folder is not found.

---

## Example Workflow

```python
# Initialize the Capture object
capture = Capture()

# Load a video file
video_path = capture.load_video("sample_video.mp4")

# Process the video into frames
frames = capture.process_video_into_frames(pixel_to_um=0.166666, is_store_video_frames=True, store_images_path='frames')

# Retrieve captured frames
captured_frames = capture.get_captured_frames()

# Load images from a folder as frames
frames_from_images = capture.load_images_as_frames('frames', capture_speed_in_fps=15, pixel_to_um=0.166666)
```
