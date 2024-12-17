# RABiTPy - Rapid Artificially Intelligent Bacterial Tracker

RABiTPy is a comprehensive package designed to track and analyze the movement of micro-organisms in video files or image sequences. This package provides tools for loading, identifying, tracking, and analyzing the movement of various organisms.

## Features

- **Capture**: Load video files or image sequences and convert them into frames.
- **Identify**: Detect and identify microorganisms using thresholding or advanced Omnipose masking.
- **Tracker**: Track identified organisms across frames, applying filters to retain meaningful tracks.
- **Stats**: Analyze tracked organisms to calculate speed, movement patterns, and other metrics.

## Installation

***NOTE: Use the python version 3.10.11***

1. First, install the package:

    ```sh
    pip install RABiTPy
    ```

2. Use this specific command to install the Omnipose

    ```sh
    pip install git+https://github.com/kevinjohncutler/omnipose.git@63045b1af0d52174dee7ff18e94c7cfd84ddd2ff
    ````

## Usage

RABiTPy consists of four main classes:

1. **Capture**: This class is responsible for loading video files or image sequences and converting them into frames that can be processed in subsequent steps.

2. **Identify**: This class is used to identify different nodes or organisms in each frame. It provides two methods for identification:
   - **Thresholding**: A simple technique that uses pixel intensity thresholds to segment organisms.
   - **AI-based Masking**: A more advanced method leveraging the AI-based(Omnipose) algorithm for accurate segmentation of organisms.

3. **Tracker**: This class tracks each identified node across frames and filters them based on criteria such as the minimum number of frames they appear in or minimal displacement across frames. This step ensures that only meaningful tracks are retained for analysis.

4. **Stats**: This class computes various statistics about the tracked organisms, such as their speed, correlation of movements, and other relevant metrics. It records these statistics for further analysis.

## Documentation

For detailed usage and examples, refer to the documentation for each class:

- [Capture Class Documentation](documentation/capture.md)
- [Identify Class Documentation](documentation/identify.md)
- [Tracker Class Documentation](documentation/track.md)
- [Stats Class Documentation](documentation/stats.md)

### Example Workflow

A Jupyter notebook with the basic implementationis can be found [here](walkthrough.ipynb).

## Notes

1. **Capture**: The `Capture` class loads video files or images and converts them into a sequence of frames. These frames are then used as input for the next class in the workflow.

2. **Identify**: The `Identify` class processes each frame to detect and identify different nodes or organisms. This can be done using simple thresholding techniques or more advanced masking techniques with Omnipose. The identified nodes are passed on to the next class.

3. **Tracker**: The `Tracker` class takes the identified nodes from the `Identify` class and tracks their movement across frames. It applies filters to ensure that only nodes meeting certain criteria (e.g., minimum appearance in frames, minimal displacement) are kept. The tracking information is then passed to the `Stats` class.

4. **Stats**: The `Stats` class analyzes the tracked nodes to compute various statistics, such as speed and correlation of movement. These statistics are crucial for understanding the behavior and movement patterns of the organisms being studied.

Each class in the workflow passes its output to the next class, ensuring a seamless transition from loading and identifying organisms to tracking their movement and finally analyzing their behavior.

## Authors

- Indraneel Vairagare (indraneel207@gmail.com)
- Samyabrata Sen (ssen31@asu.edu)
- Abhishek Shrivastava (ashrivastava@asu.edu)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

We extend our thanks to the developers of the Omnipose and Trackpy libraries, which are essential to the functionality of this package.
