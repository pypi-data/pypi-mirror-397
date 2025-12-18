from typing import Tuple
import cv2
import numpy as np
from ..pipeline.PipelineConfigManager import PipelineConfigManager
from .Preprocessor import Preprocessor


class ImageRoi(Preprocessor):
    def __init__(self):
        self.code = "roi"
        self.is_enabled = False
        self.normalized_points = []

    def _get_roi_points(self, config: PipelineConfigManager) -> list:
        if not self.is_enabled:
            return []
        
        return config.get_feature_config(self.code, [])

    def update_config(self, config: PipelineConfigManager):
        self.is_enabled = config.is_feature_enabled(self.code)
        self.normalized_points = self._get_roi_points(config)

    def _get_scaled_points(self, width: int, height: int) -> list:
        points = []
        for p in self.normalized_points:
            x = int(p["x"] * width)
            y = int(p["y"] * height)
            x = max(0, min(x, width))
            y = max(0, min(y, height))
            points.append((x, y))
        return points

    def apply(self, image: np.ndarray) -> np.ndarray:
        if not self.is_enabled or len(self.normalized_points) < 4:
            return image
        
        height, width = image.shape[:2]
        points = self._get_scaled_points(width, height)
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]

        roi_x = min(x_coords)
        roi_y = min(y_coords)
        roi_width = max(x_coords) - roi_x + 1 
        roi_height = max(y_coords) - roi_y + 1 

        if roi_width <= 0 or roi_height <= 0:
            return image

        cropped = image[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width].copy()
        
        if cropped.size == 0:
            return image

        mask = np.zeros(cropped.shape[:2], dtype=np.uint8)

        offset_points = [(x - roi_x, y - roi_y) for x, y in points]
        points_np = np.array(offset_points, dtype=np.int32).reshape((-1, 1, 2))

        cv2.fillPoly(mask, [points_np], 255)

        return cv2.bitwise_and(cropped, cropped, mask=mask)
    

    def revert_bboxes(self, bboxes: np.ndarray, dimension: Tuple[int, int]) -> np.ndarray:
        if not self.is_enabled or len(self.normalized_points) < 4:
            return bboxes

        height, width = dimension
        points = self._get_scaled_points(width, height)
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]

        roi_x = min(x_coords)
        roi_y = min(y_coords)

        return bboxes + np.array([roi_x, roi_y, roi_x, roi_y])