"""
Module to analyze particle motion and calculate speed distributions.
"""
import os
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from distfit import distfit
from tqdm import trange

from .track import Tracker  # type: ignore


class Stats:
    """
    Class to analyze particle motion and calculate speed distributions.
    """
    DEFAULT_DISTRIBUTION = 'norm'

    def __init__(self, tracker_object: Tracker) -> None:
        """
        Initializes the ParticleAnalyzer class.

        Args:
            sorted_dataframe (pd.DataFrame): The sorted DataFrame containing particle data.
            capture_speed_in_fps (float): The capture speed in frames per second.
            pixel_to_um (float): Conversion factor from pixels to micrometers.
        """
        self._parent = tracker_object
        self._sorted_dataframe = tracker_object._linked_particles_dataframes
        self._directory: str = tracker_object.get_directory()
        self._capture_speed_in_fps = tracker_object._parent._parent._actual_fps
        self.pixel_scale_factor: float = tracker_object._parent._parent.get_pixel_scale_factor()
        self._mean_array: List[float] = []

    def calculate_speed_and_plot_mean(self,
                                      distribution_type: str = DEFAULT_DISTRIBUTION,
                                      fit_range: tuple = None,
                                      ci_range: tuple = (5, 95),
                                      bin_size: int = 30,
                                      speed_unit: str = "µm/s") -> np.ndarray:
        """
        Calculate the mean speeds for each particle and plot their speed distributions.
        This version allows additional arguments to customize the distribution fitting and plotting.

        Args:
            distribution_type (str): Distribution type for fitting (default: 'norm').
            fit_range (tuple): User-defined speed range for fitting (default: None, uses confidence interval).
            ci_range (tuple): Confidence interval range for default speed limits (default: (5, 95)).
            bin_size (int): Number of bins for histogram (default: 30).
            speed_unit (str): Unit of speed to display on plots (default: "µm/s").

        Returns:
            np.ndarray: Array of mean speeds for each particle.
        """
        unique_particles = self._sorted_dataframe['particle'].unique()
        print(f'Total unique particles: {len(unique_particles)}')
        mean_array: List[float] = []

        # For each particle, compute speed and plot its distribution individually
        for idx in trange(len(unique_particles), desc='Calculating Speed'):
            each_particle = unique_particles[idx]
            current_particle = self.__get_particle_data(each_particle)
            speed = self.__calculate_speed(current_particle)
            # Updated call passes the additional arguments to the new fitting method.
            mean_speed = self.__fit_and_plot_speed_distribution(
                speed, each_particle, distribution_type=distribution_type,
                fit_range=fit_range, ci_range=ci_range,
                bin_size=bin_size, speed_unit=speed_unit
            )
            mean_array.append(mean_speed)

        self._mean_array: List[float] = mean_array
        return np.array(mean_array)

    def __get_particle_data(self, particle: int) -> pd.DataFrame:
        """
        Get data for a specific particle.

        Args:
            particle (int): The particle ID.

        Returns:
            pd.DataFrame: DataFrame containing data for the specified particle.
        """
        return self._sorted_dataframe.loc[self._sorted_dataframe['particle'] == particle, ['centroid_x', 'centroid_y', 'frame', 'particle']]

    def __calculate_speed(self, particle_data: pd.DataFrame) -> np.ndarray:
        """
        Calculate the speed of a particle.

        Args:
            particle_data (pd.DataFrame): DataFrame containing data for a particle.

        Returns:
            np.ndarray: Array of speeds for the particle.
        """
        # If there's only one row, speed can't be calculated, so return 0.0 for that single point.
        if len(particle_data) < 2:
            speed = np.array([0.0])
        else:
            x = particle_data['centroid_x'].to_numpy()
            y = particle_data['centroid_y'].to_numpy()
            x_diff = np.diff(x)
            y_diff = np.diff(y)
            distance = np.sqrt(x_diff**2 + y_diff**2)
            distance_in_um = distance * self.pixel_scale_factor
            time = particle_data['frame']
            time_diff = np.diff(time)
            time_in_seconds = time_diff / self._capture_speed_in_fps
            speed = distance_in_um / time_in_seconds

            # Append 0.0 for the last speed entry to match the length of the particle_data
            speed = np.append(speed, 0.0)

        # Assign the speed array back to the DataFrame
        particle_data['speed'] = speed
        return speed

    def __fit_and_plot_speed_distribution(
        self,
        speed: np.ndarray,
        particle: int,
        distribution_type: str = 'norm',
        fit_range: tuple = None,
        ci_range: tuple = (5, 95),
        bin_size: int = 30,
        speed_unit: str = "µm/s"
    ) -> float:
        """
        Fit the speed distribution within a user-defined range and plot the histogram and fitted distribution.

        Args:
            speed (np.ndarray): Array of speeds.
            particle (int): Particle ID.
            distribution_type (str): Distribution type for fitting (e.g., "norm", "expon", "gamma", etc.; default: 'norm').
            fit_range (tuple): User-defined speed range for fitting (default: None, uses CI).
            ci_range (tuple): Confidence interval range for selecting default speed limits (default: (5, 95)).
            bin_size (int): Number of bins for histogram (default: 30).
            speed_unit (str): Unit of speed to display on plots (default: "µm/s").

        Returns:
            float: Mean speed of the particle.
        """
        if len(speed) == 0:
            print(f"Particle {particle}: No speed data available.")
            return 0.0

        # Determine the fitting range: use user-defined range if provided; otherwise use the specified confidence interval.
        if fit_range:
            lower_bound, upper_bound = fit_range
        else:
            lower_bound, upper_bound = np.percentile(speed, ci_range)

        # Filter speed values within the selected range
        speed_filtered = speed[(speed >= lower_bound) & (speed <= upper_bound)]

        if len(speed_filtered) < 2:
            print(
                f"Particle {particle}: Not enough data points within selected range ({lower_bound}-{upper_bound} {speed_unit}).")
            return 0.0

        # Fit distribution only to the filtered speed values
        try:
            speed_distribution = distfit(distr=distribution_type, verbose=0)
            speed_distribution.fit_transform(speed_filtered, verbose=False)
            mean_speed = speed_distribution.model['loc']
        except Exception as e: # pylint: disable=broad-except
            print(
                f"Error fitting distribution '{distribution_type}' for particle {particle}: {e}")
            return 0.0

        # Create figure with two subplots: left for histogram, right for fitted distribution
        _, axes_local = plt.subplots(1, 2, figsize=(12, 5))

        # Left Plot: Histogram with full data and fit range highlighted
        ax_hist = axes_local[0]
        ax_hist.hist(speed, bins=bin_size, alpha=0.7,
                     color='black', label='Speed (Full Data)')
        ax_hist.axvline(lower_bound, color='gray', linestyle='dashed',
                        label=f'Lower Bound ({lower_bound} {speed_unit})')
        ax_hist.axvline(upper_bound, color='gray', linestyle='dashed',
                        label=f'Upper Bound ({upper_bound} {speed_unit})')
        ax_hist.set_title(
            f'Particle: {particle} - Speed Histogram (Full Data)')
        ax_hist.set_xlabel(f'Speed ({speed_unit})')
        ax_hist.set_ylabel('Frequency')
        ax_hist.legend()

        # Right Plot: Distribution fit for selected range, with mean speed labeled
        ax_dist = axes_local[1]
        speed_distribution.plot(ax=ax_dist)
        ax_dist.axvline(mean_speed, color='blue', linestyle='dashed', linewidth=2,
                        label=f'Mean Speed: {mean_speed:.2f} {speed_unit}')
        ax_dist.set_xlim(lower_bound, upper_bound)
        ax_dist.set_title(
            f'Particle: {particle} - {distribution_type.capitalize()} Fit')

        # Remove unwanted markers (e.g., "CII low/high") from the legend
        handles, labels = ax_dist.get_legend_handles_labels()
        new_handles_labels = [(h, l) for h, l in zip(
            handles, labels) if 'CII' not in l]
        if new_handles_labels:
            new_handles, new_labels = zip(*new_handles_labels)
            ax_dist.legend(new_handles, new_labels)

        plt.tight_layout()
        plt.show()

        return mean_speed

    @staticmethod
    # type: ignore
    def __hide_unused_subplots(fig: plt.Figure, axes: np.ndarray, start_idx: int) -> None:
        """
        Hide unused subplots.

        Args:
            fig (plt.Figure): Matplotlib figure object.
            axes (np.ndarray): Array of Matplotlib axes objects.
            start_idx (int): Starting index to hide subplots.

        Returns:
            None
        """
        for j in range(start_idx, len(axes)):
            fig.delaxes(axes[j])

    def plot_overall_mean_speed_distribution(self, bins: int = 10, speed_unit: str = "µm/s") -> None:
        """
        Plot the overall mean speed distribution.

        Args:
            bins (int): Number of bins for the histogram.
        Returns:
            None
        """
        # Normalize the overall distribution of mean_array
        _, ax = plt.subplots(figsize=(10, 6))
        mean_array = np.array(self._mean_array)
        ax.hist(mean_array, bins=bins, density=False,
                alpha=0.7, label='Mean Speeds')
        ax.set_title('Overall Mean Speed Distribution')
        ax.set_xlabel(f'Mean Speed {speed_unit}')
        ax.set_ylabel('Frequency')
        plt.show()

    def save_mean_speeds(self, filename: str) -> None:
        """
        Save the mean speeds to a CSV file.

        Args:
            filename (str): The filename to save the CSV file.

        Returns:
            None
        """
        mean_array = np.array(self._mean_array)
        mean_df = pd.DataFrame(mean_array, columns=['mean_speed'])
        save_file_path = os.path.join(
            self._directory, f'{filename}.csv')
        mean_df.to_csv(save_file_path, index=False)
        print(f'Mean speeds saved to {save_file_path}')
