import logging
from typing import Dict, Optional, Set

from ..repositories.AIModelRepository import AIModelRepository
from ..detection.BaseDetector import BaseDetector
from ..detection.YOLODetector import YOLODetector
from ..detection.RFDETRDetector import RFDETRDetector
from ..models.ai_model import AIModelEntity


class ModelManager:
    """Manages loading and caching of AI models to avoid redundant loads."""

    def __init__(self):
        # Cache disabled to prevent shared state issues
        # self._detector_cache: Dict[str, BaseDetector] = {}
        self._model_repo = AIModelRepository()
        logging.info("🤖 ModelManager initialized (Cache Disabled).")

    def get_detector(self, model_id: str) -> Optional[BaseDetector]:
        """
        Retrieves a detector by its model ID.
        ALWAYS loads a new instance (Cache Disabled).
        """
        if not model_id:
            return None

        # 1. Fetch the current model state from the database
        db_model: AIModelEntity = self._model_repo.get_model(model_id)
        if not db_model:
            return None

        # Always load new detector
        return self._load_detector(model_id, db_model)

    def _load_detector(self, model_id: str, db_model: AIModelEntity) -> Optional[BaseDetector]:
        """Creates a detector from a DB model entity."""
        logging.info(f"🔄 Loading model {model_id} (version: {db_model.version}) from database...")

        # Check model readiness before attempting to load
        if not db_model.is_ready_for_use():
            if db_model.is_downloading():
                logging.warning(f"⏳ Model {model_id} is still downloading. Skipping detector load.")
            elif db_model.has_download_failed():
                logging.error(f"❌ Model {model_id} download failed: {db_model.download_error}")
            else:
                logging.warning(f"⚠️ Model {model_id} is not ready for use (status: {db_model.download_status})")
            return None

        detector_type = db_model.type.lower()
        detector: Optional[BaseDetector] = None
        try:
            if detector_type == "yolo":
                detector = YOLODetector(db_model)
            elif detector_type == "rf_detr":
                detector = RFDETRDetector(db_model)
            else:
                raise ValueError(f"Unsupported model type: {detector_type}")

            if detector and detector.model is not None:
                logging.info(f"✅ Detector for model {model_id} loaded successfully.")
                return detector
            else:
                logging.error(f"❌ Failed to load detector for model: {db_model.name}")
                return None

        except Exception as e:
            logging.error(f"❌ Error creating detector for model {db_model.name}: {e}")
            return None

    def get_model_metadata(self, model_id: str) -> Optional[AIModelEntity]:
        """Retrieves model metadata without loading the detector."""
        return self._model_repo.get_model(model_id)

    def has_metadata_changed(self, cached_model: AIModelEntity, db_model: AIModelEntity) -> bool:
        """Check if critical model metadata has changed."""
        if cached_model.version != db_model.version:
            logging.info(
                f"🔄 Model {db_model.id} version changed "
                f"({cached_model.version} -> {db_model.version})."
            )
            return True

        # Compare classes
        cached_classes = set(cached_model.get_classes() or [])
        db_classes = set(db_model.get_classes() or [])
        if cached_classes != db_classes:
            logging.info(f"🔄 Model {db_model.id} classes changed.")
            return True
        
        # Compare PPE class groups
        cached_ppe_groups = cached_model.get_ppe_class_groups() or {}
        db_ppe_groups = db_model.get_ppe_class_groups() or {}
        if cached_ppe_groups != db_ppe_groups:
            logging.info(f"🔄 Model {db_model.id} PPE groups changed.")
            return True
        
        # Compare main class
        if cached_model.get_main_class() != db_model.get_main_class():
            logging.info(f"🔄 Model {db_model.id} main class changed.")
            return True
        
        return False

    def sync_cache(self, active_model_ids: Set[str]):
        """Remove unused detectors from cache."""
        # Cache is disabled, so no sync needed.
        pass
    
    def _cleanup_detector(self, detector: BaseDetector):
        """Free detector resources and GPU memory."""
        try:
            if hasattr(detector, 'model') and detector.model is not None:
                # Move model to CPU if possible
                if hasattr(detector.model, 'cpu'):
                    try:
                        detector.model.cpu()
                    except Exception as e:
                        logging.debug(f"Error moving model to CPU: {e}")
                
                if hasattr(detector.model, 'eval'):
                    try:
                        detector.model.eval()
                    except Exception:
                        pass
                
                detector.model = None
            
            detector.metadata = None
            
            # Force garbage collection and clear GPU cache
            import gc
            gc.collect()
            
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logging.debug("🧹 GPU cache cleared")
            except ImportError:
                pass
                
        except Exception as e:
            logging.error(f"Error cleaning up detector: {e}")

    def clear_cache(self):
        """Clears the detector cache."""
        logging.info("🧹 Clearing all detectors from cache (No-op as cache is disabled).")
        # self._detector_cache.clear()
