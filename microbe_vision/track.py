"""
Module for tracking particles in 2D using trackpy.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import trackpy as tp

from .identify import Identify


class Tracker:
    """
    Class for tracking particles in 2D using trackpy.
    """
    DEFAULT_POSITION_COLUMNS: list[str] = [
        'centroid_x', 'centroid_y']  # Default position columns

    def __init__(self, identify_object: Identify) -> None:
        """
        Initialize the Tracker object.
        """
        if not isinstance(identify_object, Identify):
            raise TypeError(
                "Identify_object must be provided and should be an instance of Identify.")

        self._parent = identify_object
        self._region_props_dataframe: pd.DataFrame = identify_object.get_region_props_dataframe()
        self._directory: str = identify_object.get_directory()
        self._linked_particles_dataframes: pd.DataFrame = pd.DataFrame()
        self._position_columns: list[str] = self.DEFAULT_POSITION_COLUMNS

    def link_particles(self, max_distance: float, max_memory: int, position_columns: list[str]) -> pd.DataFrame:
        """
        Link particles in a DataFrame.

        Args:
            max_distance (float): Maximum distance features can move between frames.
            max_memory (int): Maximum number of frames during which a feature can vanish.
            position_columns (List[str]): List containing the column names for the x and y positions. Default is ['centroid_x', 'centroid_y'].

        Returns:
            pd.DataFrame: DataFrame containing the linked particles.
        """
        if position_columns:
            self._position_columns = position_columns

        linked_dataframe = tp.link_df(self._region_props_dataframe, search_range=max_distance,
                                      memory=max_memory, pos_columns=self._position_columns)
        self._linked_particles_dataframes = linked_dataframe
        particle_count = linked_dataframe['particle'].nunique()
        print(f'Successfully linked {particle_count} particles.')
        return linked_dataframe

    def filter_particles(self, min_frames: int, min_displacement: float, is_update_particles: bool = True) -> pd.DataFrame:
        """
        Filter particles based on the number of frames they are present in and their displacement.
        Args:
            min_frames (int): Minimum number of frames a particle must be present in to be kept.
            min_displacement (float): Minimum displacement a particle must have to be kept. Default is 10.0.
        Returns:
            pd.DataFrame: DataFrame containing the filtered particles.
        """
        if self._linked_particles_dataframes.empty:
            raise ValueError(
                "No linked dataframes available. Please link particles first.")

        # Filtering the stubs with less than 500 frames
        filtered_dataframe = tp.filter_stubs(
            self._linked_particles_dataframes, threshold=min_frames)
        particle_count_after_filtering = filtered_dataframe['particle'].nunique(
        )
        print(
            f'After filtering based on min {min_frames} frames: {particle_count_after_filtering} unique particles')

        # Filtering the particles based on the displacement
        particle_displacements = filtered_dataframe.groupby('particle').apply(
            lambda group: np.sqrt(
                (group[self._position_columns[0]].iloc[-1] - group[self._position_columns[0]].iloc[0])**2 +
                (group[self._position_columns[1]].iloc[-1] -
                 group[self._position_columns[1]].iloc[0])**2
            )
        )
        displacement_filtered = particle_displacements[particle_displacements >
                                                       min_displacement].index
        result_dataframe = filtered_dataframe[filtered_dataframe['particle'].isin(
            displacement_filtered)]

        if is_update_particles:
            self._linked_particles_dataframes = result_dataframe

        particle_count_after_displacement_filtering = result_dataframe['particle'].nunique(
        )
        print(
            f'After filtering based on min {min_displacement} displacement filtering: {particle_count_after_displacement_filtering} unique particles')

        return result_dataframe

    def save_linked_dataframes(self, output_file_name: str) -> None:
        """
        Save the linked dataframes to a CSV file.
        Args:
            output_path (str): Path to the output file Eg. 'Linked Dataframe' to get a 'Linked Dataframe.csv' file.
        """
        if self._linked_particles_dataframes.empty:
            raise ValueError(
                "No linked dataframes available. Please link particles first.")

        output_path = os.path.join(self._directory, f'{output_file_name}.csv')
        self._linked_particles_dataframes.to_csv(output_path, index=False)
        print(f'Linked dataframes saved to {output_path}')

    def plot_trajectories_using_trackpy(self) -> None:
        """
        Plot the trajectories of the linked particles.
        Args:
            output_path (str): Path to the output file Eg. 'Trajectories' to get a 'Trajectories.png' file.
        """
        if self._linked_particles_dataframes.empty:
            raise ValueError(
                "No linked dataframes available. Please link particles first.")

        plt.figure(figsize=(12, 6))
        tp.plot_traj(self._linked_particles_dataframes,
                     pos_columns=self._position_columns[::-1])
        print('Trajectories plotted successfully.')

    def sort_and_plot_scatter_of_trajectories(self, is_update_particles: bool = True) -> None:
        """
        Plot a scatter plot of the trajectories.
        """
        plt.figure(figsize=(12, 6))
        # Observe the x and y axis are swapped
        cols = ['centroid_x', 'centroid_y', 'frame', 'particle']
        sort_by = ['particle', 'frame']
        sorted_dataframe = self.__shape_and_sort_dataframe(
            self._linked_particles_dataframes, cols, sort_by)

        if is_update_particles:
            self._linked_particles_dataframes = sorted_dataframe

        sns.scatterplot(data=sorted_dataframe, x='centroid_y',
                        y='centroid_x', hue='particle', palette='bright', s=8)
        plt.gca().invert_yaxis()
        plt.gca().set_title('Scatter plot of the trajectories')
        plt.legend(title='Particle ID', bbox_to_anchor=(
            1.05, 1), loc='upper left', borderaxespad=0.)
        plt.show()

    def visualize_particle_trajectories_from_origin(self, show_axes: bool = True):
        """
        Visualize the trajectories of particles initiated from the origin.
        args:
            show_axes: bool: Whether to show the axes lines at the origin to create quadrants.
        returns:
            None
        """
        df = self._linked_particles_dataframes

        # Initialize a new DataFrame to hold the shifted centroids
        shifted_df = pd.DataFrame()

        # Shift centroids so that each particle starts from the origin (0, 0)
        for particle_id in df['particle'].unique():
            # Create a copy of the particle's data to avoid SettingWithCopyWarning
            particle_data = df[df['particle'] == particle_id].copy()

            # Shift the centroids
            particle_data['shifted_centroid_x'] = particle_data['centroid_x'] - \
                particle_data['centroid_x'].iloc[0]
            particle_data['shifted_centroid_y'] = particle_data['centroid_y'] - \
                particle_data['centroid_y'].iloc[0]

            # Append to the shifted_df DataFrame
            shifted_df = pd.concat(
                [shifted_df, particle_data], ignore_index=True)

        sns.scatterplot(data=shifted_df, x='shifted_centroid_y',
                        y='shifted_centroid_x', hue='particle', palette='bright', s=50)

        # Connect the points to show the track
        for particle_id in shifted_df['particle'].unique():
            particle_data = shifted_df[shifted_df['particle'] == particle_id]
            plt.plot(particle_data['shifted_centroid_y'],
                     particle_data['shifted_centroid_x'])

        # Invert the y-axis
        plt.gca().invert_yaxis()

        # Set the title
        plt.gca().set_title('Trajectories of Particles initiated from Origin')

        if show_axes:
            # Draw the axes lines at the origin to create quadrants
            plt.axhline(0, color='black', linewidth=1)
            plt.axvline(0, color='black', linewidth=1)

        # Move the legend box outside the plot and give it a title
        plt.legend(title='Particle ID', bbox_to_anchor=(
            1.05, 1), loc='upper left', borderaxespad=0.)

        plt.show()

    def visualize_particle_heatmap(self):
        """
        Create a heatmap of particle densities based on original centroids.
        """
        # Plot the heatmap using seaborn
        df = self._linked_particles_dataframes
        plt.figure(figsize=(10, 8))
        sns.kdeplot(
            x=df['centroid_y'],
            y=df['centroid_x'],
            fill=True,
            cmap='viridis',
            cbar=True
        )
        plt.title('Heatmap of Particle Densities')
        plt.xlabel('Centroid Y')
        plt.ylabel('Centroid X')
        plt.gca().invert_yaxis()
        plt.show()

    def get_directory(self):
        """
        Retrieves the working directory.
        Returns:
        str: The working directory.
        """
        return self._directory

    # Private methods
    def __shape_and_sort_dataframe(self, dataframe: pd.DataFrame, cols: list[str], sort_by: list[str]) -> pd.DataFrame:
        """
        Shape and sort the dataframe.
        Args:
            dataframe (pd.DataFrame): The dataframe to shape and sort.
            cols (List[str]): List of column names to set for the dataframe.
            sort_by (List[str]): List of column names to sort the dataframe by.
            Returns:
            pd.DataFrame: The shaped and sorted dataframe.
        """
        temp_dataframe = pd.DataFrame(data=dataframe, columns=cols)
        temp_dataframe.columns = cols
        temp_dataframe.index.name = None
        return temp_dataframe.sort_values(by=sort_by, ascending=True)
