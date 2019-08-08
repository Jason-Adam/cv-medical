import pydicom
import os

import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt

from skimage import measure, morphology

INPUT_FOLDER = "/Users/jasonadam/Downloads/cv_medical/scans/"
SCAN_PATH = "CQ500CT100 CQ500CT100/Unknown Study/CT Plain 3mm/"

TEST_PATH = os.path.join(INPUT_FOLDER, SCAN_PATH)
scans = os.listdir(TEST_PATH)
patient_100 = os.listdir(os.path.join(TEST_PATH, scans[0]))
patient_100.sort()

patient_100

all_scans = []
for ct in os.listdir(INPUT_FOLDER):
    list_scans = []
    images_path = os.path.join(INPUT_FOLDER, ct + "/" + "Unknown Study/")
    list_scans.append(os.listdir(images_path))
    all_scans.append(list_scans)

all_scans


def load_scan(path: str):
    slices = [pydicom.read_file(path + s) for s in os.listdir(path)]
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(
            slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2]
        )
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)

    for s in slices:
        s.SliceThickness = slice_thickness

    return slices


test_scan = load_scan(TEST_PATH)

test_scan[0]


def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0

    # Convert to Hounsfield units (HU)
    for slice_number in range(len(slices)):

        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope

        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)

        image[slice_number] += np.int16(intercept)

    return np.array(image, dtype=np.int16)


pixes_hu = get_pixels_hu(test_scan)
pixes_hu.shape

first_patient_pixels = pixes_hu
plt.hist(first_patient_pixels.flatten(), bins=40, color="c")
plt.xlabel("Hounsfield Units (HU)")
plt.ylabel("Frequency")
plt.show()

# Show some slice in the middle
plt.imshow(first_patient_pixels[19], cmap=plt.cm.gray)
plt.show()


def sample_stack(stack, rows=10, cols=5, start_with=0, show_every=1):
    fig, ax = plt.subplots(rows, cols, figsize=[12, 12])
    for i in range(rows * cols):
        ind = start_with + i * show_every
        ax[int(i / rows), int(i % rows)].set_title("slice {}".format(ind))
        ax[int(i / rows), int(i % rows)].imshow(stack[ind], cmap="gray")
        ax[int(i / rows), int(i % rows)].axis("off")
    plt.show()
