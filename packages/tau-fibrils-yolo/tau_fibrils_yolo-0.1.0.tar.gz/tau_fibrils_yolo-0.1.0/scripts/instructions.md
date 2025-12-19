# YoloV8 - OBB Training instructions

Make sure to run all the scripts in a Python environment with `napari` and `ultralytics` installed.

## Step 1: Create a training data folder and subfolders

Create the following folder organization:

```
data/
    ├── train/
        ├── images/
        ├── labels/
    ├── valid/
        ├── images/
        ├── labels/
    ├── test/
        ├── images/
        ├── labels/
```

## Step 2: Extract and save crops from the original images

Save them under the `data/train/images/` folder you've created.

## Step 3: Annotate the crops with oriented bounding boxes (OBBs) in Napari

Run the script, and give it a path to the training images (the crops) as argument.

```
python 00_annotate.py /path/to/data/train/images/
```

## Step 4: Save the OBBs as CSV

Annotate the bounding boxes in a `Shapes` layer, and save the layer (`File > Save selected layer`).

- Save regularly for "safety", so that you don't risk losing all your annotations in the program crashes, or if something goes wrong. You can reload the shapes layer by drag-and-dropping the CSV file into Napari.
- **Do not** modify (delete, add files, etc.) the images under `data/train/images` after you started the annotation process and until you finish it. This is because the order of the files matters to assign the bounding boxes to the correct image.

## Step 5: Convert the `Shapes.csv` to Yolo labels

Run the script with the saved Shapes layer file and the training images folder as arguments:

```
python 01_shapes_to_labels.py /path/to/Shapes.csv /path/to/data/train/images/
```

This will fill-in the `data/train/labels` folder with one `.txt` file per image in the Yolo format.

## Step 6: Split the data into training/validation sets

For this, we just randomly move a fraction of the files from `data/train` to `data/valid`. Run the script:

```
python 02_split_train_valid.py /path/to/data/ 0.2
```

to move 20% of the image files and yolo labels to `/data/valid`.

## Step 7: Edit `data.yaml`

Set the correct absolute `path` to your `data/` folder in the `data.yaml` file that Yolo uses to find the data for training.

## Step 8: Train the model

First, you may want to edit the training parameters to your liking in `03_train_yolo.py`. Also, change the absolute path to `PRETRAINED_MODEL_FILE`. Yolo will download and save a small (~6 Mb) pre-trained model in it when you start the training.

Run the script with the `data.yaml` file as argument.

```
python 03_train_yolo.py /path/to/data.yaml
```

It's probably good to train for ~1000 epochs with a single GPU, which should take around 1-2 hours.

All the results, including the model weights, will be saved in an output folder named `output/`.