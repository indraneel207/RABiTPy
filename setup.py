"""
A setup file for the 2D Microbe Vision Tracker package to 
track the movement of a subject in a video file.
"""
from setuptools import setup, find_packages

setup(
    name='microbe_vision',
    version='0.1.1-alpha',
    packages=find_packages(),
    install_requires=[
        # Add your package dependencies here
        'aicsimageio==4.14.0',
        'distfit==1.7.3',
        'matplotlib==3.7.5',
        'matplotlib-inline==0.1.6',
        'numpy==1.24.4',
        'natsort==8.4.0',
        'omnipose>=1.0.6',
        'opencv-python==4.9.0.80',
        'opencv-python-headless==4.9.0.80',
        'pandas==2.1.4',
        'scikit-image==0.20.0',
        'scikit-learn==1.4.2',
        'scipy==1.13.0',
        'seaborn==0.13.2',
        'torch-optimizer==0.3.0',
        'tqdm==4.66.2',
        'trackpy==0.6.2',
    ],
    author='Abhishek Shrivastava, Samyabrata Sen, Indraneel Vairagare',
    author_email='ashrivastava@asu.edu, ssen31@asu.edu, indraneel207@gmail.com',
    description='A 2D Microbe Vision Tracker package to track the movement of a subject in a video file.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='3.10.11',
)
