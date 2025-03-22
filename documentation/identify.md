# Identify Class Documentation

## Overview

The `Identify` class is designed to perform object identification on frames using a variety of thresholding techniques and advanced segmentation with the Omnipose model. In addition to standard grayscale thresholding, it offers multiple algorithm-based methods (including adaptive and Gaussian methods) and tools for refining object centroids using 2D Gaussian fits. The class works in tandem with a provided `Capture` object that supplies video frames and related metadata.

## Workflow

![Workflow Diagram](./flow_charts/identify.png)

1. **Initialization:** An instance is created using a `Capture` object. The captured frames, working frames, and working directory are stored internally.
2. **Thresholding:** Multiple methods allow for thresholding of frames:
   - **Grayscale thresholding:** Converts frames to grayscale, inverts them, and applies a threshold.
   - **Algorithm-based thresholding:** Uses methods such as Otsu, isodata, li, and others from scikit-image.
   - **Adaptive thresholding:** Uses Gaussian adaptive thresholding.
   - **Color inversion:** Inverts frame colors if needed.
3. **Region Properties:** Labeled regions are analyzed to generate a dataframe of properties (such as area and centroid coordinates).
4. **Filtering:** The generated region properties can be filtered based on user-defined criteria.
5. **Omnipose Segmentation:** Optionally, an Omnipose model can be initialized and applied to segment objects on normalized frames.
6. **Centroid Refinement:** Gaussian fit methods are available to refine the detected centroids.
7. **Visualization & Export:** Methods are provided to display frames, plot centroids, visualize Gaussian fits, and save results to CSV.

---

## Methods

### `__init__(capture_frame_object: Capture)`

**Description:**  
Initializes the Identify instance with the provided `Capture` object.

**Arguments:**

| Name                   | Type      | Explanation                                                   | Optional | Default Value |
|------------------------|-----------|---------------------------------------------------------------|----------|---------------|
| `capture_frame_object` | `Capture` | The Capture object containing frames and metadata to process. | No       | N/A           |

**Errors:**

- **`TypeError`**: Raised if `capture_frame_object` is not an instance of `Capture`.

---

### `show_frames(images_to_show_count: int = 5, images_per_row: int = 5, use_gray_cmap: bool = False, image_size: tuple = (5, 5)) -> None`

**Description:**  
Displays a subset of the working frames in a grid. Frames are selected at equidistant intervals.

**Arguments:**

| Name                    | Type   | Explanation                                                          | Optional | Default Value |
|-------------------------|--------|----------------------------------------------------------------------|----------|---------------|
| `images_to_show_count`  | `int`  | Number of frames to display.                                         | Yes      | `5`           |
| `images_per_row`        | `int`  | Number of images per row in the display grid.                        | Yes      | `5`           |
| `use_gray_cmap`         | `bool` | Whether to display images using a grayscale colormap.                | Yes      | `False`       |
| `image_size`            | `tuple`| Size (width, height) for each image plot.                            | Yes      | `(5, 5)`      |

**Returns:**

- `None`

**Errors:**

- **`ValueError`**: Raised if `images_to_show_count` exceeds the total number of frames or if `images_per_row` is less than or equal to zero.

---

### `apply_grayscale_thresholding(threshold: float = 0.5, is_update_frames: bool = True) -> List`

**Description:**  
Converts each captured frame to grayscale, inverts the grayscale image, and applies a binary threshold.  
**Note:** The threshold value must be between 0 and 1.

**Arguments:**

| Name               | Type    | Explanation                                                       | Optional | Default Value |
|--------------------|---------|-------------------------------------------------------------------|----------|---------------|
| `threshold`        | `float` | The threshold value for binarization (expected range: 0–1).        | Yes      | `0.5`         |
| `is_update_frames` | `bool`  | Whether to update the internal working frames with the thresholded images. | Yes      | `True`        |

**Returns:**

- `List`: The list of updated (binary) frames.

**Errors:**

- **`ValueError`**: Raised if the threshold value is not within the range [0, 1].

---

### `try_all_algorithm_based_thresholding(frame_index: int = 0) -> None`

**Description:**  
Applies a set of thresholding algorithms (isodata, li, mean, minimum, otsu, triangle, yen) from scikit-image to a specified frame for comparison purposes.

**Arguments:**

| Name         | Type | Explanation                                         | Optional | Default Value |
|--------------|------|-----------------------------------------------------|----------|---------------|
| `frame_index`| `int`| Index of the frame to which the algorithms are applied. | Yes      | `0`           |

**Returns:**

- `None`

---

### `apply_algorithm_based_thresholding(algorithm: str = 'otsu', is_color_inverse: bool = False, is_update_frames: bool = True, **kwargs) -> List`

**Description:**  
Applies a specified thresholding algorithm to all captured frames. Supports algorithms such as 'otsu', 'isodata', 'li', 'mean', 'minimum', 'triangle', and 'yen'. Optionally inverts colors before thresholding.

**Arguments:**

| Name              | Type   | Explanation                                                                  | Optional | Default Value |
|-------------------|--------|------------------------------------------------------------------------------|----------|---------------|
| `algorithm`       | `str`  | The thresholding algorithm to use (e.g., 'otsu').                            | Yes      | `'otsu'`      |
| `is_color_inverse`| `bool` | If True, inverts the grayscale image before applying thresholding.           | Yes      | `False`       |
| `is_update_frames`| `bool` | Whether to update the working frames with the thresholded results.           | Yes      | `True`        |
| `**kwargs`        |        | Additional keyword arguments for the selected thresholding function.         | -        | -             |

**Returns:**

- `List`: The updated list of thresholded frames.

**Errors:**

- **`ValueError`**: Raised if the specified algorithm is not recognized.

---

### `apply_gaussian_adaptive_thresholding(block_size: int = 11, c: int = 2, is_color_inverse: bool = False, is_update_frames: bool = True) -> List`

**Description:**  
Applies Gaussian adaptive thresholding to each captured frame.  
**Note:** Inversion can be applied if dark objects are displayed on a light background.

**Arguments:**

| Name               | Type   | Explanation                                                       | Optional | Default Value |
|--------------------|--------|-------------------------------------------------------------------|----------|---------------|
| `block_size`       | `int`  | Size of the block used for adaptive thresholding.                 | Yes      | `11`          |
| `c`                | `int`  | Constant subtracted from the mean within each block.              | Yes      | `2`           |
| `is_color_inverse` | `bool` | Whether to invert the binary image after thresholding.            | Yes      | `False`       |
| `is_update_frames` | `bool` | Whether to update the internal frames with the thresholded images.  | Yes      | `True`        |

**Returns:**

- `List`: The updated list of thresholded frames.

---

### `apply_color_inverse(is_update_frames: bool = True) -> List`

**Description:**  
Applies color inversion to each captured frame using a bitwise NOT operation.

**Arguments:**

| Name               | Type   | Explanation                                                       | Optional | Default Value |
|--------------------|--------|-------------------------------------------------------------------|----------|---------------|
| `is_update_frames` | `bool` | Whether to update the working frames with the inverted images.    | Yes      | `True`        |

**Returns:**

- `List`: The list of color-inverted frames.

---

### `generate_region_props_to_dataframe(view_props: List[AvailableProps]) -> pd.DataFrame`

**Description:**  
Generates a dataframe containing region properties for each working frame. For each frame, connected regions are labeled and properties (as specified by `view_props`) are computed and compiled into a single dataframe with an added `frame` column.

**Arguments:**

| Name       | Type                   | Explanation                                                     | Optional | Default Value |
|------------|------------------------|-----------------------------------------------------------------|----------|---------------|
| `view_props` | `List[AvailableProps]` | List of properties (e.g., `AREA`, `CENTROID`) to extract from each region. | No       | N/A           |

**Returns:**

- `pd.DataFrame`: Dataframe with region properties for all frames.

**Errors:**

- **`ValueError`**: Raised if `view_props` is None or empty.

---

### `apply_filters_on_region_props(props_threshold: List[PropsThreshold], is_update_dataframes: bool = True) -> pd.DataFrame`

**Description:**  
Filters the region properties dataframe based on a list of threshold conditions. Each condition specifies a property, an operation (greater than, less than, or equals), and a threshold value.

**Arguments:**

| Name                  | Type              | Explanation                                                      | Optional | Default Value |
|-----------------------|-------------------|------------------------------------------------------------------|----------|---------------|
| `props_threshold`     | `List[PropsThreshold]` | List of threshold conditions to apply.                           | No       | N/A           |
| `is_update_dataframes`| `bool`            | Whether to update the internal dataframe with the filtered data. | Yes      | `True`        |

**Returns:**

- `pd.DataFrame`: The filtered region properties dataframe.

---

### `get_possible_omnipose_model_names() -> List[str]`

**Description:**  
Retrieves the list of available Omnipose model names from the underlying model library.

**Returns:**

- `List[str]`: The list of possible Omnipose model names.

---

### `initialize_omnipose_model(model_name: str = 'bact_phase_omni', use_gpu: bool = False, params: dict = OMNIPOSE_DEFAULT_PARAMS) -> None`

**Description:**  
Initializes the Omnipose segmentation model using the specified model name and parameters.  
- Optionally activates GPU support if `use_gpu` is True.
- Prepares the working frames by normalizing them before segmentation.

**Arguments:**

| Name        | Type   | Explanation                                                   | Optional | Default Value              |
|-------------|--------|---------------------------------------------------------------|----------|----------------------------|
| `model_name`| `str`  | The Omnipose model name to use.                               | Yes      | `'bact_phase_omni'`        |
| `use_gpu`   | `bool` | Whether to enable GPU for the model processing.               | Yes      | `False`                    |
| `params`    | `dict` | Parameters for the Omnipose model (default settings provided by `OMNIPOSE_DEFAULT_PARAMS`). | Yes      | `OMNIPOSE_DEFAULT_PARAMS`  |

**Returns:**

- `None`

---

### `apply_omnipose_masking(batch_size: int = 50, save_masks: bool = False, masks_store_path: str = 'masks', is_update_frames: bool = True) -> List`

**Description:**  
Segments objects in the normalized frames using the previously initialized Omnipose model.  
- Processes frames in batches.
- Optionally saves the generated masks to a specified folder.
- Can update the internal working frames with the mask results.

**Arguments:**

| Name               | Type   | Explanation                                                        | Optional | Default Value |
|--------------------|--------|--------------------------------------------------------------------|----------|---------------|
| `batch_size`       | `int`  | Number of frames to process per batch during segmentation.         | Yes      | `50`          |
| `save_masks`       | `bool` | Whether to save the generated mask images to disk.                 | Yes      | `False`       |
| `masks_store_path` | `str`  | Directory path where masks should be saved.                        | Yes      | `'masks'`     |
| `is_update_frames` | `bool` | Whether to update the working frames with the segmentation masks.  | Yes      | `True`        |

**Returns:**

- `List`: List of segmented mask images.

**Errors:**

- **`ValueError`**: Raised if the Omnipose model has not been initialized.

---

### `plot_centroids(show_time: bool = False) -> None`

**Description:**  
Plots a scatter plot of object centroids extracted from the region properties dataframe.  
- If `show_time` is True, the centroids are colored according to the frame number and a color bar is displayed.

**Arguments:**

| Name       | Type   | Explanation                                          | Optional | Default Value |
|------------|--------|------------------------------------------------------|----------|---------------|
| `show_time`| `bool` | Whether to include frame number information via color mapping. | Yes      | `False`       |

**Returns:**

- `None`

---

### `save_identified_objects_to_csv(output_file_name: str = 'identified_objects') -> None`

**Description:**  
Saves the current region properties dataframe (which includes object properties such as area and centroid) to a CSV file.  
- Additional columns (`new_x` and `new_y`) are created by swapping the centroid coordinates.

**Arguments:**

| Name                | Type   | Explanation                                          | Optional | Default Value            |
|---------------------|--------|------------------------------------------------------|----------|--------------------------|
| `output_file_name`  | `str`  | Base name for the CSV file (saved in the working directory). | Yes      | `'identified_objects'`   |

**Returns:**

- `None`

---

### `get_region_props_dataframe() -> pd.DataFrame`

**Description:**  
Returns the internal region properties dataframe that contains the computed properties for each identified region.

**Returns:**

- `pd.DataFrame`: The region properties dataframe.

---

### `get_directory() -> str`

**Description:**  
Retrieves the working directory path used for storing files and outputs.

**Returns:**

- `str`: The working directory path.

---

## Gaussian Fit Methods

These methods refine the detected centroids using a 2D Gaussian fit applied on sub-images around each centroid.

### `visualize_gaussian_fit_on_a_frame(frame_index: int, fit_window: int = 7) -> None`

**Description:**  
Visualizes the Gaussian fitting process on a specified frame.  
- Plots both the initial centroids (blue circles) and the refined centroids (green stars) after performing a 2D Gaussian fit on sub-images.

**Arguments:**

| Name         | Type | Explanation                                                  | Optional | Default Value |
|--------------|------|--------------------------------------------------------------|----------|---------------|
| `frame_index`| `int`| Index of the frame to visualize (1-indexed).                 | No       | N/A           |
| `fit_window` | `int`| Half-size of the window used for the Gaussian fit.           | Yes      | `7`           |

**Returns:**

- `None`

---

### `optimize_centroids_using_gaussian_fit(fit_window: int = 7, max_workers: int = None) -> None`

**Description:**  
Optimizes centroid coordinates in the internal region properties dataframe by applying a 2D Gaussian fit on a sub-image around each centroid.  
- Uses parallel processing (via ThreadPoolExecutor) to process frames concurrently.
- Updates the region properties with refined centroid coordinates if the refined position is within acceptable bounds.

**Arguments:**

| Name          | Type | Explanation                                                  | Optional | Default Value |
|---------------|------|--------------------------------------------------------------|----------|---------------|
| `fit_window`  | `int`| Half-size of the window for the Gaussian fit.                | Yes      | `7`           |
| `max_workers` | `int`| Maximum number of threads to use; if None, a default is chosen.| Yes      | `None`        |

**Returns:**

- `None`

---

## PropsThreshold Structure

The `PropsThreshold` is a dictionary used to specify filtering conditions on the region properties. It includes:

| Key         | Description                                               | Type                   | Example Value                                  |
|-------------|-----------------------------------------------------------|------------------------|------------------------------------------------|
| `property`  | The property to filter on (from the AvailableProps enum). | `AvailableProps`       | `AvailableProps.AREA`                          |
| `operation` | The comparison operation (from AvailableOperations enum).  | `AvailableOperations`  | `AvailableOperations.GREATER_THAN`             |
| `value`     | The threshold value to compare against.                 | `int`, `float`, or `str` | `100`                                          |

**Example:**

```python
from constants import AvailableProps, AvailableOperations

threshold = {
    "property": AvailableProps.AREA,
    "operation": AvailableOperations.GREATER_THAN,
    "value": 100
}
```

This example filters objects based on their `AREA`, keeping only those with an area greater than 100.

## Enums for `PropsThreshold`

### AvailableProps

The `AvailableProps` enum provides different properties that can be used for filtering in the `PropsThreshold` structure.

| Enum Value            | Description                                |
|-----------------------|--------------------------------------------|
| `AREA`                | The area of the object.                    |
| `PERIMETER`           | The perimeter of the object.               |
| `CENTROID`            | The centroid (x, y coordinates) of the object. |
| `MAJOR_AXIS_LENGTH`   | The length of the major axis of the object.|
| `MINOR_AXIS_LENGTH`   | The length of the minor axis of the object.|
| `ECCENTRICITY`        | The eccentricity of the object.            |

### AvailableOperations

The `AvailableOperations` enum defines the comparison operations that can be applied in the `PropsThreshold`.

| Enum Value            | Description                                |
|-----------------------|--------------------------------------------|
| `GREATER_THAN`        | Checks if the property value is greater than the specified threshold. |
| `LESS_THAN`           | Checks if the property value is less than the specified threshold. |
| `EQUALS`              | Checks if the property value is equal to the specified threshold. |

### Example of Using Multiple `PropsThreshold`

You can use multiple thresholds to filter based on various properties:

```python
from constants import AvailableProps, AvailableOperations

thresholds = [
    {
        "property": AvailableProps.AREA,
        "operation": AvailableOperations.GREATER_THAN,
        "value": 100
    },
    {
        "property": AvailableProps.PERIMETER,
        "operation": AvailableOperations.LESS_THAN,
        "value": 50
    }
]
```

In this example, objects are filtered to include those with an area greater than 100 and a perimeter less than 50.

---

## Example Workflow

```python
from capture import Capture
from identify import Identify
from constants import AvailableProps, AvailableOperations

# Initialize Capture and load/process video frames
capture = Capture(working_directory='input_files')
capture.load_video('sample_video.mp4')
frames = capture.process_video_into_frames()

# Create an Identify instance with the Capture object
identify = Identify(capture)

# Display a few frames
identify.show_frames(images_to_show_count=3, images_per_row=3, use_gray_cmap=True)

# Apply grayscale thresholding (threshold value between 0 and 1)
thresholded_frames = identify.apply_grayscale_thresholding(threshold=0.5, is_update_frames=True)
identify.show_frames(images_to_show_count=3, images_per_row=3, use_gray_cmap=True)

# Alternatively, try various algorithm-based thresholding methods on the first frame
identify.try_all_algorithm_based_thresholding(frame_index=0)

# Generate region properties dataframe using selected view properties
view_props = [AvailableProps.LABEL, AvailableProps.AREA, AvailableProps.CENTROID]
region_props_df = identify.generate_region_props_to_dataframe(view_props)

# Apply filters on region properties
props_threshold = [
    {"property": AvailableProps.AREA, "operation": AvailableOperations.GREATER_THAN, "value": 100},
    {"property": AvailableProps.AREA, "operation": AvailableOperations.LESS_THAN, "value": 500}
]
filtered_df = identify.apply_filters_on_region_props(props_threshold)

# Initialize the Omnipose model and segment objects
identify.initialize_omnipose_model(model_name='bact_phase_omni', use_gpu=True)
masks = identify.apply_omnipose_masking(batch_size=50, save_masks=True, masks_store_path='masks', is_update_frames=True)

# Plot centroids of identified objects
identify.plot_centroids(show_time=True)

# Optimize centroids using Gaussian fitting across frames
identify.optimize_centroids_using_gaussian_fit(fit_window=7)

# Visualize Gaussian fit on a specific frame
identify.visualize_gaussian_fit_on_a_frame(frame_index=1, fit_window=7)

# Save the identified objects and their properties to CSV
identify.save_identified_objects_to_csv(output_file_name='identified_objects')
```
