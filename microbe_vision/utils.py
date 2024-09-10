"""
Module to provide utility functions for the microbe_vision package.
"""
import os
import pandas as pd

from .track import Tracker
from .capture import Capture
from .identify import Identify

class Utility:
    """
    Class to provide utility functions for the microbe_vision package.
    """
    @staticmethod
    def combine_csvs_to_tracker(csv_file_paths: list[str],
                                working_directory: str = Capture.DEFAULT_FILE_DIRECTORY,
                                pixel_scale_factor: float = Capture.DEFAULT_PIXEL_SCALE_FACTOR,
                                scale_units: str = Capture.DEFAULT_SCALE_UNITS,
                                capture_speed_in_fps: int = Capture.DEFAULT_CAPTURE_SPEED_IN_FPS) -> Tracker:
        """
        Combine multiple CSVs of linked DataFrames into a single Tracker object by creating 
        the necessary Capture and Identify objects.

        Args:
            csv_file_paths (List[str]): List of file paths to the CSVs to be combined.
            working_directory (str, optional): The working directory where files are stored. Defaults to 'input_files'.
            pixel_scale_factor (float, optional): The pixel scale factor. Defaults to 1.
            scale_units (str, optional): The scale units. Defaults to 'units'.
            capture_speed_in_fps (int, optional): The capture speed in frames per second. Defaults to 15.

        Returns:
            Tracker: A Tracker object with the combined linked DataFrames.
        """
        # Step 1: Create the Capture object and simulate loading frames (since video is already processed)
        capture = Capture(working_directory=working_directory)
        capture.set_properties(
            capture_speed_in_fps=capture_speed_in_fps,
            pixel_scale_factor=pixel_scale_factor,
            scale_units=scale_units
        )

        # Step 2: Create the Identify object using the Capture object
        identify = Identify(capture)

        # Step 3: Combine CSVs into a single DataFrame and modify particle indices
        combined_dataframe = pd.DataFrame()

        for idx, file_path in enumerate(csv_file_paths):
            if not os.path.exists(file_path):
                raise FileNotFoundError(
                    f"The file {file_path} does not exist.")

            df = pd.read_csv(file_path)
            # Modify the particle column by prepending the CSV index
            df['particle'] = df['particle'].apply(lambda x: f'{idx}_{x}')
            combined_dataframe = pd.concat(
                [combined_dataframe, df], ignore_index=True)

        # Step 4: Create the Tracker object using the Identify object
        tracker = Tracker(identify)
        tracker.set_linked_particles_dataframes(combined_dataframe)

        print(
            f'Combined {len(csv_file_paths)} CSV files into a Tracker object with modified particle indices.')

        return tracker
