# Microbe Vision

Microbe Vision is a comprehensive package designed to track and analyze the movement of microorganisms in video files or image sequences. This package provides tools for loading, identifying, tracking, and analyzing the movement of various organisms.

## Installation

1. First, install the package:

    ```sh
    pip install microbe_vision
    ```

2. Then, install the additional dependencies from the `requirements.txt`:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

Microbe Vision consists of four main classes:

1. **Capture**: This class is responsible for loading video files or image sequences and converting them into frames that can be processed in subsequent steps.

2. **Identify**: This class is used to identify different nodes or organisms in each frame. It provides two methods for identification:
   - **Thresholding**: A simple technique that uses pixel intensity thresholds to segment organisms.
   - **Omnipose - Masking**: A more advanced method leveraging the Omnipose algorithm for accurate segmentation of organisms.

3. **Tracker**: This class tracks each identified node across frames and filters them based on criteria such as the minimum number of frames they appear in or minimal displacement across frames. This step ensures that only meaningful tracks are retained for analysis.

4. **Stats**: This class computes various statistics about the tracked organisms, such as their speed, correlation of movements, and other relevant metrics. It records these statistics for further analysis.

### Example Workflow

A Jupyter notebook is attached to the code for the basic implementation.

## Notes:

1. **Capture**: The `Capture` class loads video files or images and converts them into a sequence of frames. These frames are then used as input for the next class in the workflow.

2. **Identify**: The `Identify` class processes each frame to detect and identify different nodes or organisms. This can be done using simple thresholding techniques or more advanced masking techniques with Omnipose. The identified nodes are passed on to the next class.

3. **Tracker**: The `Tracker` class takes the identified nodes from the `Identify` class and tracks their movement across frames. It applies filters to ensure that only nodes meeting certain criteria (e.g., minimum appearance in frames, minimal displacement) are kept. The tracking information is then passed to the `Stats` class.

4. **Stats**: The `Stats` class analyzes the tracked nodes to compute various statistics, such as speed and correlation of movement. These statistics are crucial for understanding the behavior and movement patterns of the organisms being studied.

Each class in the workflow passes its output to the next class, ensuring a seamless transition from loading and identifying organisms to tracking their movement and finally analyzing their behavior.

## Authors

- Abhishek Shrivastava
- Indraneel Vairagare

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

Special thanks to the developers of the Omnipose and Trackpy libraries, which are integral to this package's functionality.
