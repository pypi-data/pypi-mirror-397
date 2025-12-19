from tau_fibrils_yolo.widget import (
    detect_fibrils,
    max_iou_boxes,
    min_distance_boxes,
    boxes_kernel_density,
)

from qtpy.QtWidgets import QWidget
import imaging_server_kit as sk


class YoloDetectorWidget(QWidget):
    def __init__(self, viewer):
        super().__init__()
        multi = sk.combine(
            [detect_fibrils, max_iou_boxes, min_distance_boxes, boxes_kernel_density],
            name="Tau fibrils analysis",
        )
        widget = sk.to_qwidget(multi, viewer)
        self.setLayout(widget.layout())


from ._version import version as __version__

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
