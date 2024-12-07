# Tracker Class Documentation

## Overview

The `Tracker` class in the RABiTPy package is responsible for tracking particles in 2D using the Trackpy library. It provides functionality for linking particles across frames, filtering trajectories, saving linked data, and plotting particle trajectories.

## Workflow

![image](./flow_charts/track.png)

## Class Attributes

| Attribute                | Description                                                    | Default Value        |
|--------------------------|----------------------------------------------------------------|----------------------|
| `DEFAULT_POSITION_COLUMNS` | Default position columns for particle tracking.                | `['centroid_x', 'centroid_y']` |

## Public Methods

### `__init__`

**Description**:  
Initializes the `Tracker` object with the specified `Identify` object, setting up the internal data structures for tracking particles.

#### Arguments

| Name              | Type      | Explanation                                              | Optional | Default Value |
|-------------------|-----------|----------------------------------------------------------|----------|---------------|
| `identify_object` | `Identify` | The `Identify` object used to retrieve region properties. | No       | N/A           |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `None` | The method does not return any value. |

#### Errors

- **`TypeError`**: Raised if `identify_object` is not provided or is not an instance of `Identify`.

---

### `link_particles`

**Description**:  
Links particles across frames based on their positions, using the Trackpy library.

#### Arguments

| Name              | Type        | Explanation                                                    | Optional | Default Value           |
|-------------------|-------------|----------------------------------------------------------------|----------|-------------------------|
| `max_distance`    | `float`     | Maximum distance a particle can move between frames.           | No       | N/A                     |
| `max_memory`      | `int`       | Maximum number of frames during which a particle can disappear. | No       | N/A                     |
| `position_columns`| `list[str]` | List containing column names for the x and y positions.        | Yes      | `['centroid_x', 'centroid_y']` |

#### Returns

| Type          | Explanation  |
|---------------|--------------|
| `pd.DataFrame` | DataFrame containing the linked particles. |

---

### `filter_particles`

**Description**:  
Filters particles based on the number of frames they are present in and their displacement.

#### Arguments

| Name                 | Type        | Explanation                                                   | Optional | Default Value |
|----------------------|-------------|---------------------------------------------------------------|----------|---------------|
| `min_frames`         | `int`       | Minimum number of frames a particle must be present in.       | No       | N/A           |
| `min_displacement`   | `float`     | Minimum displacement a particle must have to be retained.     | No       | N/A           |
| `is_update_particles`| `bool`      | Whether to update the internal data structure with the filtered particles. | Yes      | `True`        |

#### Returns

| Type          | Explanation  |
|---------------|--------------|
| `pd.DataFrame` | DataFrame containing the filtered particles. |

#### Errors

- **`ValueError`**: Raised if there are no linked dataframes available (i.e., if `link_particles` has not been called).

---

### `save_linked_dataframes`

**Description**:  
Saves the linked particles' DataFrame to a CSV file.

#### Arguments

| Name             | Type   | Explanation                                         | Optional | Default Value |
|------------------|--------|-----------------------------------------------------|----------|---------------|
| `output_file_name` | `str` | The name of the output CSV file.                    | No       | N/A           |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `None` | The method does not return any value. |

#### Errors

- **`ValueError`**: Raised if there are no linked dataframes available (i.e., if `link_particles` has not been called).

---

### `plot_trajectories_using_trackpy`

**Description**:  
Plots the trajectories of the linked particles using Trackpy.

#### Arguments

| Name  | Type | Explanation | Optional | Default Value |
|-------|------|-------------|----------|---------------|
| None  | None | This method does not require any arguments. | N/A | N/A |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `None` | The method does not return any value. |

#### Errors

- **`ValueError`**: Raised if there are no linked dataframes available (i.e., if `link_particles` has not been called).

---

### `sort_and_plot_scatter_of_trajectories`

**Description**:  
Sorts the linked particles' DataFrame and plots a scatter plot of their trajectories.

#### Arguments

| Name                 | Type  | Explanation                                                  | Optional | Default Value |
|----------------------|-------|--------------------------------------------------------------|----------|---------------|
| `is_update_particles`| `bool`| Whether to update the internal data structure with the sorted DataFrame. | Yes      | `True`        |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `None` | The method does not return any value. |

#### Errors

- **`ValueError`**: Raised if there are no linked dataframes available (i.e., if `link_particles` has not been called).

---

### `overlay_tracks_on_video`

**Description**:  
Overlays tracked particle trajectories onto the loaded video frames and saves the processed video. This method utilizes the video frames already loaded and processed by the `Capture` class, ensuring consistency in file paths and directories. It assigns unique colors to each particle using a specified colormap and draws their movement trajectories across the video frames.

#### Arguments

| Name                  | Type | Explanation                                                                                           | Optional | Default Value |
|-----------------------|------|-------------------------------------------------------------------------------------------------------|----------|---------------|
| `output_video_filename` | `str` | The name of the output video file where the trajectories will be overlaid.                           | No       | N/A           |
| `colormap_name`         | `str` | The name of the matplotlib colormap used to assign unique colors to each particle. Defaults to `"viridis"`. Matplotlib offers a variety of colormaps such as `"plasma"`, `"inferno"`, `"jet"`, etc. | Yes      | `"viridis"`   |
| `frame_index_offset`    | `int` | Adjusts frame indexing differences between tracking data and video frames. For example, if tracking data frames start at `1` and video frames start at `0`, an offset of `-1` aligns them correctly. Defaults to `-1`. | Yes      | `-1`          |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `None` | The method does not return any value. |

#### Errors

- **`ValueError`**:  
  - Raised if there are no captured frames available from the `Capture` class (i.e., if the video has not been loaded and processed correctly).
  - Raised if the tracking data is empty (i.e., if particles have not been linked using `link_particles`).

---

### `get_directory`

**Description**:  
Retrieves the working directory where output files will be stored.

#### Arguments

| Name  | Type | Explanation | Optional | Default Value |
|-------|------|-------------|----------|---------------|
| None  | None | This method does not require any arguments. | N/A | N/A |

#### Returns

| Type  | Explanation  |
|-------|--------------|
| `str` | The working directory path. |

---

## Example Workflow

```python
from tracker import Tracker

# Initialize the Tracker objects using previous made identify object
tracker = Tracker(identify_object=identify)

# Link particles
linked_particles = tracker.link_particles(max_distance=50, max_memory=50, position_columns=['centroid_x', 'centroid_y'])

# Filter particles based on presence in frames and displacement
filtered_particles = tracker.filter_particles(min_frames=500, min_displacement=10, is_update_particles=True)

# Save the linked DataFrame to a CSV file
tracker.save_linked_dataframes(output_file_name='Linked_Particles')

# Plot the trajectories of the linked particles
tracker.plot_trajectories_using_trackpy()

# Sort and plot a scatter plot of the trajectories
tracker.sort_and_plot_scatter_of_trajectories()

# Overlay tracks on video
output_video_filename = "Flavo_case_tracks_overlaid.avi"
tracker.overlay_tracks_on_video(
    output_video_filename=output_video_filename,
    colormap_name="viridis",
    frame_index_offset=-1  # Adjust based on your tracking data
)
```
