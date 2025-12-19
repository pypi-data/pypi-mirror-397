import pandas as pd
import skimage.io
from pathlib import Path
import sys

if __name__ == "__main__":
    _, shapes_file, training_images_folder = sys.argv
    
    # All the crops should be in the training image folder already
    image_files = list(Path(training_images_folder).iterdir())
    df = pd.read_csv(shapes_file).drop(columns=['shape-type', 'vertex-index'])
    image_shapes = [skimage.io.imread(image_file).shape for image_file in image_files]

    print(len(image_files))
    print(len(image_shapes))

    for axis_zero, (image_file, [rx, ry]) in enumerate(zip(image_files, image_shapes)):
        label_out_path = image_file.parents[1] / 'labels' / f"{image_file.stem}.txt"

        sub_df = df[df['axis-0'] == axis_zero]
        if len(sub_df) == 0:
            pd.DataFrame({}).to_csv(label_out_path, header=None, index=None, sep=' ', mode='w')
        else:
            with open(label_out_path, 'w') as f:
                polygon_indeces = sub_df['index'].unique().tolist()
                for polygon_idx in polygon_indeces:
                    polygon_df = df[df['index'] == polygon_idx]
                    polygon_coords_x_normed = polygon_df['axis-1'].to_numpy() / rx
                    polygon_coords_y_normed = polygon_df['axis-2'].to_numpy() / ry
                    line = "0" + f"".join(f" {y:.3f} {x:.3f}" for x, y in zip(polygon_coords_x_normed, polygon_coords_y_normed)) + "\n"
                    f.write(line)
                
                print("Saved ", label_out_path)