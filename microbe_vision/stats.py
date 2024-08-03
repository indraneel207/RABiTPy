"""
Module to analyze particle motion and calculate speed distributions.
"""
import os
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from distfit import distfit

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
        self._capture_speed_in_fps = tracker_object._parent._parent.get_frame_rate()
        self._pixel_to_um: float = tracker_object._parent._parent.get_pixel_to_um()
        self._mean_array: List[float] = []

    def calculate_and_plot_mean(self, plots_per_row: int = 4, distribution_type: any = DEFAULT_DISTRIBUTION) -> np.ndarray:
        """
        Calculate the mean array of speeds for each particle and plot the distributions.

        Args:
            plots_per_row (int): Number of plots per row in the grid.
            distribution_type (any): Distribution to fit. Default is 'norm'. 
                Check distfit documentation for more options here: https://erdogant.github.io/distfit/pages/html/Parametric.html#distributions

        Returns:
            np.ndarray: Array of mean speeds for each particle.
        """
        unique_particles = self._sorted_dataframe['particle'].unique()
        print(f'Total unique particles: {len(unique_particles)}')
        mean_array: List[float] = []

        total_particles = len(unique_particles)
        # Calculate number of rows needed
        rows = (total_particles + plots_per_row - 1) // plots_per_row

        fig, axes = plt.subplots(rows * 2, plots_per_row, figsize=(20, rows * 10))
        axes = axes.flatten()  # Flatten the 2D array of axes for easy iteration

        for idx, each_particle in enumerate(unique_particles):
            current_particle = self.__get_particle_data(each_particle)
            speed = self.__calculate_speed(current_particle)
            mean_speed = self.__fit_and_plot_speed_distribution(
                axes, idx, speed, each_particle, distribution_type=distribution_type)
            mean_array.append(mean_speed)

        # Hide any unused subplots
        self.__hide_unused_subplots(fig, axes, idx * 2 + 2)
        plt.tight_layout()
        plt.show()

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
        x = particle_data['centroid_x'].to_numpy()
        y = particle_data['centroid_y'].to_numpy()
        x_diff = np.diff(x)
        y_diff = np.diff(y)
        distance = np.sqrt(x_diff**2 + y_diff**2)
        distance_in_um = distance * self._pixel_to_um
        time = particle_data['frame']
        time_diff = np.diff(time)
        time_in_seconds = time_diff / self._capture_speed_in_fps
        speed = distance_in_um / time_in_seconds
        particle_data['speed'] = np.append(speed, 0)
        return speed

    def __fit_and_plot_speed_distribution(self, axes: np.ndarray, idx: int, speed: np.ndarray, particle: int, distribution_type: any = DEFAULT_DISTRIBUTION) -> float:
        """
        Fit the speed distribution and plot the histogram and distribution.

        Args:
            ax (plt.Axes): Matplotlib axes object to plot on.
            speed (np.ndarray): Array of speeds.
            particle (int): Particle ID.
            distr (any): Distribution to fit.

        Returns:
            float: Mean speed of the particle.
        """
        speed_distribution = distfit(distr=distribution_type)
        speed_distribution.fit_transform(speed)
        mean_speed = speed_distribution.model['loc']

        # Plot the histogram
        ax_hist = axes[idx * 2]
        ax_hist.hist(speed, bins=30, alpha=0.7, label='Speed')
        ax_hist.set_title(f'Particle: {particle} - Speed Histogram')
        ax_hist.legend()
        
        # Plot the distribution
        ax_dist = axes[idx * 2 + 1]
        speed_distribution.plot(ax=ax_dist)
        ax_dist.set_title(f'Particle: {particle} - Fitted Distribution')

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

    def plot_overall_mean_speed_distribution(self, distribution_type: any = DEFAULT_DISTRIBUTION) -> None:
        """
        Plot the overall mean speed distribution.

        Args:
            mean_array (np.ndarray): Array of mean speeds for each particle.

        Returns:
            None
        """
        # Normalize the overall distribution of mean_array
        fig, ax = plt.subplots(figsize=(10, 6))
        mean_array = np.array(self._mean_array)
        mean_distribution = distfit(distr=distribution_type)
        mean_distribution.fit_transform(mean_array)
        
        mean_distribution.plot(ax=ax)
        ax.hist(mean_array, bins='auto', density=True,
                 alpha=0.7, label='Mean Speeds')
        ax.set_title('Overall Mean Speed Distribution')
        ax.legend()
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
