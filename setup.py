"""
A setup file for the 2D RABiTPy Tracker package to
track the movement of a subject in a video file.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "pypi-description.md").read_text(encoding="utf-8")

setup(
    name='RABiTPy',
    version='1.1.0',
    packages=find_packages(),
    install_requires=[
        # Add your package dependencies here
        'aicsimageio==4.14.0',
        'distfit==1.7.3',
        'ipywidgets==8.1.5',
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
    author='Indraneel Vairagare',
    author_email='indraneel207@gmail.com',
    maintainer='Samyabrata Sen, Abhishek Shrivastava',
    maintainer_email='ssen31@asu.edu, ashrivastava@asu.edu',
    description='RABiTPy: A package to track the movement of a subject in a video file.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/indraneel207/RABiTPy',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    python_requires='>=3.10, <3.11',
    keywords='tracking video analysis 2D',
    project_urls={
        'Bug Reports': 'https://github.com/indraneel207/RABiTPy/issues',
        'Source': 'https://github.com/indraneel207/RABiTPy',
    }
)
