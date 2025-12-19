import napari
from tau_fibrils_yolo import YoloDetectorWidget, __version__

if __name__ == "__main__":
    viewer = napari.Viewer(title=f"Tau Fibrils Yolo ({__version__})")
    viewer.window.add_dock_widget(YoloDetectorWidget(viewer), name="Tau Fibrils Yolo")
    napari.run()
