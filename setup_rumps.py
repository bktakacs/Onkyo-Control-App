# SETUP FOR RUMPS STATUS BAR ICON ONKYO CONTROLS

from setuptools import setup

APP = ['rumps_test.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps, '],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
