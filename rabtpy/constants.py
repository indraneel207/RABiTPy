"""
Constants file to store the available properties and operations
"""
from enum import Enum
from typing import TypedDict, Union

class AvailableProps(Enum):
    """
    Enum to store the available properties
    """
    LABEL = 'label'
    AREA = 'area'
    CENTROID = 'centroid'
    MAJOR_AXIS_LENGTH = 'major_axis_length'
    MINOR_AXIS_LENGTH = 'minor_axis_length'
    FRAME = 'frame'

class AvailableOperations(Enum):
    """
    Enum to store the available operations
    """
    GREATER_THAN = '>'
    LESS_THAN = '<'
    EQUALS = '=='

class PropsThreshold(TypedDict):
    """
    Typed dictionary to store the property threshold
    """
    property: AvailableProps
    operation: AvailableOperations
    value: Union[int, float, str]

grayscale_channel = [0, 0] #this means segment based on first channel(gray scale), no second channel

# define parameters
OMNIPOSE_DEFAULT_PARAMS: dict = {
                'channels': grayscale_channel, # always define this with the model
                'rescale': None, # upscale or downscale your images, None = no rescaling 
                'mask_threshold': -1, # erode or dilate masks with higher or lower values 
                'flow_threshold': 0, # default is .4, but only needed if there are spurious masks to clean up; slows down output
                'transparency': True, # transparency in flow output
                'omni': True, # we can turn off Omnipose mask reconstruction, not advised 
                'cluster': True, # use DBSCAN clustering
                'resample': True, # whether or not to run dynamics on rescaled grid or original grid 
                'verbose': False, # turn on if you want to see more output 
                'tile': False, # average the outputs from flipped (augmented) images; slower, usually not needed 
                'niter': 7, # None lets Omnipose calculate # of Euler iterations (usually <20) but you can tune it for over/under segmentation 
                'augment': False, # Can optionally rotate the image and average outputs, usually not needed 
                'affinity_seg': False, # new feature, stay tuned...
            }
