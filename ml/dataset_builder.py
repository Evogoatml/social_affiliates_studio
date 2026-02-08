"""
Viral Dataset Builder
Converts scraped viral content into training-ready datasets
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

try:
    from datasets import Dataset, DatasetDict, Features, Value, Sequence
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


class ViralDatasetBuilder:
    """
    Builds and manages training datasets from viral content
    """
    
    def __init__(self, database: Any):
        """
        Initialize dataset builder
        
        Args:
            database: Database instance
        """
        self.database = database
        self.logger = logging.getLogger(__name__)
        self.datasets_dir = Path("ml/datasets")
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
    
    def build_caption_dataset(
        self,
        min_engagement: int = 5000,
        platforms: Optional[List[str]] = None
    ) -> Optional[DatasetDict]:
        """
        Build dataset for caption generation
        
        Args:
            min_engagement: Minimum engagement threshold
            platforms: List of platforms to include (None = all)
            
        Returns:
            DatasetDict with train/validation/test splits
        """
        if not HF_AVAILABLE:
            self.logger.error("❌ datasets library not available")
            return None
        
        self.logger.info("📊 Building caption dataset...")
        
        try:
            # Get viral content
            viral_data = self.database.get_viral_content(min_engagement=min_engagement)
            
            if not viral_data:
                self.logger.warning("⚠️ No viral content found")
                return None
            
            # Filter by platform if specified
            if platforms:
                viral_data = [v for v in viral_data if v.get('platform') in platforms]
            
            # Prepare examples
            examples = []
            for item in viral_data:
                examples.append({
                    'platform': item.get('platform', 'unknown'),
                    'content_type': item.get('content_type', 'post'),
                    'caption': item.get('caption', ''),
                    'hashtags': json.dumps(item.get('hashtags', [])),
                    'engagement_score': item.get('engagement_score', 0),
                    'likes': item.get('metrics', {}).get('likes', 0),
                    'comments': item.get('metrics', {}).get('comments', 0),
                    'shares': item.get('metrics', {}).get('shares', 0),
                    'views': item.get('metrics', {}).get('views', 0),
                    'created_at': item.get('created_at', ''),
                })
            
            # Convert to DataFrame
            df = pd.DataFrame(examples)
            
            # Create dataset
            dataset = Dataset.from_pandas(df)
            
            # Split: 80% train, 10% validation, 10% test
            train_test = dataset.train_test_split(test_size=0.2, seed=42)
            val_test = train_test['test'].train_test_split(test_size=0.5, seed=42)
            
            dataset_dict = DatasetDict({
                'train': train_test['train'],
                'validation': val_test['train'],
                'test': val_test['test']
            })
            
            self.logger.info(f"✅ Dataset created: {len(dataset_dict['train'])} train, "
                           f"{len(dataset_dict['validation'])} val, {len(dataset_dict['test'])} test")
            
            # Save to disk
            output_path = self.datasets_dir / f"caption_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dataset_dict.save_to_disk(str(output_path))
            
            # Save metadata
            metadata = {
                'dataset_type': 'caption_generation',
                'min_engagement': min_engagement,
                'platforms': platforms or 'all',
                'total_examples': len(examples),
                'train_size': len(dataset_dict['train']),
                'validation_size': len(dataset_dict['validation']),
                'test_size': len(dataset_dict['test']),
                'created_at': datetime.now().isoformat(),
                'path': str(output_path)
            }
            
            with open(output_path / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return dataset_dict
            
        except Exception as e:
            self.logger.error(f"❌ Error building caption dataset: {e}")
            return None
    
    def build_engagement_prediction_dataset(
        self,
        min_engagement: int = 1000
    ) -> Optional[DatasetDict]:
        """
        Build dataset for engagement prediction
        
        Args:
            min_engagement: Minimum engagement threshold
            
        Returns:
            DatasetDict for training engagement prediction models
        """
        if not HF_AVAILABLE:
            self.logger.error("❌ datasets library not available")
            return None
        
        self.logger.info("📊 Building engagement prediction dataset...")
        
        try:
            viral_data = self.database.get_viral_content(min_engagement=min_engagement)
            
            if not viral_data:
                self.logger.warning("⚠️ No viral content found")
                return None
            
            examples = []
            for item in viral_data:
                # Extract features
                caption = item.get('caption', '')
                hashtags = item.get('hashtags', [])
                metrics = item.get('metrics', {})
                
                # Calculate engagement score (target variable)
                engagement_score = (
                    metrics.get('likes', 0) +
                    metrics.get('comments', 0) * 2 +
                    metrics.get('shares', 0) * 3 +
                    metrics.get('views', 0) * 0.1
                )
                
                examples.append({
                    'caption': caption,
                    'caption_length': len(caption),
                    'num_hashtags': len(hashtags),
                    'hashtags': json.dumps(hashtags[:10]),
                    'platform': item.get('platform', 'unknown'),
                    'content_type': item.get('content_type', 'post'),
                    'hour_posted': item.get('hour_posted', 12),
                    'engagement_score': engagement_score,
                    'likes': metrics.get('likes', 0),
                    'comments': metrics.get('comments', 0),
                    'shares': metrics.get('shares', 0),
                    'views': metrics.get('views', 0),
                })
            
            df = pd.DataFrame(examples)
            dataset = Dataset.from_pandas(df)
            
            # Split
            train_test = dataset.train_test_split(test_size=0.2, seed=42)
            val_test = train_test['test'].train_test_split(test_size=0.5, seed=42)
            
            dataset_dict = DatasetDict({
                'train': train_test['train'],
                'validation': val_test['train'],
                'test': val_test['test']
            })
            
            self.logger.info(f"✅ Engagement dataset created: {len(dataset_dict['train'])} train examples")
            
            # Save
            output_path = self.datasets_dir / f"engagement_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dataset_dict.save_to_disk(str(output_path))
            
            return dataset_dict
            
        except Exception as e:
            self.logger.error(f"❌ Error building engagement dataset: {e}")
            return None
    
    def build_hashtag_recommendation_dataset(self) -> Optional[DatasetDict]:
        """
        Build dataset for hashtag recommendation
        
        Returns:
            DatasetDict for training hashtag recommendation models
        """
        if not HF_AVAILABLE:
            self.logger.error("❌ datasets library not available")
            return None
        
        self.logger.info("📊 Building hashtag recommendation dataset...")
        
        try:
            # Get trending hashtags with performance data
            trending_hashtags = self.database.get_trending_hashtags(limit=1000)
            
            if not trending_hashtags:
                self.logger.warning("⚠️ No trending hashtags found")
                return None
            
            examples = []
            for hashtag in trending_hashtags:
                examples.append({
                    'hashtag': hashtag.get('hashtag', ''),
                    'platform': hashtag.get('platform', 'unknown'),
                    'usage_count': hashtag.get('usage_count', 0),
                    'avg_engagement': hashtag.get('avg_engagement', 0),
                    'trend_score': hashtag.get('trend_score', 0),
                    'category': hashtag.get('category', 'general'),
                    'performance_score': (
                        hashtag.get('usage_count', 0) * 0.3 +
                        hashtag.get('avg_engagement', 0) * 0.7
                    )
                })
            
            df = pd.DataFrame(examples)
            dataset = Dataset.from_pandas(df)
            
            # Split
            dataset_dict = dataset.train_test_split(test_size=0.2, seed=42)
            
            self.logger.info(f"✅ Hashtag dataset created: {len(dataset_dict['train'])} train examples")
            
            # Save
            output_path = self.datasets_dir / f"hashtag_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dataset_dict.save_to_disk(str(output_path))
            
            return dataset_dict
            
        except Exception as e:
            self.logger.error(f"❌ Error building hashtag dataset: {e}")
            return None
    
    def export_to_csv(self, dataset: DatasetDict, output_name: str):
        """
        Export dataset to CSV files
        
        Args:
            dataset: Dataset to export
            output_name: Base name for output files
        """
        try:
            output_dir = self.datasets_dir / output_name
            output_dir.mkdir(exist_ok=True)
            
            for split_name, split_data in dataset.items():
                df = split_data.to_pandas()
                output_file = output_dir / f"{split_name}.csv"
                df.to_csv(output_file, index=False)
                self.logger.info(f"✅ Exported {split_name} to {output_file}")
                
        except Exception as e:
            self.logger.error(f"❌ Error exporting to CSV: {e}")
    
    def upload_to_huggingface(
        self,
        dataset: DatasetDict,
        repo_name: str,
        token: Optional[str] = None
    ):
        """
        Upload dataset to Hugging Face Hub
        
        Args:
            dataset: Dataset to upload
            repo_name: Repository name (username/dataset-name)
            token: Hugging Face API token
        """
        if not HF_AVAILABLE:
            self.logger.error("❌ Hugging Face libraries not available")
            return
        
        try:
            self.logger.info(f"📤 Uploading dataset to: {repo_name}")
            
            dataset.push_to_hub(
                repo_name,
                token=token,
                private=False
            )
            
            self.logger.info(f"✅ Dataset uploaded: https://huggingface.co/datasets/{repo_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Error uploading dataset: {e}")
    
    def get_dataset_stats(self, dataset: DatasetDict) -> Dict:
        """
        Get statistics about a dataset
        
        Args:
            dataset: Dataset to analyze
            
        Returns:
            Dictionary of statistics
        """
        try:
            stats = {
                'splits': list(dataset.keys()),
                'total_examples': sum(len(split) for split in dataset.values()),
                'features': list(dataset['train'].features.keys()) if 'train' in dataset else [],
            }
            
            # Per-split stats
            for split_name, split_data in dataset.items():
                stats[f'{split_name}_size'] = len(split_data)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating stats: {e}")
            return {}
