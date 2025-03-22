# Stats Class Documentation

## Overview

The `Stats` class is responsible for analyzing particle motion and calculating speed distributions. It extracts the linked particle data from a provided `Tracker` object, computes the speed of each particle, fits a distribution to the speed data, and offers methods for plotting and saving the results.

## Workflow

![Workflow Diagram](./flow_charts/stats.png)

1. **Initialization:**  
   The class is initialized with a `Tracker` object. It retrieves the linked particle DataFrame, working directory, capture speed, and pixel scale factor from the parent objects.
2. **Speed Calculation & Distribution Fitting:**  
   For each particle, the class calculates the instantaneous speeds from centroid changes between frames. A distribution (default is normal) is then fitted to the filtered speed data, and the mean speed is extracted.
3. **Visualization:**  
   Individual particle speed distributions are plotted with histograms and fitted curves. An overall histogram of mean speeds is also available.
4. **Data Saving:**  
   Calculated mean speeds can be saved to a CSV file for further analysis.

---

## Class Attributes

| Attribute              | Description                                                      | Default Value |
|------------------------|------------------------------------------------------------------|---------------|
| `DEFAULT_DISTRIBUTION` | The default distribution type used for fitting speed data.       | `'norm'`      |

---

## Public Methods

### `__init__(tracker_object: Tracker) -> None`

**Description:**  
Initializes the Stats instance with the specified `Tracker` object. The constructor retrieves the linked particle DataFrame, the working directory, the capture speed (in frames per second), and the pixel scale factor from the parent Capture object.

**Arguments:**

| Name             | Type      | Explanation                                                        | Optional | Default Value |
|------------------|-----------|--------------------------------------------------------------------|----------|---------------|
| `tracker_object` | `Tracker` | The Tracker object that provides the linked particle data.         | No       | N/A           |

**Returns:**

- `None`

---

### `calculate_speed_and_plot_mean(distribution_type: str = DEFAULT_DISTRIBUTION, fit_range: tuple = None, ci_range: tuple = (5, 95), bin_size: int = 30, speed_unit: str = "µm/s") -> np.ndarray`

**Description:**  
Calculates the speed for each particle and fits a distribution to the speed data. For every unique particle, the method:
- Extracts the particle’s trajectory data.
- Computes the instantaneous speeds.
- Filters the speeds within a specified range (either provided via `fit_range` or determined by the confidence interval `ci_range`).
- Fits the specified distribution (default is `'norm'`) using the `distfit` library.
- Plots two subplots: one showing a histogram of all speed data with the selected fit range highlighted, and another displaying the fitted distribution along with the computed mean speed.

**Arguments:**

| Name                | Type    | Explanation                                                                                                    | Optional | Default Value       |
|---------------------|---------|----------------------------------------------------------------------------------------------------------------|----------|---------------------|
| `distribution_type` | `str`   | Distribution type for fitting (e.g., `'norm'`, `'expon'`, `'gamma'`).                                          | Yes      | `'norm'`            |
| `fit_range`         | `tuple` | User-defined speed range for fitting. If not provided, the method uses the percentile values defined by `ci_range`. | Yes      | `None`              |
| `ci_range`          | `tuple` | Confidence interval range (in percentiles) used to determine the default fitting range when `fit_range` is not provided. | Yes      | `(5, 95)`           |
| `bin_size`          | `int`   | Number of bins to use for the histogram.                                                                      | Yes      | `30`                |
| `speed_unit`        | `str`   | The unit of speed for labeling plots (e.g., "µm/s").                                                           | Yes      | `"µm/s"`            |

**Returns:**

- `np.ndarray`: Array of mean speeds for each particle.

---

### `plot_overall_mean_speed_distribution(bins: int = 10, speed_unit: str = "µm/s") -> None`

**Description:**  
Plots a histogram of the overall mean speeds calculated for all particles.

**Arguments:**

| Name         | Type   | Explanation                                          | Optional | Default Value |
|--------------|--------|------------------------------------------------------|----------|---------------|
| `bins`       | `int`  | Number of bins for the histogram.                    | Yes      | `10`          |
| `speed_unit` | `str`  | Unit of speed to label the x-axis (e.g., "µm/s").      | Yes      | `"µm/s"`      |

**Returns:**

- `None`

---

### `save_mean_speeds(filename: str) -> None`

**Description:**  
Saves the calculated mean speeds (stored internally) to a CSV file in the working directory.  
- The output CSV file will have one column labeled `mean_speed`.

**Arguments:**

| Name      | Type  | Explanation                                              | Optional | Default Value |
|-----------|-------|----------------------------------------------------------|----------|---------------|
| `filename`| `str` | The base name for the output CSV file.                 | No       | N/A           |

**Returns:**

- `None`

---

## Example Workflow

```python
from stats import Stats

# Initialize the Stats object using an existing Tracker object
stats = Stats(tracker_object=tracker)

# Calculate and plot mean speeds for each particle using a normal distribution fit
mean_speeds = stats.calculate_speed_and_plot_mean(
    distribution_type='norm',
    fit_range=None,        # Use the confidence interval to determine the fitting range
    ci_range=(5, 95),
    bin_size=30,
    speed_unit="µm/s"
)

# Plot the overall mean speed distribution across all particles
stats.plot_overall_mean_speed_distribution(bins=10, speed_unit="µm/s")

# Save the calculated mean speeds to a CSV file named 'mean_speeds'
stats.save_mean_speeds(filename='mean_speeds')
```
