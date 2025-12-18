"""Setup script for hsntools."""

import os
from setuptools import setup, find_packages

# Get the current version number from inside the module
with open(os.path.join('hsntools', 'version.py')) as version_file:
    exec(version_file.read())

# Load the long description from the README
with open('README.rst') as readme_file:
    long_description = readme_file.read()

# Load the required dependencies from the requirements file
with open("requirements.txt") as requirements_file:
    install_requires = requirements_file.read().splitlines()

setup(
    name = 'hsntools',
    version = __version__,
    description = 'Code for working with the Human Single-Neuron Pipeline.',
    long_description = long_description,
    long_description_content_type = 'text/x-rst',
    python_requires = '>=3.7',
    packages = find_packages(),
    license = 'MIT License',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ],
    platforms = 'any',
    project_urls = {
        'Documentation' : 'https://hsnpipeline.github.io/hsntools/',
        'Bug Reports' : 'https://github.com/HSNPipeline/hsntools/issues',
        'Source' : 'https://github.com/HSNPipeline/hsntools',
    },
    download_url = 'https://github.com/HSNPipeline/hsntools/releases',
    keywords = ['neuroscience', 'single units', 'data management', 'neurodata without borders'],
    install_requires = install_requires,
    tests_require = ['pytest'],
    extras_require = {
        'plot' : ['matplotlib'],
        'timestamps' : ['scipy', 'scikit-learn'],
        'nwb' : ['h5py', 'pynwb'],
        'files' : ['scipy', 'pandas', 'h5py', 'pynwb', 'neo', 'mat73'],
        'tests' : ['pytest'],
        'all' : ['matplotlib', 'scipy', 'scikit-learn', 'pandas', 'h5py', 'pynwb', 'neo', 'mat73', 'pytest'],
    }
)