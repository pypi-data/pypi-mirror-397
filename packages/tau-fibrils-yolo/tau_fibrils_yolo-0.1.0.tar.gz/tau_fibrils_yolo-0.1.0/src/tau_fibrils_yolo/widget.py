import os
from importlib import resources
from pathlib import Path

import imaging_server_kit as sk
import numpy as np
import pooch
from skimage.color import gray2rgb
from ultralytics import YOLO

from tau_fibrils_yolo.boxes_utils import (boxes_iou_filter,
                                          boxes_kernel_density_map,
                                          boxes_min_distance_filter,
                                          clear_border_boxes)

_MODEL = None

MODEL_DIR = Path(os.getenv("XDG_DATA_HOME", Path.home())) / ".yolo"
WEIGHTS_PATH = MODEL_DIR / "yolo_fibrils_100ep.pt"


def retrieve_model():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if WEIGHTS_PATH.exists():
        return str(WEIGHTS_PATH)

    return pooch.retrieve(
        url="https://sandbox.zenodo.org/records/99113/files/100ep.pt",
        known_hash="md5:2fc4be1e4feae93f75e335856be3083d",
        path=str(MODEL_DIR),
        fname=WEIGHTS_PATH.name,
        progressbar=True,
    )


def get_model() -> YOLO:
    global _MODEL
    if _MODEL is None:
        weights = retrieve_model()
        _MODEL = YOLO(weights)
    return _MODEL


def cast_to_rgb(image: np.ndarray) -> np.ndarray:
    """Convert an image to RGB if it is grayscale."""
    if len(image.shape) == 2:
        image = image / np.iinfo(np.uint16).max
        image = image * 255
        image = gray2rgb(image).astype(np.uint8)
    return image


@sk.algorithm(
    # parameters={"image": sk.Image(rgb=True)}
)
def _detect_fibrils_tile(image: np.ndarray, imgsz: int, iou: float, conf: float):
    """Runs the model on a tile corresponding to the model's imgsz that it was trained on."""

    # Castt the image to RGB
    image_rgb = cast_to_rgb(image)

    # Instantiate the model
    model = get_model()

    # Run the model
    result = model.predict(
        source=image_rgb,
        conf=conf,  # Confidence threshold for detections.
        iou=iou,  # Intersection over union threshold.
        augment=False,
        imgsz=imgsz,  # Square resizing to this image size
    )[0]

    probas = result.obb.conf.cpu().numpy()
    boxes = result.obb.xyxyxyxy.cpu().numpy()

    # Invert X-Y
    boxes = boxes[..., ::-1]

    n_boxes = len(boxes)

    if n_boxes > 0:
        return sk.Boxes(
            boxes, name="Boxes", meta={"features": {"probabilities": probas}}
        )
    else:
        return sk.Null(name="No boxes")


@sk.algorithm(
    name="Tau fibrils detector",
    description="YOLO model designed to detect tau fibrils in EM images.",
    parameters={
        "image": sk.Image(dimensionality=[2, 3]),
        "iou": sk.Float(
            name="IoU",
            description="Intersection over union threshold",
            min=0,
            max=1,
            default=0.5,
        ),
        "conf": sk.Float(
            name="Confidence",
            description="Confidence level for the detection",
            min=0,
            max=1,
            default=0.05,
        ),
        "color_by_probas": sk.Bool(
            name="Colorize by probability",
            description="Whether to display the detected boxes with a colormap corresponding to detection probability",
            default=True,
        ),
    },
    samples=[
        {
            "image": resources.files("tau_fibrils_yolo").joinpath("sample/sample.tif")
        }
    ]
)
def detect_fibrils(image, iou, conf, color_by_probas):
    model = get_model()
    imgsz = model.args.get("imgsz", 640)

    results = _detect_fibrils_tile.run(
        image, imgsz, iou, conf, tiled=True, tile_size_px=imgsz, overlap_percent=0.1
    )

    boxes_result = results.read("Boxes")
    if boxes_result is None:
        return sk.Notification("No fibrils detected.")

    boxes = boxes_result.data

    probas = boxes_result.meta["features"]["probabilities"]

    boxes, probas = clear_border_boxes(boxes, probas=probas)

    if len(boxes):
        meta = {
            "features": {"probabilities": probas},
            "opacity": 1.0,
            "edge_width": 2,
            "face_color": "#ff000022",
            "edge_color": "#ff0000",
        }
        if color_by_probas:
            meta["face_color"] = "transparent"
            meta["edge_color"] = "probabilities"
        return sk.Boxes(boxes, name="Tau fibrils", meta=meta)
    else:
        return sk.Notification("No fibrils detected.")


@sk.algorithm(
    name="Min distance",
    description="Minimum distance filter for detection boxes",
    parameters={
        "boxes": sk.Boxes(),
        "min_dist_px": sk.Integer(
            name="Min distance", description="Minimum distance in pixels", default=5
        ),
    },
    tileable=False,
)
def min_distance_boxes(boxes, min_dist_px):
    boxes = boxes_min_distance_filter(boxes, min_dist_px=min_dist_px)
    n_boxes = len(boxes)
    if n_boxes > 0:
        meta = {
            "opacity": 1.0,
            "edge_width": 2,
            "face_color": "#ff000022",
            "edge_color": "#ff0000",
        }
        return (
            sk.Boxes(boxes, name="Filtered", meta=meta),
            sk.String(f"{n_boxes} boxes."),
        )
    else:
        return sk.Notification("No fibrils remaining.")


@sk.algorithm(
    name="Max IoU",
    description="Maximum IoU filter for detection boxes",
    parameters={
        "boxes": sk.Boxes(),
        "max_iou": sk.Float(
            name="Max IoU",
            description="Maximum IoU",
            min=0.0,
            max=1.0,
            default=0.5,
        ),
    },
    tileable=False,
)
def max_iou_boxes(boxes, max_iou):
    boxes = boxes_iou_filter(boxes, max_iou)
    n_boxes = len(boxes)
    if n_boxes > 0:
        meta = {
            "opacity": 1.0,
            "edge_width": 2,
            "face_color": "#ff000022",
            "edge_color": "#ff0000",
        }
        return (
            sk.Boxes(boxes, name="Filtered", meta=meta),
            sk.String(f"{n_boxes} boxes."),
        )
    else:
        return sk.Notification("No fibrils remaining.")


@sk.algorithm(
    name="Kernel density",
    description="Compute a kernel density image from box coordinates.",
    parameters={
        "boxes": sk.Boxes(),
        "image": sk.Image(dimensionality=[2, 3]),
        "gaussian_sigma_px": sk.Integer(
            name="Sigma",
            description="Scale at which to compute the density estimate",
            default=50,
            min=1,
        ),
        "downscale_factor": sk.Integer(
            name="Downscale factor",
            description="Factor used to downscale the image before computing the density estimate.",
            default=8,
            min=1,
            step=2,
        ),
    },
    tileable=False,
)
def boxes_kernel_density(boxes, image, gaussian_sigma_px, downscale_factor):
    density_map = boxes_kernel_density_map(
        boxes, image, gaussian_sigma_px, downscale_factor
    )
    dmin = density_map.min()
    dmax = density_map.max()
    return sk.Image(
        density_map,
        meta={"colormap": "viridis", "contrast_limits": [dmin, dmax], "opacity": 0.5},
    )
