"""
The identify module provides the Identify class to perform object identification
on frames using different methods.
"""
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cellpose_omni import core, models  # type: ignore
from cellpose_omni.models import MODEL_NAMES
from matplotlib.lines import Line2D  # type: ignore
from omnipose.utils import normalize99  # type: ignore
from scipy.optimize import curve_fit  # type: ignore
from skimage import measure
from skimage.color import rgb2gray
from skimage.filters import threshold_isodata  # pylint: disable=E0611
from skimage.filters import threshold_li  # pylint: disable=E0611
from skimage.filters import threshold_mean  # pylint: disable=E0611
from skimage.filters import threshold_minimum  # pylint: disable=E0611
from skimage.filters import threshold_otsu  # pylint: disable=E0611
from skimage.filters import threshold_triangle  # pylint: disable=E0611
from skimage.filters import threshold_yen  # pylint: disable=E0611
from skimage.filters import \
    try_all_threshold  # pylint: disable=E0611; pylint: disable=E0611
from tqdm import tqdm, trange

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

    def try_all_algorithm_based_thresholding(self, frame_index: int = 0) -> None:
        """
        Applies thresholding algorithms from the scikit-image library to the captured frames.
        Read more about it here: https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.try_all_threshold
        NOTE: The function might show dark objects over a light background. But for actual implementation, opposite is required.
        Args:
            frame_index (int): The index of the frame to apply the thresholding to. Default is 0.
        Returns:
            None
        """
        gray_image = rgb2gray(self._captured_frames[frame_index])
        fig, ax = try_all_threshold(gray_image, figsize=(10, 8), verbose=False)
        print("Following thresholding algorithms are applied: 'isodata', 'li', 'mean', 'minimum', 'otsu', 'triangle', 'yen'")
        plt.show()

    def apply_algorithm_based_thresholding(self, algorithm: str = 'otsu', is_color_inverse: bool = False, is_update_frames: bool = True, **kwargs) -> List:
        """
        Applies algorithm-based thresholding to the captured frames.
        NOTE: If the dark objects over a light background are getting displayed, Put 'is_color_inverse' to True to correct it before moving to the next step.
        Args:
            algorithm (str): The algorithm to use for thresholding. 
                'otsu', 'isodata', 'li', 'mean', 'minimum', 'otsu', 'triangle', 'yen' are the available options.
                Default is 'otsu'.
            is_update_frames (bool): Whether to update the captured frames.
            is_color_inverse (bool): Whether to invert the colors. Default is False.
            **kwargs: Additional keyword arguments for the thresholding algorithms. 
                Check the skimage documentation for more information on other passable args
                Link: https://scikit-image.org/docs/stable/api/skimage.filters.html
        Returns:
            List: The updated frames after applying algorithm-based thresholding.
        """

        # Mapping of available algorithms to their corresponding functions
        algorithm_function_map = {
            'otsu': threshold_otsu,
            'isodata': threshold_isodata,
            'li': threshold_li,
            'mean': threshold_mean,
            'minimum': threshold_minimum,
            'triangle': threshold_triangle,
            'yen': threshold_yen
        }

        if algorithm not in algorithm_function_map:
            raise ValueError(
                f"Algorithm '{algorithm}' is not recognized. Available algorithms: {list(algorithm_function_map.keys())}")

        # Retrieve the threshold function based on the selected algorithm
        threshold_function = algorithm_function_map[algorithm]
        updated_frames: List = []

        for frame_index in trange(len(self._captured_frames), desc='Applying algorithm-based thresholding'):
            gray_scale = rgb2gray(self._captured_frames[frame_index])
            
            # Invert the colors if required
            gray_scale = 1 - gray_scale if is_color_inverse else gray_scale

            threshold_value = threshold_function(gray_scale)
            binary_image = gray_scale > threshold_value
            updated_frames.append(binary_image)

        if is_update_frames:
            self._working_frames = updated_frames

        print(
            f'Selected {algorithm} Algorithm-based thresholding applied successfully.')
        print(
            "NOTE: If dark objects are displayed over a light background, set 'is_color_inverse' to True "
            "and redo the thresholding to correct it before proceeding to the next step."
        )

        return updated_frames

    def apply_gaussian_adaptive_thresholding(self, block_size: int = 11, c: int = 2, is_color_inverse: bool = False, is_update_frames: bool = True) -> List:
        """
        Applies Gaussian adaptive thresholding to the captured frames.
        NOTE: If the dark objects over a light background are getting displayed, Put 'is_color_inverse' to True to correct it before moving to the next step.
        Args:
            block_size (int): The size of the block for adaptive thresholding. Default is 11.
            c (int): The constant to subtract from the mean. Default is 2.
            is_color_inverse (bool): Whether to invert the colors. Default is False.
            is_update_frames (bool): Whether to update the captured frames.
        Returns:
            List: The updated frames after applying Gaussian adaptive thresholding.
        """
        updated_frames: List = []
        for frame_index in trange(len(self._captured_frames), desc='Applying Gaussian adaptive thresholding'):
            gray_scale = rgb2gray(self._captured_frames[frame_index])
            gray_scale = (gray_scale * 255).astype('uint8')

            # Apply Gaussian adaptive thresholding
            thresholded_image = cv2.adaptiveThreshold(
                gray_scale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c
            )

            # Convert thresholded image to binary format (True/False)
            # This creates a boolean array (True/False)
            binary_image = thresholded_image > 0

            # Convert to 0/1 representation
            binary_image = binary_image.astype(int)

            # Invert the binary image if is_color_inverse is True
            if is_color_inverse:
                binary_image = 1 - binary_image  # Inverts the binary image

            updated_frames.append(binary_image)

        if is_update_frames:
            self._working_frames = updated_frames

        print('Gaussian adaptive thresholding applied successfully.')
        print(
            "NOTE: If dark objects are displayed over a light background, set 'is_color_inverse' to True "
            "and redo the thresholding to correct it before proceeding to the next step."
        )
        return updated_frames

    def apply_color_inverse(self, is_update_frames: bool = True) -> List:
        """
        Applies color inverse to the captured frames.
        Args:
            is_update_frames (bool): Whether to update the captured frames.
        Returns:
            List: The updated frames after applying color inverse.
        """
        updated_frames: List = []
        for frame_index in trange(len(self._captured_frames), desc='Applying color inverse'):
            inverted_frame = cv2.bitwise_not(
                self._captured_frames[frame_index])
            updated_frames.append(inverted_frame)

        if is_update_frames:
            self._working_frames = updated_frames

        print('Color inverse applied successfully.')
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
        plt.xlabel('Pixel X')
        plt.ylabel('Pixel Y')

        plt.gca().invert_yaxis()
        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(False)
        plt.show()

    def save_identified_objects_to_csv(self, output_file_name='identified_objects') -> None:
        """
        Saves the identified objects to a CSV file. The file will contain the region properties dataframe. 
        Args:
            output_file_name (str): The name of the output file.
        Returns:
            None
        """
        save_file_path = os.path.join(
            self._directory, f'{output_file_name}.csv')

        # Create a copy of the dataframe to avoid modifying the original
        modified_dataframe = self._region_props_dataframe.copy()

        # Add new columns for swapped centroid_x and centroid_y
        modified_dataframe["new_x"] = modified_dataframe["centroid_y"]
        modified_dataframe["new_y"] = modified_dataframe["centroid_x"]

        modified_dataframe.to_csv(save_file_path, index=False)
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

    def __process_batch_images_to_get_masks(self, batch_images: List, save_masks: bool = True, batch_start_index: int = 0) -> List:
        """
        Processes the batch images to get the binary masks.
        Args:
            batch_images (List): The list of batch images to process.
            save_masks (bool): Whether to save the masks.
        Returns:
            List: The binary masks.
        """
        masks = self.__get_segmented_masks(batch_images)
        if save_masks:
            for i, mask in enumerate(masks):
                mask_index = batch_start_index + i
                mask_number = str(mask_index).zfill(len(str(masks)))
                mask_path = os.path.join(
                    self._mask_store_path, f'mask_{mask_number}.tiff')
                cv2.imwrite(mask_path, mask)
        return masks

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
            binary_masks = self.__process_batch_images_to_get_masks(
                batch_images, save_masks, each)
            print(f'Batch {each // batch_size + 1} segmentation is complete')
            resultant_masks += binary_masks
        return resultant_masks

    # Gaussian Fit Methods
    def __2d_gaussian(self, coords, amplitude, xo, yo, sigma_x, sigma_y, offset):
        """
        A static 2D Gaussian model.
        """
        x, y = coords
        return (amplitude * np.exp(-(((x - xo) ** 2) / (2 * sigma_x ** 2) +
                                     ((y - yo) ** 2) / (2 * sigma_y ** 2))) + offset).ravel()

    def __extract_subimage(self, gray_frame: np.ndarray, center: tuple, fit_window: int):
        """
        Extracts a sub-image centered at `center` using a window of size fit_window.

        Args:
            gray_frame (np.ndarray): Grayscale image.
            center (tuple): Center in (y, x) order.
            fit_window (int): Half-size of the window.

        Returns:
            sub_image (np.ndarray): Extracted sub-image.
            xmin, ymin (int): Top-left coordinates of the sub-image.
            If the window exceeds image boundaries, returns (None, None, None).
        """
        x_center = center[1]  # center is (y, x)
        y_center = center[0]
        xmin = int(x_center - fit_window)
        xmax = int(x_center + fit_window)
        ymin = int(y_center - fit_window)
        ymax = int(y_center + fit_window)

        if xmin < 0 or ymin < 0 or xmax >= gray_frame.shape[1] or ymax >= gray_frame.shape[0]:
            return None, None, None
        sub_image = gray_frame[ymin:ymax, xmin:xmax]
        return sub_image, xmin, ymin

    def __fit_gaussian_to_subimage(self, sub_image: np.ndarray, fit_window: int):
        """
        Performs a 2D Gaussian fit on the given sub-image.

        Args:
            sub_image (np.ndarray): The extracted sub-image.
            fit_window (int): Half-size of the window.

        Returns:
            opt_param (np.ndarray): Optimized parameters.
            x_vals, y_vals (np.ndarray): Meshgrid arrays corresponding to the sub-image.
        """
        x_vals, y_vals = np.meshgrid(
            np.arange(sub_image.shape[1]), np.arange(sub_image.shape[0]))
        x_data = x_vals.ravel()
        y_data = y_vals.ravel()
        intensity_data = sub_image.ravel()

        amplitude_guess = np.max(sub_image)
        sigma_guess = max(fit_window / 2, 1)
        offset_guess = np.min(sub_image)
        initial_guess = (amplitude_guess, fit_window / 2,
                         fit_window / 2, sigma_guess, sigma_guess, offset_guess)
        bounds = ((0, 0, 0, 0.1, 0.1, 0), (np.inf, fit_window,
                  fit_window, fit_window, fit_window, np.inf))

        opt_param, _ = curve_fit(self.__2d_gaussian, (x_data, y_data), intensity_data,
                                 p0=initial_guess, bounds=bounds)
        return opt_param, x_vals, y_vals

    def __compute_refined_centroid(self, opt_param: np.ndarray, xmin: int, ymin: int, initial_center: tuple, fit_window: int):
        """
        Computes the refined centroid (in full-image coordinates) from the fitted parameters.

        Args:
            opt_param (np.ndarray): Optimized Gaussian parameters.
            xmin, ymin (int): Top-left coordinates of the sub-image.
            initial_center (tuple): Original centroid in (y, x) order.
            fit_window (int): Half-size of the window.

        Returns:
            (refined_x, refined_y): The refined centroid.
            If the shift exceeds fit_window, returns the initial centroid.
        """
        refined_x = xmin + opt_param[1]
        refined_y = ymin + opt_param[2]
        x_init = initial_center[1]
        y_init = initial_center[0]
        if abs(refined_x - x_init) > fit_window or abs(refined_y - y_init) > fit_window:
            return x_init, y_init
        return refined_x, refined_y

    def __process_gaussian_fit_on_a_frame(self, gray_frame: np.ndarray, frame_index: pd.DataFrame, fit_window: int = 7) -> tuple[dict, dict]:
        """
        Processes the Gaussian fit on a single frame.

        Args:
            gray_frame (np.ndarray): Grayscale image.
            frame_index (int): The index of the frame to process.
            fit_window (int): Half-size of the window for the Gaussian fit.
        Returns:
            initial_centroids (dict): Initial centroids in (y, x) order.
            gaussian_centroids (dict): Refined centroids in (y, x) order.
        """
        frame_region_props = self._region_props_dataframe[
            self._region_props_dataframe['frame'] == frame_index]

        # Skip empty frames
        if frame_region_props.empty:
            return None  # Skip empty frames

        initial_centroids = {}
        gaussian_centroids = {}

        for _, row in frame_region_props.iterrows():
            initial_center = (row['centroid_y'], row['centroid_x'])
            label = row['label']

            initial_centroids[label] = initial_center

            sub_image, xmin, ymin = self.__extract_subimage(
                gray_frame, initial_center, fit_window)
            if sub_image is None:
                gaussian_centroids[label] = initial_center
                continue

            try:
                opt_param, _, _ = self.__fit_gaussian_to_subimage(
                    sub_image, fit_window)
                refined_x, refined_y = self.__compute_refined_centroid(
                    opt_param, xmin, ymin, initial_center, fit_window)
                gaussian_centroids[label] = (refined_y, refined_x)
            except Exception:  # pylint: disable=W0703
                gaussian_centroids[label] = initial_center
        return initial_centroids, gaussian_centroids

    def visualize_gaussian_fit_on_a_frame(self, frame_index: int, fit_window: int = 7) -> None:
        """
        Visualizes the Gaussian fit on all centroids in a frame.

        Args:
            frame_index (int): The index of the frame to visualize.
            fit_window (int): Half-size of the window for the Gaussian fit.

        Returns:
            None
        """
        if self._region_props_dataframe.empty:
            print(
                "Region properties dataframe is empty. Please generate region properties first.")
            return

        if frame_index < 0 or frame_index > len(self._captured_frames):
            print("Invalid frame index.")
            return

        gray_frame = self._working_frames[frame_index - 1]

        initial_centroids, refined_centroids = self.__process_gaussian_fit_on_a_frame(
            gray_frame, frame_index, fit_window)

        plt.figure(figsize=(10, 8))
        plt.imshow(gray_frame, cmap='gray')
        plt.plot([center[0] for center in initial_centroids.values()],
                 [center[1] for center in initial_centroids.values()], 'bo', markersize=5)
        plt.plot([center[0] for center in refined_centroids.values()],
                 [center[1] for center in refined_centroids.values()], 'g*', markersize=5)
        plt.title(f"Gaussian Fit on All Centroids in Frame {frame_index}")
        plt.xlabel("Y (pixels)")
        plt.ylabel("X (pixels)")
        legend_elements = [Line2D([0], [0], marker='o', color='w', label='Initial centroid',
                                  markerfacecolor='b', markersize=8),
                           Line2D([0], [0], marker='*', color='w', label='Refined centroid',
                                  markerfacecolor='g', markersize=12)]
        plt.legend(handles=legend_elements, loc='upper right')
        plt.show()

    def optimize_centroids_using_gaussian_fit(self, fit_window: int = 7, max_workers: int = None) -> None:
        """
        Optimizes the centroid coordinates in the internal region properties dataframe using
        parallel processing with threads. Each frame is processed independently: for each region
        in a frame, a sub-image is extracted and a 2D Gaussian fit is performed. If the refined
        centroid is within acceptable bounds, the internal dataframe is updated accordingly.

        This version uses ThreadPoolExecutor for parallel processing.

        Args:
            fit_window (int): The search window size around the detected centroid (default is 7).
            max_workers (int): Maximum number of worker threads. If None, ThreadPoolExecutor
                            will choose a default.
        Returns:
            None
        """
        if self._region_props_dataframe.empty:
            print(
                "Region properties dataframe is empty. Please generate region properties first.")
            return

        num_frames = len(self._captured_frames)
        # Assuming frames are numbered starting at 1
        frame_numbers = range(1, num_frames + 1)

        futures = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for frame_num in frame_numbers:
                # Submit processing task for each frame. Use the stored working frame.
                futures[executor.submit(self.__process_gaussian_fit_on_a_frame,
                                        self._working_frames[frame_num - 1],
                                        frame_num, fit_window)] = frame_num

            results = {}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing frames (Parallel)"):
                frame_num = futures[future]
                try:
                    # Expecting each future to return a tuple: (frame_num, (initial_centroids, refined_centroids))
                    result = future.result()
                    results[frame_num] = result[1]
                except Exception as e:  # pylint: disable=W0703
                    print(f"Error processing frame {frame_num}: {e}")
                    results[frame_num] = None

        # Update the internal dataframe using the refined centroids
        for frame_num, result in tqdm(results.items(), desc="Updating centroids"):
            if result is None:
                continue
            for label, refined_center in result.items():
                self._region_props_dataframe.loc[
                    (self._region_props_dataframe['frame'] == frame_num) &
                    (self._region_props_dataframe['label'] == label),
                    ['centroid_y', 'centroid_x']
                ] = refined_center

        print("Centroids optimized successfully using Gaussian fit.")
