"""
Image encoding function for the image format tasks.

The function encodes images in base64 format. It processes PNG images
from structured directories and returns them as base64-encoded strings.

The script expects:
- A specific directory structure with question-specific folders (Q1, Q2, etc.)
- PNG format images within each folder
- Four images per folder for consistency in evaluation tasks

Returns:
    List of base64-encoded strings representing the images in a given folder.
"""

import base64
import os


def encode_images_from_folder(folder_name):
    # define the folder path relative to the working directory
    folder_path = os.path.join(os.getcwd(), "../images", folder_name)

    # only PNGs are here considered valid image extensions
    valid_extensions = ".png"

    # initialize a list to store encoded images
    encoded_images = []

    # iterate over all four images in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(valid_extensions):
            image_path = os.path.join(folder_path, filename)

            # read and encode the image
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

            encoded_images.append(encoded_image)

    return encoded_images   # which will be a list of four base64-encoded images
