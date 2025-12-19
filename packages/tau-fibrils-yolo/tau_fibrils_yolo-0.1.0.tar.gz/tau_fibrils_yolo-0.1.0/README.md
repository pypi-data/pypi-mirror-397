![EPFL Center for Imaging logo](https://imaging.epfl.ch/resources/logo-for-gitlab.svg)
# 🧬 Tau Fibrils Yolo - Object detection in EM images

![screenshot](assets/screenshot.png)

We provide a [YoloV8](https://docs.ultralytics.com/) model for the detection of oriented bounding boxes (OBBs) of Tau fibrils in EM images. The model is integrated as a [Napari](https://napari.org/stable/) plugin.

[[`Installation`](#installation)] [[`Model`](#model)] [[`Usage`](#usage)] [[`Training`](#training)]

This project is part of a collaboration between the [EPFL Center for Imaging](https://imaging.epfl.ch/) and the [Laboratory of Biological Electron Microscopy](https://www.lbem.ch/).

## Installation

We recommend performing the installation in a clean Python environment. Install the package from PyPi:

```sh
pip install tau-fibrils-yolo
```

or from the repository:

```sh
pip install git+https://gitlab.com/center-for-imaging/tau-fibrils-object-detection.git
```

or clone the repository and install with:

```sh
git clone https://github.com/EPFL-Center-for-Imaging/tau-fibrils-yolo.git
cd tau-fibrils-yolo
pip install -e .
```

## Usage

**In Napari**

To use the model in Napari, start the viewer with

```sh
napari -w tau-fibrils-yolo
```

or open the plugin from `Plugins > Tau fibrils detection`.

**From the command-line**

Run inference on an image from the command-line:

```sh
tau_fibrils_predict_image -i /path/to/folder/image_001.tif
```

This command will run the YOLO model and save a CSV file containing measurements next to the image:

```
folder/
    ├── image_001.tif
    ├── image_001_results.csv
```

## Training

The instructions for training the model can be found [here](./scripts/instructions.md).

## Issues

If you encounter any problems, please file an issue along with a detailed description.

## License

This project is licensed under the [AGPL-3](LICENSE) license.

This project depends on the [ultralytics](https://github.com/ultralytics/ultralytics) package which is licensed under AGPL-3.

## Acknowledgements

We would particularly like to thank **Valentin Vuillon** for annotating the images on which this model was trained, and for developing the preliminary code that laid the foundation for this image analysis project. The repository containing his original version of the project can be found [here](https://gitlab.com/epfl-center-for-imaging/automated-analysis-tau-fibrils-project).