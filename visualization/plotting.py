import pydicom
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage


INPUT_FOLDER = "/Users/jasonadam/Downloads/cv_medical/scans/CQ500CT111 CQ500CT111/Unknown Study/CT PLAIN/"
patients = os.listdir(INPUT_FOLDER)
patients.sort()


def load_scan(path):
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


def get_pixels_hu(scans):
    image = np.stack([s.pixel_array for s in scans])
    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.float)

    # Set outside-of-scan pixels to 1
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0

    # Convert to Hounsfield units (HU)
    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope

    if slope != 1:
        image = slope * image.astype(np.float)
        image = image.astype(np.float)

    image += np.float(intercept)

    return np.array(image, dtype=np.float)


test_patient = load_scan(INPUT_FOLDER)
len(test_patient)
test_patient_pixels = get_pixels_hu(test_patient)


# Sample Plotting
plt.hist(test_patient_pixels.flatten(), bins=40, color="c")
plt.xlabel("Hounsfield Units (HU)")
plt.ylabel("Frequency")
plt.show()

# Show some slice in the middle
plt.imshow(test_patient_pixels[13], cmap=plt.cm.gray)
plt.show()


def sample_stack(stack, rows=5, cols=5, start_with=0, show_every=1):
    fig, ax = plt.subplots(rows, cols, figsize=[12, 12])
    for i in range(rows * cols):
        ind = start_with + i * show_every
        ax[int(i / rows), int(i % rows)].set_title("slice {}".format(ind))
        ax[int(i / rows), int(i % rows)].imshow(stack[ind], cmap="gray")
        ax[int(i / rows), int(i % rows)].axis("off")
    plt.show()


plot_test_pixels = test_patient_pixels[1:26]
sample_stack(plot_test_pixels)


def normalize(image, min_bound=-1000.0, max_bound=2000):
    image = (image - min_bound) / (max_bound - min_bound)
    image[image > 1] = 1
    image[image < 0] = 0
    return image


np.max(normalize(test_patient_pixels))
np.min(normalize(test_patient_pixels))
np.mean(normalize(test_patient_pixels))

np.max(test_patient_pixels)
np.min(test_patient_pixels)


def resample(image, scan, new_spacing=[1, 1, 1]):
    spacing = [float(scan[0].SliceThickness)]
    pixel_spacing = [float(i) for i in scan[0].PixelSpacing]
    for i in pixel_spacing:
        spacing.append(i)

    spacing = np.array(spacing)

    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor

    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor, mode="nearest")

    return image


resamp_test = resample(test_patient_pixels, test_patient)
resamp_test.shape


def plot_3d(image, threshold=-300):

    # Position the scan upright,
    # so the head of the patient would be at the top facing the camera
    p = image.transpose(2, 1, 0)

    verts, faces = measure.marching_cubes(p, threshold)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")

    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces], alpha=0.70)
    face_color = [0.45, 0.45, 0.75]
    mesh.set_facecolor(face_color)
    ax.add_collection3d(mesh)

    ax.set_xlim(0, p.shape[0])
    ax.set_ylim(0, p.shape[1])
    ax.set_zlim(0, p.shape[2])

    plt.show()
