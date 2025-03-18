"""
Module for tracking particles in 2D using trackpy.
"""

import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import trackpy as tp
from matplotlib import cm
from tqdm import tqdm

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
        self._capture_speed_in_fps = identify_object._parent.get_frame_rate()
        self._pixel_scale_factor: float = identify_object._parent.get_pixel_scale_factor()
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

    def compute_plot_save_MSD(self, max_lag_time: int = 100, is_save: bool = False, output_file_name: str = 'Mean_Squared_Difference') -> pd.DataFrame:
        """
        Calculate the Mean Squared Displacement (MSD) of the particles.
        Args:
            max_lag_time (int): Maximum lag time to calculate the MSD. Default is 100.
            is_save (bool): Whether to save the MSD values to a CSV file. Default is False.
            output_file_name (str): Name of the output file to save the MSD values. Default is 'Mean_Squared_Difference'.
        Returns:
            pd.DataFrame: DataFrame containing the MSD values.
        """
        if self._linked_particles_dataframes.empty:
            raise ValueError(
                "No linked dataframes available. Please link particles first.")

        # Calculate the MSD
        msd_dataframe = tp.imsd(
            self._linked_particles_dataframes, mpp=self._pixel_scale_factor, fps=self._capture_speed_in_fps, max_lagtime=max_lag_time, pos_columns=self._position_columns[::-1])

        # Calculate the EMSD
        emsd_dataframe = tp.emsd(
            self._linked_particles_dataframes, mpp=self._pixel_scale_factor, fps=self._capture_speed_in_fps, max_lagtime=max_lag_time, pos_columns=self._position_columns[::-1])

        # Create subplots
        _, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=300)

        # Plot MSD
        ax1.plot(msd_dataframe.index, msd_dataframe, 'k-',
                 alpha=0.1)  # black lines, semitransparent
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax1.set(
            ylabel=r'$\langle \Delta r^2 \rangle$ [$\mu$m$^2$]', xlabel='lag time $t$')
        ax1.set_title('Mean Squared Displacement (MSD)')

        # Plot EMSD
        ax2.plot(emsd_dataframe.index, emsd_dataframe, 'bo')
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.set(
            ylabel=r'$\langle \Delta r^2 \rangle$ [$\mu$m$^2$]', xlabel='lag time $t$')
        ax2.set_title('Ensemble Mean Squared Displacement (EMSD)')

        plt.show()

        # Save the MSD values to a CSV file
        if is_save:
            output_path = os.path.join(
                self._directory, f'{output_file_name}.csv')
            msd_dataframe.to_csv(output_path, index=False)
            print(f'MSD values saved to {output_path}')

        return msd_dataframe

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

        # Create a copy of the dataframe to avoid modifying the original
        modified_dataframe = self._linked_particles_dataframes.copy()

        # Add new columns for swapped centroid_x and centroid_y
        modified_dataframe["new_x"] = modified_dataframe["centroid_y"]
        modified_dataframe["new_y"] = modified_dataframe["centroid_x"]

        modified_dataframe.to_csv(output_path, index=False)
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
        # Add axis titles
        plt.xlabel('Centroid X')
        plt.ylabel('Centroid Y')

        plt.gca().invert_yaxis()
        plt.gca().set_title('Scatter plot of the trajectories')

        n_cols = len(
            sorted_dataframe) // 20000 if len(sorted_dataframe) > 20000 else 1

        plt.legend(title='Particle ID', bbox_to_anchor=(
            1.05, 1), loc='upper left', borderaxespad=0., ncols=n_cols)
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

        # Add axis titles
        plt.xlabel('Centroid X')
        plt.ylabel('Centroid Y')

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

        n_cols = len(
            particle_data) // 20000 if len(particle_data) > 20000 else 1

        # Move the legend box outside the plot and give it a title
        plt.legend(title='Particle ID', bbox_to_anchor=(
            1.05, 1), loc='upper left', borderaxespad=0., ncols=n_cols)

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
        plt.xlabel('Centroid X')
        plt.ylabel('Centroid Y')
        plt.gca().invert_yaxis()
        plt.show()

    def get_directory(self):
        """
        Retrieves the working directory.
        Returns:
        str: The working directory.
        """
        return self._directory

    def set_linked_particles_dataframes(self, linked_particles_dataframes: pd.DataFrame) -> None:
        """
        Set the linked particles dataframes.
        Args:
            linked_particles_dataframes (pd.DataFrame): The linked particles dataframes.
        Returns:
            None
        """
        self._linked_particles_dataframes = linked_particles_dataframes

    def overlay_tracks_on_video(
        self,
        output_video_filename: str,
        colormap_name: str = "viridis",
        frame_index_offset: int = -1,
        show_labels: bool = True,
        font_scale: float = 0.5,
        font_thickness: int = 1,
        label_offset_x: int = 5,
        label_offset_y: int = -5
    ) -> None:
        """
        Overlays tracked particle trajectories onto the loaded video frames and saves the output video.
        Uses internal parent objects for video information.

        Args:
            output_video_filename (str): Name of the output video file to save with overlaid tracks.
            colormap_name (str, optional): Name of the matplotlib colormap to assign unique colors to particles.
                Default is "viridis".
            frame_index_offset (int, optional): Offset to adjust frame indexing differences between
                the tracking data and video frames. Default is -1.
            show_labels (bool, optional): Whether to overlay particle ID labels on the video frames. Default is True.
            font_scale (float, optional): Font size for particle ID labels. Default is 0.5.
            font_thickness (int, optional): Thickness of the label text. Default is 1.
            label_offset_x (int, optional): Horizontal offset for label placement. Default is 5.
            label_offset_y (int, optional): Vertical offset for label placement. Default is -5.

        Raises:
            ValueError: If tracking data is not available.
            ValueError: If no captured frames are available from the Capture class.
        """
        # Retrieve the working directory from the Capture class via the Identify object
        working_directory = self._parent.get_directory()

        # Construct the full output video path
        output_video_path = os.path.join(
            working_directory, output_video_filename)

        # Retrieve captured frames and validate
        frames = self._parent._parent.get_captured_frames()
        if not frames:
            raise ValueError(
                "No captured frames available. Ensure the video is loaded and processed correctly.")

        # Retrieve frame rate information
        frame_rate_info = self._parent._parent.get_frame_rate()
        fps = frame_rate_info.get(
            'user_provided_fps') or frame_rate_info.get('default_fps') or 15

        # Retrieve tracking data
        tracking_data = self._linked_particles_dataframes
        if tracking_data.empty:
            raise ValueError(
                "Tracking data is empty. Ensure particles are linked before overlaying tracks.")

        # Sort tracking data by frame and particle for consistency
        tracking_data = tracking_data.reset_index(drop=True)
        tracking_data = tracking_data.sort_values(by=["frame", "particle"])

        # Generate unique colors for particles
        particle_colors = self._generate_particle_colors(
            tracking_data, colormap_name)

        # Initialize video writer using the first frame dimensions
        video_writer = self._initialize_video_writer(
            frames[0], fps, output_video_path)

        # Dictionary to store cumulative particle tracks
        particle_tracks = {particle: []
                           for particle in tracking_data['particle'].unique()}

        # Total number of frames
        total_frames = len(frames)

        # Initialize progress bar
        with tqdm(total=total_frames, desc="Overlaying Tracks on Video") as progress_bar:
            for current_frame_index, frame in enumerate(frames):
                # Adjust frame index based on the offset
                adjusted_frame_index = current_frame_index + 1 + frame_index_offset

                # Extract particle data for the current frame
                frame_data = tracking_data[tracking_data['frame']
                                           == adjusted_frame_index]

                # Update particle tracks
                self._update_particle_tracks(frame_data, particle_tracks)

                # Draw particle trajectories on the frame
                self._draw_particle_tracks(
                    frame, particle_tracks, particle_colors)

                # Optionally, draw particle ID labels at the last tracked position
                if show_labels:
                    for particle_id, track_points in particle_tracks.items():
                        if track_points:
                            last_position = track_points[-1]
                            label_position = (
                                last_position[0] + label_offset_x, last_position[1] + label_offset_y)
                            cv2.putText(frame, str(particle_id), label_position,
                                        cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                                        particle_colors.get(
                                            particle_id, (255, 255, 255)),
                                        font_thickness, cv2.LINE_AA)

                # Write the processed frame to the output video
                video_writer.write(frame)
                progress_bar.update(1)

        # Release video writer resources
        video_writer.release()
        print(
            f'Processed video with overlaid tracks saved to {output_video_path}')

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

    def _generate_particle_colors(self, tracking_data: pd.DataFrame, colormap_name: str) -> dict:
        """
        Generates unique colors for each particle using the specified colormap.

        Args:
            tracking_data (pd.DataFrame): DataFrame containing tracking data.
            colormap_name (str): Name of the matplotlib colormap to use.

        Returns:
            dict: A dictionary mapping each particle ID to its assigned color in BGR format.
        """

        unique_particles = tracking_data['particle'].unique()
        num_particles = len(unique_particles)
        cmap = cm.get_cmap(colormap_name, num_particles)
        particle_colors = {particle: cmap(
            i)[:3] for i, particle in enumerate(unique_particles)}

        # Convert colors from 0-1 range to 0-255 range and from RGB to BGR for OpenCV
        particle_colors_bgr = {
            p: (int(c[2] * 255), int(c[1] * 255),
                int(c[0] * 255))  # Convert RGB to BGR
            for p, c in particle_colors.items()
        }

        return particle_colors_bgr

    def _initialize_video_writer(self, frame: np.ndarray, fps: float, output_video_path: str) -> cv2.VideoWriter:
        """
        Initializes the OpenCV VideoWriter object.

        Args:
            frame (np.ndarray): A single frame from the video to determine frame size.
            fps (float): Frames per second for the output video.
            output_video_path (str): Full path to save the output video.

        Returns:
            cv2.VideoWriter: Initialized VideoWriter object.
        """
        frame_height, frame_width = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Codec for the output video
        video_writer = cv2.VideoWriter(
            output_video_path, fourcc, fps, (frame_width, frame_height))
        return video_writer

    def _update_particle_tracks(self, frame_data: pd.DataFrame, particle_tracks: dict) -> None:
        """
        Updates the particle tracks dictionary with new positions from the current frame.

        Args:
            frame_data (pd.DataFrame): DataFrame containing particle data for the current frame.
            particle_tracks (dict): Dictionary storing cumulative tracks for each particle.
        """
        for _, row in frame_data.iterrows():
            particle_id = row['particle']
            # Swap x and y coordinates for correct alignment (assuming 'centroid_y' is x and 'centroid_x' is y)
            particle_position = (
                int(row['centroid_y']), int(row['centroid_x']))
            particle_tracks[particle_id].append(particle_position)

    def _draw_particle_tracks(self, frame: np.ndarray, particle_tracks: dict, particle_colors: dict) -> None:
        """
        Draws the particle tracks on the given frame.

        Args:
            frame (np.ndarray): The video frame to draw on.
            particle_tracks (dict): Dictionary storing cumulative tracks for each particle.
            particle_colors (dict): Dictionary mapping each particle ID to its color.
        """
        for particle_id, track_points in particle_tracks.items():
            # Default to white if not found
            track_color = particle_colors.get(particle_id, (255, 255, 255))
            for i in range(1, len(track_points)):
                cv2.line(
                    frame, track_points[i - 1], track_points[i], track_color, thickness=2)
