from dask import delayed
import dask.array as da
import numpy as np
import napari
import skimage.io
from pathlib import Path
import sys

if __name__=='__main__':
    _, training_images_folder = sys.argv
    folder = Path(training_images_folder)
    files = folder.glob("*.tif")

    lazy_imread = delayed(skimage.io.imread)
    lazy_arrays = [lazy_imread(fn) for fn in files]
    dask_arrays = [
        da.from_delayed(
            delayed_reader, 
            shape=(640, 640),
            dtype=np.uint16,
        )
        for delayed_reader in lazy_arrays
    ]
    stack = da.stack(dask_arrays, axis=0)

    viewer = napari.view_image(stack, multiscale=False, contrast_limits=[0, 65_000], colormap='gray')
    
    napari.run()