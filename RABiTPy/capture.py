"""
The capture module provides the Capture class to retrieve file paths, store images 
from a video, and perform related operations.
"""
import os
import cv2
from tqdm import tqdm, trange


class Capture:
    """
    The Capture class provides methods to retrieve file paths, store images from a video, 
    and perform related operations.
    """

    DEFAULT_FILE_DIRECTORY = 'input_files'
    DEFAULT_STORE_IMAGE_FILE_DIRECTORY = 'frames_from_video'
    SUPPORTED_INPUT_VIDEO_FILE_TYPES = ['avi', 'mp4', 'mpg', 'mpeg']
    DEFAULT_PIXEL_SCALE_FACTOR = 1
    DEFAULT_SCALE_UNITS = 'units'
    DEFAULT_CAPTURE_SPEED_IN_FPS = 15

    def __init__(self, working_directory=DEFAULT_FILE_DIRECTORY):
        """
        Initializes a new instance of the Capture class.

        Args:
          working_directory (str): The directory where the input files are located. 
          Defaults to DEFAULT_FILE_DIRECTORY.
        """
        self._directory = self.__handle_working_directory_preprocess(working_directory)
        self._supported_video_file_types: list[str] = Capture.SUPPORTED_INPUT_VIDEO_FILE_TYPES
        self._video_file_path: str = ''
        self._video_file_name: str = ''
        self._default_fps: int = 0
        self._actual_fps: int = 0
        self._pixel_scale_factor: float = 0.0
        self._scale_units: str = ''
        self._video_frames_store_path: str = ''
        self._captured_frames: list = []

    def load_video(self, file_name=''):
        """
        Retrieves and validates the file path based on user input and prints the video information.

        Args:
          file_name (str, optional): The name of the video file. Defaults to ''.

        Returns:
          str: The validated file path.

        Raises:
          FileNotFoundError: If the specified file is not found.
        """
        try:
            self._video_file_name = file_name

            self.__validate_the_file_name_and_type(file_name)
            file_path = self.__generate_and_validate_file_path(file_name)
            self._video_file_path = file_path

            video = cv2.VideoCapture(self._video_file_path)
            try:
                default_video_fps = self.__print_video_info_and_get_fps(video)
                self._default_fps = default_video_fps
            finally:
                video.release()

            print(f'Video file loaded successfully: {file_path}')
            return file_path

        except FileNotFoundError as e:
            print(e)

    def process_video_into_frames(self, pixel_scale_factor: float = DEFAULT_PIXEL_SCALE_FACTOR,
                                  scale_units: str = DEFAULT_SCALE_UNITS,
                                  capture_speed_in_fps=None,
                                  is_store_video_frames=False,
                                  store_images_path=DEFAULT_STORE_IMAGE_FILE_DIRECTORY) -> list:
        """
        Processes the already loaded video into frames based on the given pixel to micrometer conversion factor and capture speed.
        The pixel_scale_factor is mandatory to process the video into frames else will give an error.

        Args:
          pixel_scale_factor (float, optional): The pixel scale factor. Defaults to DEFAULT_PIXEL_SCALE_FACTOR.
          scale_units (str, optional): The scale units. Defaults to DEFAULT_SCALE_UNITS.
          capture_speed_in_fps (int, optional): Capture speed in frames/sec. Defaults to given video FPS or 15. Note: If the user provides the capture speed in FPS, The time of the video might be different from the actual video time, although the total frames will be constant.
          is_store_video_frames (bool, optional): Flag to store video frames. Defaults to False.
          store_images_path (str, optional): Path to store images. Defaults to DEFAULT_STORE_IMAGE_FILE_DIRECTORY.

        Returns:
          list: The captured frames.

        Raises:
          ValueError: If the pixel to micrometer conversion factor is not provided.
        """
        try:
            if not pixel_scale_factor:
                raise ValueError('Error: A valid Pixel Scale factor is mandatory to process the video and calculate the stats')

            # If the user provides the capture speed in FPS, then use that value else use the video FPS
            if capture_speed_in_fps:
                self._actual_fps = capture_speed_in_fps
                print(f'User provided a FPS: {self._actual_fps}, So processing the video with the given FPS')
            else:
                self._actual_fps = self._default_fps

            captured_frames = []
            self._pixel_scale_factor = pixel_scale_factor
            self._scale_units = scale_units

            captured_frames = self.__capture_images_from_video(is_store_video_frames,
                                                               store_images_path)
            self._captured_frames = captured_frames
            print(
                f'Processed video into frames successfully with pixel scale factor: {self._pixel_scale_factor} {self._scale_units}'
            )
            return captured_frames
        except ValueError as e:
            print(e)

    def get_captured_frames(self):
        """
        Retrieves the captured frames.

        Returns:
          list: The captured frames.
        """
        return self._captured_frames

    def get_directory(self):
        """
        Retrieves the working directory.
        Returns:
          str: The working directory.
        """
        return self._directory

    def get_frame_rate(self) -> dict:
        """
        Retrieves the frame rate.
        Returns:
          dict: The frame rates (user provided and default).
        """
        return { 'user_provided_fps': self._actual_fps, 'default_fps': self._default_fps }

    def get_pixel_scale_factor(self):
        """
        Retrieves the pixel to micrometer conversion factor.
        Returns:
          float: The pixel to micrometer conversion factor.
        """
        return self._pixel_scale_factor

    def load_images_as_frames(self, folder_path, capture_speed_in_fps=DEFAULT_CAPTURE_SPEED_IN_FPS, pixel_scale_factor=DEFAULT_PIXEL_SCALE_FACTOR, scale_units=DEFAULT_SCALE_UNITS):
        """
        Loads all images from the given folder as frames in alphabetical order of the filenames.

        Args:
          folder_path (str): The path of the folder containing the images.
          capture_speed_in_fps (int, optional): The capture speed in frames per second. Defaults to DEFAULT_CAPTURE_SPEED_IN_FPS.
          pixel_scale_factor (float, optional): The pixel scale factor. Defaults to DEFAULT_PIXEL_SCALE_FACTOR.
          scale_units (str, optional): The scale units. Defaults to DEFAULT_SCALE_UNITS.

        Raises:
          FileNotFoundError: If the specified folder is not found.
        """
        self._default_fps = capture_speed_in_fps
        self._actual_fps = capture_speed_in_fps
        self._pixel_scale_factor = pixel_scale_factor
        self._scale_units = scale_units

        complete_folder_path = os.path.join(self._directory, folder_path)
        if not os.path.isdir(complete_folder_path):
            raise FileNotFoundError(f'Folder not found: {complete_folder_path}')

        image_files = self.__list_files(complete_folder_path)
        frames = []
        for index in trange(len(image_files), desc='Loading frames'):
            image_path = os.path.join(complete_folder_path, image_files[index])
            frame = cv2.imread(image_path)
            if frame is not None:
                frames.append(frame)

        self._captured_frames = frames
        print(f'{len(frames)} frames loaded from folder: {complete_folder_path}')
        return frames

    def set_properties(self, pixel_scale_factor: float = DEFAULT_PIXEL_SCALE_FACTOR, scale_units: str = DEFAULT_SCALE_UNITS, capture_speed_in_fps=None):
        """
        Sets the properties of the Capture object.

        Args:
          pixel_scale_factor (float, optional): The pixel scale factor. Defaults to 1.
          scale_units (str, optional): The scale units. Defaults to 'units'.
          capture_speed_in_fps (int, optional): Capture speed in frames/sec. Defaults to 15.
        """
        self._pixel_scale_factor = pixel_scale_factor
        self._scale_units = scale_units
        self._actual_fps = capture_speed_in_fps

    # Private Methods
    def __capture_images_from_video(self,
                                    is_store_video_frames=False,
                                    store_images_path=DEFAULT_STORE_IMAGE_FILE_DIRECTORY):
        """
        Captures images from a video file.

        Args:
          is_store_video_frames (bool, optional): Flag to store video frames. Defaults to False.
          store_images_path (str, optional): Path to store images. Defaults to DEFAULT_STORE_IMAGE_FILE_DIRECTORY.

        Returns:
          list: The captured frames.
        """
        if is_store_video_frames:
            complete_store_path = self.__handle_folder_preprocess(store_images_path)
            self._video_frames_store_path = complete_store_path

        captured_frames = []
        video = cv2.VideoCapture(self._video_file_path)
        try:
            captured_frames = self.__capture_and_store_frames(video, is_store_video_frames)
        finally:
            video.release()

        print(f'{len(captured_frames)} frame(s) captured successfully '
              f'for the video FPS: {self._actual_fps} to the '
              f'folder: {self._video_frames_store_path}'
              )
        return captured_frames

    def __validate_the_file_name_and_type(self, file_name=''):
        """
        Validates the file name and type.

        Args:
          file_name (str, optional): The name of the file. Defaults to ''.

        Raises:
          ValueError: If the file name is empty or the file type is not supported.
        """

        self.__validate_empty_file_name(file_name)
        self.__validate_file_type(file_name)

    def __validate_empty_file_name(self, filename=''):
        """
        Checks if the file name is empty.

        Args:
          filename (str): The file name to check.

        Raises:
          ValueError: If the file name is empty.
        """
        if not filename:
            raise ValueError('Empty file name. Please provide a valid filename')

    def __validate_file_type(self, filename=''):
        """
        Checks if the file type is supported.

        Args:
          filename (str): The file name to check.

        Raises:
          ValueError: If the file type is not supported.
        """
        file_type = self.__get_file_type(filename)
        self.__is_supported_file_type(file_type)

    def __get_file_type(self, filename=''):
        """
        Retrieves the file type from the given file name.

        Args:
          filename (str): The file name.

        Returns:
          str: The file type.
        """
        return filename.split('.')[-1]

    def __is_supported_file_type(self, file_type=''):
        """
        Checks if the file type is supported.

        Args:
          file_type (str): The file type to check.

        Raises:
          ValueError: If the file type is not supported.
        """
        if file_type not in self._supported_video_file_types:
            raise ValueError(
                'Invalid file type. Please provide a valid file type')

    def __generate_and_validate_file_path(self, file_name=''):
        """
        Generates and validates the file path based on the given file name.

        Args:
          file_name (str): The file name.

        Returns:
          str: The validated file path.

        Raises:
          FileNotFoundError: If the file path does not exist.
        """
        file_path = self.__generate_file_path(file_name)
        self.__check_file_path(file_path)
        return file_path

    def __generate_file_path(self, file_name=''):
        """
        Generates the file path based on the given file name.

        Args:
          file_name (str): The file name.

        Returns:
          str: The generated file path.
        """
        return os.path.join(self._directory, file_name)

    def __check_file_path(self, file_path=''):
        """
        Checks if the file path exists.

        Args:
          file_path (str): The file path to check.

        Raises:
          FileNotFoundError: If the file path does not exist.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                'File does not exist. Please provide a valid filename')

    def __convert_fps_to_ms(self):
        """
        Converts frames per second (FPS) to milliseconds (ms).

        Returns:
          float: The converted value in milliseconds.
        """
        milliseconds_in_a_second = 1000
        round_off_decimals = 2
        return round(milliseconds_in_a_second / self._actual_fps, round_off_decimals)

    def __handle_working_directory_preprocess(self, working_directory):
        """
        Handles the preprocessing of the working directory.

        Args:
          working_directory (str): The working directory.

        Returns:
          str: The complete path of the working directory.
        """
        if not working_directory:
            user_working_dir = os.getcwd()
            working_directory = os.path.join(user_working_dir, Capture.DEFAULT_FILE_DIRECTORY)
        if not os.path.exists(working_directory):
            os.makedirs(working_directory)
        return working_directory

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

    def __print_video_info_and_get_fps(self, video):
        """
        Prints the information about the video and retrieves the frames per second (FPS).

        Args:
          video: The video object.
        """
        round_off_decimals = 2
        video_fps = video.get(cv2.CAP_PROP_FPS)
        print('---------- Video Stats ----------')
        print(f'Video Frame Width: {int(video.get(cv2.CAP_PROP_FRAME_WIDTH))}')
        print(
            f'Video Frame Height: {int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))}')
        print(f'Frame Rate: {video_fps} FPS')
        print(f'Total Frames: {video.get(cv2.CAP_PROP_FRAME_COUNT)} frames')
        print(f'Video Duration (s): {round(video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS), round_off_decimals)}')
        print('---------------------------------')
        return video_fps

    def __get_total_frames(self, video):
        """
        Retrieves the total frames of the video.

        Args:
          video: The video object.

        Returns:
          int: The total frames of the video.
        """
        return int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    def __capture_and_store_frames(self, video, is_store_video_frames=False):
        """
        Captures and stores frames from the video.

        Args:
          video: The video object.
          is_store_video_frames (bool, optional): Flag to store video frames. Defaults to False.

        Returns:
          list: The captured frames.
        """
        frame_to_capture_in_ms = 0
        frame_counter = 0
        image_path_prefix = 'frame'
        captured_frames = []
        capture_speed_in_ms = self.__convert_fps_to_ms()

        total_frames = self.__get_total_frames(video)
        with tqdm(total=total_frames, desc='Frame capture progress') as progress_bar:

            while True:
                video.set(cv2.CAP_PROP_POS_MSEC, frame_to_capture_in_ms)
                has_frame, frame = video.read()

                if not has_frame:
                    break

                if is_store_video_frames:
                    frame_counter += 1
                    frame_number = str(frame_counter).zfill(len(str(total_frames)))
                    cv2.imwrite(f'{self._video_frames_store_path}/{image_path_prefix}_{frame_number}.tiff', frame)

                captured_frames.append(frame)
                progress_bar.update(1)
                frame_to_capture_in_ms += capture_speed_in_ms

        return captured_frames

    def __extract_number_from_file_name(self, filename=''):
        """
        Extracts the number from the filename.
        Args:
          filename (str): The filename.
        Returns:
          int: The extracted number.
        """
        return int(filename.split('_')[1].split('.')[0])

    def __remove_folders_from_file_list(self, files=None, file_path=''):
        """
        Removes folders from the list of files.
        Args:
          files (list, optional): The list of files. Defaults to None.
          file_path (str): The file path.
        Returns:
          list: The filtered list of files.
        """
        if files is None:
            files = []
        return [f for f in files if os.path.isfile(os.path.join(file_path, f))]

    def __list_files(self, file_path=''):
        """
        Lists the files in the given folder.
        Args:
          file_path (str): The path of the folder.
        Returns:
          list: The list of files.
        """
        files = os.listdir(file_path)
        filtered_files = self.__remove_folders_from_file_list(files, file_path)
        sorted_files = sorted(filtered_files, key=self.__extract_number_from_file_name)
        return sorted_files
