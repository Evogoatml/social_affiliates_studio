"""
Model Manager
Manages trained models, versioning, and deployment
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ModelManager:
    """
    Manages AI models: loading, saving, versioning, deployment
    """
    
    def __init__(self):
        """Initialize model manager"""
        self.logger = logging.getLogger(__name__)
        self.models_dir = Path("ml/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry_file = self.models_dir / "model_registry.json"
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load model registry from disk"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {'models': [], 'active_model': None}
    
    def _save_registry(self):
        """Save model registry to disk"""
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(
        self,
        model_path: str,
        name: str,
        description: str = "",
        metrics: Optional[Dict] = None
    ) -> str:
        """
        Register a trained model
        
        Args:
            model_path: Path to model files
            name: Model name
            description: Model description
            metrics: Training/evaluation metrics
            
        Returns:
            Model ID
        """
        model_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        model_entry = {
            'id': model_id,
            'name': name,
            'description': description,
            'path': model_path,
            'metrics': metrics or {},
            'registered_at': datetime.now().isoformat(),
            'status': 'registered'
        }
        
        self.registry['models'].append(model_entry)
        self._save_registry()
        
        self.logger.info(f"✅ Model registered: {model_id}")
        return model_id
    
    def set_active_model(self, model_id: str):
        """
        Set a model as active for production use
        
        Args:
            model_id: Model identifier
        """
        # Find model
        model = next((m for m in self.registry['models'] if m['id'] == model_id), None)
        
        if not model:
            self.logger.error(f"❌ Model not found: {model_id}")
            return
        
        # Update status
        for m in self.registry['models']:
            if m['id'] == model_id:
                m['status'] = 'active'
            elif m['status'] == 'active':
                m['status'] = 'inactive'
        
        self.registry['active_model'] = model_id
        self._save_registry()
        
        self.logger.info(f"✅ Active model set to: {model_id}")
    
    def get_active_model(self) -> Optional[Dict]:
        """
        Get currently active model
        
        Returns:
            Model metadata or None
        """
        if not self.registry['active_model']:
            return None
        
        return next(
            (m for m in self.registry['models'] if m['id'] == self.registry['active_model']),
            None
        )
    
    def list_models(self, status: Optional[str] = None) -> List[Dict]:
        """
        List all registered models
        
        Args:
            status: Filter by status (active, inactive, registered)
            
        Returns:
            List of model metadata
        """
        models = self.registry['models']
        
        if status:
            models = [m for m in models if m.get('status') == status]
        
        return models
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """
        Get detailed information about a model
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model metadata or None
        """
        return next(
            (m for m in self.registry['models'] if m['id'] == model_id),
            None
        )
    
    def delete_model(self, model_id: str, delete_files: bool = False):
        """
        Delete a model from registry (optionally delete files)
        
        Args:
            model_id: Model identifier
            delete_files: Whether to delete model files from disk
        """
        model = self.get_model_info(model_id)
        
        if not model:
            self.logger.error(f"❌ Model not found: {model_id}")
            return
        
        # Remove from registry
        self.registry['models'] = [
            m for m in self.registry['models'] if m['id'] != model_id
        ]
        
        # Update active model if deleted
        if self.registry['active_model'] == model_id:
            self.registry['active_model'] = None
        
        self._save_registry()
        
        # Delete files if requested
        if delete_files:
            model_path = Path(model['path'])
            if model_path.exists():
                shutil.rmtree(model_path)
                self.logger.info(f"🗑️ Deleted model files: {model_path}")
        
        self.logger.info(f"✅ Model deleted from registry: {model_id}")
    
    def compare_models(self, model_ids: List[str]) -> Dict:
        """
        Compare metrics across multiple models
        
        Args:
            model_ids: List of model identifiers
            
        Returns:
            Comparison data
        """
        comparison = {
            'models': [],
            'metrics': {}
        }
        
        for model_id in model_ids:
            model = self.get_model_info(model_id)
            if model:
                comparison['models'].append({
                    'id': model['id'],
                    'name': model['name'],
                    'metrics': model.get('metrics', {})
                })
        
        # Aggregate metrics
        if comparison['models']:
            metric_keys = set()
            for model in comparison['models']:
                metric_keys.update(model['metrics'].keys())
            
            for key in metric_keys:
                comparison['metrics'][key] = [
                    model['metrics'].get(key, None)
                    for model in comparison['models']
                ]
        
        return comparison
    
    def export_model_for_deployment(self, model_id: str, output_path: str):
        """
        Export model for deployment (e.g., to production server)
        
        Args:
            model_id: Model identifier
            output_path: Destination path
        """
        model = self.get_model_info(model_id)
        
        if not model:
            self.logger.error(f"❌ Model not found: {model_id}")
            return
        
        try:
            model_path = Path(model['path'])
            output_path = Path(output_path)
            
            # Copy model files
            shutil.copytree(model_path, output_path, dirs_exist_ok=True)
            
            # Add deployment metadata
            deployment_info = {
                'model_id': model_id,
                'model_name': model['name'],
                'exported_at': datetime.now().isoformat(),
                'metrics': model.get('metrics', {}),
                'deployment_version': '1.0'
            }
            
            with open(output_path / 'deployment_info.json', 'w') as f:
                json.dump(deployment_info, f, indent=2)
            
            self.logger.info(f"✅ Model exported to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Error exporting model: {e}")
    
    def get_best_model(self, metric: str = 'eval_loss', minimize: bool = True) -> Optional[Dict]:
        """
        Get best model based on a specific metric
        
        Args:
            metric: Metric to compare (e.g., 'eval_loss', 'accuracy')
            minimize: True if lower is better, False if higher is better
            
        Returns:
            Best model metadata or None
        """
        models_with_metric = [
            m for m in self.registry['models']
            if metric in m.get('metrics', {})
        ]
        
        if not models_with_metric:
            return None
        
        best_model = min(
            models_with_metric,
            key=lambda m: m['metrics'][metric] if minimize else -m['metrics'][metric]
        )
        
        return best_model
    
    def create_model_checkpoint(self, model_id: str) -> str:
        """
        Create a backup checkpoint of a model
        
        Args:
            model_id: Model identifier
            
        Returns:
            Checkpoint path
        """
        model = self.get_model_info(model_id)
        
        if not model:
            self.logger.error(f"❌ Model not found: {model_id}")
            return ""
        
        try:
            model_path = Path(model['path'])
            checkpoint_name = f"{model_id}_checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            checkpoint_path = self.models_dir / "checkpoints" / checkpoint_name
            checkpoint_path.parent.mkdir(exist_ok=True)
            
            shutil.copytree(model_path, checkpoint_path)
            
            self.logger.info(f"✅ Checkpoint created: {checkpoint_path}")
            return str(checkpoint_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error creating checkpoint: {e}")
            return ""
