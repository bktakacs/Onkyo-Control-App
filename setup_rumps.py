# SETUP FOR RUMPS STATUS BAR ICON ONKYO CONTROLS
import os

from setuptools import setup
from setuptools import find_packages

APP = ['rumps_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'on.jpg',
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps', 'pynput'],
}

setup(
    name='OnkyoControlApp',
    app=APP,
    author='Ben Takacs',
    data_files=DATA_FILES,
    version='1.01',
    options={'py2app': OPTIONS},
    packages=find_packages(),
    setup_requires=['py2app'],
)

# then run in the terminal:
# python setup_rumps.py py2app