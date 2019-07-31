import pydicom
import os

CWD = os.getcwd()
PROJECT_ROOT = "CQ500/CQ500CT0 CQ500CT0/Unknown Study/CT Plain/"
FULL_PATH = os.path.join(CWD, PROJECT_ROOT)


def read_image_slices(path: str) -> list:
    dicom_files = []
    slice_images: list = os.listdir(path)
    for image in slice_images:
        dicom = pydicom.dcmread(image)
        dicom_files.append(dicom)
    return dicom_files


dicom_list: list = read_image_slices(FULL_PATH)
