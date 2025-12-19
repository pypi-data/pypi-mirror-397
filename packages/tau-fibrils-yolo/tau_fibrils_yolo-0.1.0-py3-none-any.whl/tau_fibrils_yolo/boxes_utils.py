from typing import Any, Optional

import cv2
import numpy as np
from numpy.linalg import norm
from scipy.ndimage import zoom
from scipy.spatial import distance_matrix
from sklearn.neighbors import KernelDensity


def boxes_min_distance_filter(
    boxes, min_dist_px=5, probas: Optional[np.ndarray] = None
) -> Any:
    """Returns a filter matching objects isolated by less than min_dist_px pixels."""
    centers = boxes_centers(boxes)
    dist_matrix = distance_matrix(centers, centers)
    np.fill_diagonal(dist_matrix, np.inf)
    filt = np.min(dist_matrix, axis=1) > min_dist_px
    if probas is not None:
        return boxes[filt], probas[filt]
    else:
        return boxes[filt]


def boxes_iou_filter(
    boxes: np.ndarray, max_iou: float = 0.0, probas: Optional[np.ndarray] = None
) -> Any:
    """Removes boxes based on an intersection over union threshold."""
    keep = []
    for i, box_i in enumerate(boxes):
        should_keep_i = True
        box_i = boxes[i]
        for j in keep:
            box_j = boxes[j]
            intersection, _ = cv2.intersectConvexConvex(box_i, box_j)
            area_i = cv2.contourArea(box_i)
            area_j = cv2.contourArea(box_j)
            union = area_i + area_j - intersection
            iou = intersection / union
            if iou >= max_iou:
                should_keep_i = False
                break
        if should_keep_i:
            keep.append(i)

    if probas is not None:
        return boxes[keep], probas[keep]
    else:
        return boxes[keep]


def clear_border_boxes(boxes: np.ndarray, probas: Optional[np.ndarray] = None) -> Any:
    """Removes boxes touching the image border."""
    filt = ~(boxes < 0).any(axis=2).any(axis=1)
    if probas is not None:
        return boxes[filt], probas[filt]
    else:
        return boxes[filt]


def boxes_centers(boxes: np.ndarray) -> np.ndarray:
    """Returns the center coordinates of the boxes."""
    box_cy = (np.max(boxes[..., 1], axis=1) + np.min(boxes[..., 1], axis=1)) / 2
    box_cx = (np.max(boxes[..., 0], axis=1) + np.min(boxes[..., 0], axis=1)) / 2
    box_centers = np.vstack((box_cx, box_cy)).T
    return box_centers


def boxes_kernel_density_map(boxes, image, gaussian_sigma_px=50, downscale_factor=8):
    """Returns a kernel density image from box coordinates."""
    grid_size_x = image.shape[0] // downscale_factor
    grid_size_y = image.shape[1] // downscale_factor

    x_grid, y_grid = np.meshgrid(
        np.linspace(0, grid_size_y - 1, grid_size_y),
        np.linspace(0, grid_size_x - 1, grid_size_x),
    )

    grid_points = np.vstack([y_grid.ravel(), x_grid.ravel()]).T

    kde = KernelDensity(
        bandwidth=gaussian_sigma_px, kernel="gaussian", algorithm="ball_tree"
    )

    kde.fit(boxes_centers(boxes) / downscale_factor)

    density_map = np.exp(kde.score_samples(grid_points)).reshape(
        (grid_size_x, grid_size_y)
    )
    density_map = zoom(density_map, zoom=downscale_factor, order=1)

    return density_map


def box_measurements(box):
    """Returns the center, length, and width of an oriented bounding box."""
    p0, p1, p2, p3 = box

    if norm(p2 - p0) < norm(p1 - p0):
        p0, p3, p2, p1 = box

    p5 = p0 + (p1 - p0) / 2
    p6 = p3 + (p2 - p3) / 2

    width = norm(p1 - p0)
    length = norm(p2 - p0)

    diagonal = p6 - p5
    center = p5 + diagonal / 2

    return center, length, width
