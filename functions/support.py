import os
import sys

def cwdpath(relative_path):

    try:
        base_path = sys._MEIPASS  # PyInstaller's internal temp directory
    except AttributeError:
        base_path = os.getcwd()   # Current working directory for development

    # Construct full path using os.path.join
    return os.path.join(base_path, relative_path)