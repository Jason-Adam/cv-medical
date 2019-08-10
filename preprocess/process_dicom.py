import pydicom
import os
import numpy as np
import matplotlib.pyplot as plt


INPUT_FOLDER = "/Users/jasonadam/Downloads/cv_medical/scans/"


def get_loaded_scans(base_path, slice_count: int = 256):
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


# test = get_loaded_scans(base_path=INPUT_FOLDER)
# for patient in test:
#     for i in patient:
#         print(i.PatientName)


def get_pixels_hu(slices: list):
    for scans in slices:
        try:
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

            yield np.array(image, dtype=np.float)
        except OSError:
            pass


# test = get_loaded_scans(base_path=INPUT_FOLDER, slice_count=32)
# arrays_test = get_pixels_hu(test)
# for i in arrays_test:
#     print(i.shape)





# Sample Plotting
plt.hist(first_patient_pixels.flatten(), bins=40, color="c")
plt.xlabel("Hounsfield Units (HU)")
plt.ylabel("Frequency")
plt.show()

# Show some slice in the middle
plt.imshow(first_patient_pixels[30], cmap=plt.cm.gray)
plt.show()


def sample_stack(stack, rows=6, cols=6, start_with=1, show_every=1):
    fig, ax = plt.subplots(rows, cols, figsize=[12, 12])
    for i in range(rows * cols):
        ind = start_with + i * show_every
        ax[int(i / rows), int(i % rows)].set_title("slice {}".format(ind))
        ax[int(i / rows), int(i % rows)].imshow(stack[ind], cmap="gray")
        ax[int(i / rows), int(i % rows)].axis("off")
    plt.show()


sample_stack(pixes_hu)
