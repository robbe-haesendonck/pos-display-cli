#!/usr/bin/env python3

"""Setup module."""
from setuptools import setup, find_packages
import os


def read(fname):
    """Read and return the contents of a file."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pos-display-cli',
    version='0.0.2',
    description='pos-display-cli is a command-line utility for printing to a pos display',
    long_description=read('README.md'),
    author='Kalman Olah',
    author_email='kalman@inuits.eu',
    url='https://github.com/kalmanolah/pos-display-cli',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'simplejson',
        'unidecode',
        'pyserial',
        'loguru'
    ],
    entry_points={
        'console_scripts': [
            'pos-display-cli = pos_display_cli:main',
        ]
    },
)
