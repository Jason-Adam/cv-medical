import pydicom
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
import scipy.ndimage

INPUT_FOLDER = "/Users/jasonadam/Downloads/cv_medical/scans/"
SAVE_FOLDER = "/Users/jasonadam/Downloads/cv_medical/processed_arrays/"
LABELS_PATH = "/Users/jasonadam/Downloads/cv_medical/ich_reads.csv"

labels = pd.read_csv(LABELS_PATH)
labels.head()

slice_counts = []
for ct in os.listdir(INPUT_FOLDER):
    images_path = os.path.join(INPUT_FOLDER, ct + "/" + "Unknown Study/")
    list_scans = os.listdir(images_path)

    for scan_folders in list_scans:
        slice_path = os.path.join(images_path, scan_folders + "/")
        slices = os.listdir(slice_path)
        slice_counts.append(len(slices))

plt.hist(slice_counts)
counts = Counter(slice_counts)
counts.most_common(1)


def get_loaded_scans(base_path, slice_count: int = 32):
    for ct in os.listdir(base_path):
        images_path = os.path.join(base_path, ct + "/" + "Unknown Study/")
        list_scans = os.listdir(images_path)

        for scan_folders in list_scans:
            slice_path = os.path.join(images_path, scan_folders + "/")
            slices = os.listdir(slice_path)
            if len(slices) != slice_count:
                continue
            else:
                slices.sort()
                yield list([pydicom.read_file(os.path.join(slice_path, s)) for s in slices])


test = get_loaded_scans(base_path=INPUT_FOLDER)
patient_ids = []
for patient in test:
    patient_ids.append(patient[0].PatientName)

patient_ids = [str(i) for i in patient_ids] 
patient_ids = pd.DataFrame(patient_ids)
patient_ids

labels = labels[labels["patient_id"].isin(patient_ids)].reset_index()
labels.drop(columns="index", inplace=True, axis=1)
labels


def get_pixels_hu(slices: list):
    for scans in slices:
        try:
            patient_id = str(scans[0].PatientName)
            image = np.stack([s.pixel_array for s in scans])
            image = image.astype(np.float)
            # Set outside-of-scan pixels to 0
            # The intercept is usually -1024, so air is approximately 0
            image[image == -2000] = 0

            # Convert to Hounsfield units (HU)
            for slice_number in range(len(scans)):

                intercept = scans[slice_number].RescaleIntercept
                slope = scans[slice_number].RescaleSlope

                if slope != 1:
                    image[slice_number] = slope * image[slice_number]

                image[slice_number] += np.float(intercept)

            yield np.array(image, dtype=np.float), patient_id
        except:
            pass


test = get_loaded_scans(base_path=INPUT_FOLDER, slice_count=32)
arrays_test = get_pixels_hu(test)

for stack, patient_name, scans in arrays_test:
    print(stack.shape, patient_name, scans[0].SliceThickness)

len(os.listdir(SAVE_FOLDER))


def normalize_stacks(image, min_bound=-1000.0, max_bound=2000.0):
    image = (image - min_bound) / (max_bound - min_bound)
    image[image > 1] = 1
    image[image < 0] = 0
    return image

from skimage.transform import rescale

test = get_loaded_scans(base_path=INPUT_FOLDER, slice_count=32)
arrays_test = get_pixels_hu(test)
for i, j in arrays_test:
    normalized = scipy.ndimage.interpolation.zoom(i, (0.25, 0.25, 0.25), mode="nearest")
    normalized = normalize_stacks(normalized)
    normalized = normalized - np.mean(normalized)
    np.save(os.path.join(SAVE_FOLDER, j), normalized)


os.listdir(SAVE_FOLDER)
