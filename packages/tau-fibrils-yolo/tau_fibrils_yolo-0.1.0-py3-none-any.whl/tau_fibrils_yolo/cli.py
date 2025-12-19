import tifffile
from pathlib import Path
import argparse
import pandas as pd


from tau_fibrils_yolo.widget import detect_fibrils
from tau_fibrils_yolo.boxes_utils import box_measurements


def process_input_file_predict(input_image_file):
    image = tifffile.imread(input_image_file)

    results = detect_fibrils.run(image)
    box_results = results.read("Tau fibrils")
    
    boxes = box_results.data
    probas = box_results.meta["features"]["probabilities"]

    centers_x = []
    centers_y = []
    lengths = []
    widths = []
    for box in boxes:
        center, length, width = box_measurements(box)
        centers_x.append(center[0])
        centers_y.append(center[1])
        lengths.append(length)
        widths.append(width)

    df = pd.DataFrame(
            {
                "probability": probas,
                "length": lengths,
                "width": widths,
                "center_x": centers_x,
                "center_y": centers_y,
            }
        )

    input_image_path = Path(input_image_file)
    out_file_name = input_image_path.parent / f"{input_image_path.stem}_results.csv"

    df.to_csv(out_file_name)

    print("Saved results to ", out_file_name)


def cli_predict_image():
    """Command-line entry point for model inference."""
    parser = argparse.ArgumentParser(description="Use this command to run inference.")
    parser.add_argument(
        "-i",
        type=str,
        required=True,
        help="Input image. Must be a TIF image file.",
    )
    args = parser.parse_args()

    process_input_file_predict(args.i)