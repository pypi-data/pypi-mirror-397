import sys
import shutil
import numpy as np
from pathlib import Path

if __name__ == '__main__':
    _, data_folder, valid_fraction = sys.argv
    valid_fraction = float(valid_fraction)

    train_folder = Path(data_folder) / 'train'
    valid_folder = Path(data_folder) / 'valid'

    all_files = list((train_folder / 'labels').glob('*.txt'))

    n_files = len(all_files)
    print(f"{n_files=}")

    n_val = int(n_files * valid_fraction)
    print(f"{n_val=}")
    
    shuffled_idx = np.arange(n_files)
    np.random.shuffle(shuffled_idx)
    valid_idx = shuffled_idx[:n_val]
    train_idx = shuffled_idx[n_val:]

    for idx, file in enumerate(all_files):
        if idx in valid_idx:
            image_file = train_folder / 'images' / f"{file.stem}.tif"
            shutil.move(file, valid_folder / 'labels')
            shutil.move(image_file, valid_folder / 'images')