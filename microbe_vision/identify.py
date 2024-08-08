"""
The identify module provides the Identify class to perform object identification
on frames using different methods.
"""
import os
import time
from typing import List

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cellpose_omni import core, models  # type: ignore
from cellpose_omni.models import MODEL_NAMES
from omnipose.utils import normalize99  # type: ignore
from skimage import measure
from skimage.color import rgb2gray
from tqdm import trange

from .capture import Capture
from .constants import (OMNIPOSE_DEFAULT_PARAMS, AvailableOperations,
                        AvailableProps, PropsThreshold)


class Identify:
    """
    The Identify class provides methods to perform object identification on frames
    using nominal thresholding and omnipose models.
    """

    def __init__(self, capture_frame_object: Capture):
        """
        Initializes a new instance of the Identify class.
        Args:
            capture_frame_object (Capture | None): The Capture object to use for identification.
        Raises:
            TypeError: If the capture_frame_object is not an instance of Capture.
        """
        if not isinstance(capture_frame_object, Capture):
            raise TypeError(
                "capture_frame_object must be an instance of Capture")

        self._parent = capture_frame_object
        self._captured_frames: List = capture_frame_object.get_captured_frames()
        self._working_frames: List = self._captured_frames
        self._directory: str = capture_frame_object.get_directory()

        self._region_props_dataframe: pd.DataFrame = pd.DataFrame()

        self._normalized_frames: List = []
        self._omnipose_model: models.CellposeModel | None = None
        self._omnipose_params: dict = {}
        self._mask_store_path: str = ''

    def show_frames(self, images_to_show_count: int = 5, images_per_row: int = 5, use_gray_cmap: bool = False, image_size: tuple = (5, 5)) -> None:
        """
        Displays the captured frames.
        Args:
            images_to_show_count (int): The number of (equidistant) images to show. Default is 5.
            images_per_row (int): The number of images to show per row. Default is 5.
            use_gray_cmap (bool): Whether to use a grayscale colormap.
            image_size (tuple): The size of the image to display. Default is (5, 5).
        Returns:
            None
        """
        total_images = len(self._working_frames)
        if images_to_show_count > total_images:
            raise ValueError(
                'The number of images to show cannot be greater than the total number of images.')

        if images_per_row <= 0:
            raise ValueError(
                'The number of images per row cannot be negative.')

        jump = total_images // images_to_show_count
        selected_images_indices = range(0, total_images, jump)[
            :images_to_show_count]

        # Determine the number of rows based on the user input
        n_cols = images_per_row
        n_rows = int(np.ceil(images_to_show_count / n_cols))

        # Calculate dynamic figure size
        fig_width = n_cols * image_size[0]
        fig_height = n_rows * image_size[1]

        fig, axes = plt.subplots(
            n_rows, n_cols, figsize=(fig_width, fig_height))
        axes = axes.flatten()  # Flatten in case the axes array is multidimensional

        for idx, img_idx in enumerate(selected_images_indices):
            ax = axes[idx]
            if use_gray_cmap:
                ax.imshow(self._working_frames[img_idx], cmap='gray')
            else:
                ax.imshow(self._working_frames[img_idx])
            ax.set_title(f'Image {img_idx + 1}')
            ax.axis('off')  # Hide axes for better visualization

        # Hide any remaining subplots if there are fewer images than subplot slots
        for i in range(images_to_show_count, len(axes)):
            axes[i].axis('off')

        plt.tight_layout()
        plt.show()

    # Nominal Methods
    def apply_grayscale_thresholding(self, threshold: float = 0.5, is_update_frames: bool = True) -> List:
        """
        Applies grayscale thresholding to the captured frames.
        Args:
            threshold (float): The threshold value to use for thresholding.
            is_update_frames (bool): Whether to update the captured frames.
        Returns:
            List: The updated frames after applying grayscale thresholding.
        """
        updated_frames: List = []
        if threshold < 0 or threshold > 1:
            raise ValueError(
                'The threshold value should be between 0 and 1.')

        for frame_index in trange(len(self._captured_frames), desc='Applying grayscale thresholding'):
            gray_scale = rgb2gray(self._captured_frames[frame_index])
            gray_scale_opp = 1 - gray_scale
            binary_image = gray_scale_opp > threshold
            updated_frames.append(binary_image)

        if is_update_frames:
            self._working_frames = updated_frames

        print('Threshold applied successfully.')
        return updated_frames

    def generate_region_props_to_dataframe(self, view_props: List[AvailableProps]) -> pd.DataFrame:
        """
        Generates region properties for the captured frames.
        Args:
            view_props (List[AvailableProps]): The list of view properties to generate region properties for.
        Returns:
            pd.DataFrame: The region properties dataframe.
        """
        if not view_props or len(view_props) == 0:
            raise ValueError('The view properties cannot be None or empty.')

        region_props_dataframe = pd.DataFrame()
        for frame_index in trange(len(self._working_frames), desc='Generating region properties'):
            labelled_frame = measure.label(self._working_frames[frame_index])
            properties = tuple(prop.value for prop in view_props)
            region_props = measure.regionprops_table(
                labelled_frame, properties=properties)

            frame_dataframe = pd.DataFrame(region_props)
            frame_dataframe.columns = self.__get_custom_column_names(
                view_props)
            frame_dataframe['frame'] = frame_index + 1

            region_props_dataframe = pd.concat(
                [region_props_dataframe, frame_dataframe], ignore_index=True)
        self._region_props_dataframe = region_props_dataframe

        print('Region properties generated successfully.')
        return region_props_dataframe

    def apply_filters_on_region_props(self, props_threshold: List[PropsThreshold], is_update_dataframes: bool = True) -> pd.DataFrame:
        """
        Applies filters on the region properties dataframe.
        Args:
            props_threshold (List[PropsThreshold]): The list of property thresholds to apply.
            is_update_dataframes (bool): Whether to update the region properties dataframe.
        Returns:
            pd.DataFrame: The filtered region properties dataframe.
        """
        filtered_df = self._region_props_dataframe.copy()
        for threshold_condition in props_threshold:
            prop = threshold_condition['property']
            operation = threshold_condition['operation']
            value = threshold_condition['value']

            # Applying the filter based on the operation
            if operation == AvailableOperations.GREATER_THAN:
                filtered_df = filtered_df[filtered_df[prop.value] > value]
            elif operation == AvailableOperations.LESS_THAN:
                filtered_df = filtered_df[filtered_df[prop.value] < value]
            elif operation == AvailableOperations.EQUALS:
                filtered_df = filtered_df[filtered_df[prop.value] == value]
            else:
                print(f'Invalid operation in props_threshold: {operation}')

        if is_update_dataframes:
            self._region_props_dataframe = filtered_df

        print('Filters applied successfully.')
        return filtered_df

    # Omnipose Methods
    def get_possible_omnipose_model_names(self) -> List[str]:
        """
        Gets the possible omnipose model names.
        Returns:
            List[str]: The list of possible omnipose model names.
        """
        return MODEL_NAMES

    def initialize_omnipose_model(self, model_name: str = 'bact_phase_omni', use_gpu: bool = False, params: dict = OMNIPOSE_DEFAULT_PARAMS) -> None:
        """
        Initializes the omnipose model.
        Args:
            model_name (str): The name of the omnipose model to use.
            params (dict): The parameters to use for the omnipose model.
            use_gpu (bool): Whether to use the GPU for the omnipose model.
        Returns:
            None
        """
        is_gpu_activated = self.__activate_gpu() if use_gpu else False
        omnipose_model = models.CellposeModel(
            gpu=is_gpu_activated, model_type=model_name)
        self.__prepare_frames_for_omnipose_model()
        self._omnipose_model = omnipose_model
        self._omnipose_params = params
        print('Omnipose model initialized successfully.')

    def apply_omnipose_masking(self, batch_size: int = 50, save_masks: bool = False, masks_store_path: str = 'masks', is_update_frames: bool = True) -> List:
        """
        Segments the objects using the omnipose model.
        Args:
            save_masks (bool): Whether to save the masks.
            masks_store_path (str): The path to store the masks.
        Returns:
            List: The segmented masks.
        """
        if not self._omnipose_model:
            raise ValueError('The omnipose model is not initialized.')

        if masks_store_path:
            complete_store_path = self.__handle_folder_preprocess(
                masks_store_path)
            self._mask_store_path = complete_store_path

        masks = self.__get_masks_from_batch_wise_segmented_images(
            batch_size=batch_size,
            save_masks=save_masks)
        print('Objects segmented successfully using the omnipose model.')

        if is_update_frames:
            self._working_frames = masks
        return masks

    # Utility Methods
    def plot_centroids(self, show_time=False) -> None:
        """
        Plots the centroids of the objects.
        Args:
            show_time (bool): Whether to show the time on the plot.
        Returns:
            None
        """
        if show_time:
            plt.scatter(self._region_props_dataframe['centroid_y'], self._region_props_dataframe['centroid_x'],
                        s=5, c=self._region_props_dataframe['frame'], cmap="jet_r")

            # Add color bar with label
            color_bar = plt.colorbar()
            color_bar.set_label('Frame Number')
        else:
            plt.scatter(self._region_props_dataframe['centroid_y'],
                        self._region_props_dataframe['centroid_x'], s=5, color='black')
        # Add title
        plt.title('Scatter Plot of Centroids Over Frames')

        # Add axis labels
        plt.xlabel('Pixel Y')
        plt.ylabel('Pixel X')

        plt.gca().invert_yaxis()
        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(False)
        plt.show()

    def save_identified_objects_to_csv(self, output_file_name='identified_objects') -> None:
        """
        Saves the identified objects to a CSV file.
        Args:
            output_file_name (str): The name of the output file.
        Returns:
            None
        """
        save_file_path = os.path.join(
            self._directory, f'{output_file_name}.csv')
        self._region_props_dataframe.to_csv(save_file_path, index=False)
        print('Identified objects saved successfully to path: ', save_file_path)

    def get_region_props_dataframe(self) -> pd.DataFrame:
        """
        Gets the region properties dataframe.
        Returns:
            pd.DataFrame: The region properties dataframe.
        """
        return self._region_props_dataframe

    def get_directory(self):
        """
        Retrieves the working directory.
        Returns:
          str: The working directory.
        """
        return self._directory

    # Private methods
    def __get_custom_column_names(self, view_props: List[AvailableProps]) -> List[str]:
        """
        Function to get the column names.
        Args:
            view_props (List[AvailableProps]): The list of view properties to get the column names for.
        Returns:
            List[str]: The list of column names for the view properties.
        Raises:
            ValueError: If the view properties are None.
        """
        column_names: List[str] = []
        if view_props is None:
            raise ValueError('The view properties cannot be None.')
        for view_prop in view_props:
            if view_prop == AvailableProps.CENTROID:
                column_names.append('centroid_x')
                column_names.append('centroid_y')
            else:
                column_names.append(view_prop.value)
        return column_names

    def __prepare_frames_for_omnipose_model(self) -> None:
        """
        Prepares the captured frames for the omnipose model - Normalizing the frames.
        Returns:
            None
        """
        if self._normalized_frames:
            print('Frames are already prepared for the omnipose model.')
            return
        is_binary_frames = self.__are_frames_binary(self._working_frames)
        if is_binary_frames:
            self._working_frames = self.__convert_to_uint8(
                self._working_frames)

        normalized_frames = []
        for frame_index in trange(len(self._working_frames), desc='Preparing frames for the omnipose model'):
            gray_image = self._working_frames[frame_index] if is_binary_frames else cv2.cvtColor(
                self._working_frames[frame_index], cv2.COLOR_BGR2GRAY)
            normalized_frame = normalize99(gray_image)
            normalized_frames.append(normalized_frame)
        self._normalized_frames = normalized_frames
        print('Frames prepared successfully for the omnipose model.')

    def __are_frames_binary(self, frames: List) -> bool:
        """
        Checks if all frames are binary (contain only True or False values).
        Args:
            frames (List): The frames to be checked.
        Returns:
            bool: True if all frames are binary, False otherwise.
        """
        return all(np.array_equal(frame, frame.astype(bool)) for frame in frames)

    def __convert_to_uint8(self, binary_frames: List) -> List:
        """
        Converts binary frames to uint8 format.
        Args:
            binary_frames (List): The binary frames to be converted.
        Returns:
            List: The converted frames in uint8 format.
        """
        uint8_frames = [(frame.astype(np.uint8) * 255)
                        for frame in binary_frames]
        return uint8_frames

    def __activate_gpu(self) -> bool:
        """
        Activates the GPU for the omnipose model.
        Returns:
            bool: Whether the GPU is activated.
        """
        use_gpu = core.use_gpu()
        print(f'>>> GPU activated? {use_gpu}')
        return use_gpu

    def __handle_folder_preprocess(self, image_store_path):
        """
        Handles the preprocessing of the image store folder.

        Args:
          image_store_path (str): The path of the image store folder.

        Returns:
          str: The complete path of the image store folder.
        """
        complete_path = os.path.join(self._directory, image_store_path)
        if os.path.exists(complete_path):
            self.__empty_folder(complete_path)
        else:
            os.makedirs(complete_path)
        return complete_path

    def __empty_folder(self, folder_path):
        """
        Empties the contents of a folder.

        Args:
        folder_path (str): The path of the folder to empty.
        """
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)

    def __get_segmented_masks(self, batch_images: List) -> List:
        """
        Gets the segmented masks for the batch images.
        Args:
            batch_images (List): The list of batch images to get the segmented masks for.
        Returns:
            List: The segmented masks.
        """
        tic = time.time()
        masks, _, _ = self._omnipose_model.eval(
            batch_images, **self._omnipose_params)  # type: ignore
        net_time = time.time() - tic
        print(f'total segmentation time: {net_time}s')
        return masks

    def __convert_masks_to_binary(self, given_masks: List) -> List:
        """
        Converts the given masks to binary masks.
        Args:
            given_masks (List): The list of masks to convert to binary masks.
        Returns:
            List: The binary masks. 
        """
        background_class_value = 0
        binary_mask_images = []
        for mask in given_masks:
            new_mask = mask > background_class_value
            mask_as_image = new_mask.astype('uint8') * 255
            binary_mask_images.append(mask_as_image)
        return binary_mask_images

    def __process_batch_images_to_get_binary_masks(self, batch_images: List, save_masks: bool = True, batch_start_index: int = 0) -> List:
        """
        Processes the batch images to get the binary masks.
        Args:
            batch_images (List): The list of batch images to process.
            save_masks (bool): Whether to save the masks.
        Returns:
            List: The binary masks.
        """
        masks = self.__get_segmented_masks(batch_images)
        binary_masks = self.__convert_masks_to_binary(masks)
        if save_masks:
            for i, mask in enumerate(binary_masks):
                mask_index = batch_start_index + i
                mask_path = os.path.join(
                    self._mask_store_path, f'mask_{mask_index}.tiff')
                cv2.imwrite(mask_path, mask)
        return binary_masks

    def __get_masks_from_batch_wise_segmented_images(self, batch_size: int = 5, save_masks: bool = True) -> List:
        """
        Gets the masks from the batch-wise segmented images.
        Args:
            batch_size (int): The batch size to use for segmentation.
            save_masks (bool): Whether to save the masks.
        Returns:
            List: The masks.
        """
        resultant_masks = []
        for each in trange(0, len(self._normalized_frames), batch_size, desc='Segmenting images'):
            batch_images = self._normalized_frames[each: each + batch_size]
            binary_masks = self.__process_batch_images_to_get_binary_masks(
                batch_images, save_masks, each)
            print(f'Batch {each // batch_size + 1} segmentation is complete')
            resultant_masks += binary_masks
        return resultant_masks
