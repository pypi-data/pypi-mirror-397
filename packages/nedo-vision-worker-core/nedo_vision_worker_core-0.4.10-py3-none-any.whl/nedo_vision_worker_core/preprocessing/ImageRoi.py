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
        # We don't crop anymore, just return the image as is
        # Filtering will happen in filter_detections
        return image
    

    def revert_bboxes(self, bboxes: np.ndarray, dimension: Tuple[int, int]) -> np.ndarray:
        return bboxes
    
    def filter_detections(self, detections: list, dimension: Tuple[int, int]) -> list:
        if not self.is_enabled or len(self.normalized_points) < 4:
            return detections

        height, width = dimension
        points = self._get_scaled_points(width, height)
        points_np = np.array(points, dtype=np.int32).reshape((-1, 1, 2))

        filtered_detections = []
        for det in detections:
            bbox = det["bbox"]
            # bbox is [x1, y1, x2, y2]
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            
            # Measure distance. If >= 0, it's inside or on edge.
            result = cv2.pointPolygonTest(points_np, (center_x, center_y), False)
            if result >= 0:
                filtered_detections.append(det)
        
        return filtered_detections