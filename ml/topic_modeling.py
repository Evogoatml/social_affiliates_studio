"""
Topic Modeling for Viral Content Analysis
Uses Contextualized Topic Models (CTM) to analyze themes in viral social media content
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np

# CTM imports
try:
    from contextualized_topic_models.models.ctm import CombinedTM, ZeroShotTM
    from contextualized_topic_models.utils.data_preparation import WhiteSpacePreprocessingStopwords, TopicModelDataPreparation
    from contextualized_topic_models.utils.preprocessing import bert_embeddings_from_list
    CTM_AVAILABLE = True
except ImportError:
    CTM_AVAILABLE = False
    logging.warning("Contextualized Topic Models not installed. Run: pip install contextualized-topic-models")


class ViralTopicModeler:
    """
    Analyzes viral content using Contextualized Topic Models (CTM)
    to identify trending topics, themes, and content patterns
    """
    
    def __init__(self, config: Any, database: Any):
        """
        Initialize the topic modeler
        
        Args:
            config: System configuration
            database: Database instance for accessing viral content
        """
        self.config = config
        self.database = database
        self.logger = logging.getLogger(__name__)
        
        # Paths
        self.models_dir = Path("ml/models/topic_models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_dir = Path("ml/datasets/topic_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # CTM configuration
        self.num_topics = 10  # Default number of topics
        self.model_type = "combined"  # or "zeroshot"
        
        # Model instances
        self.model = None
        self.tp = None  # TopicModelDataPreparation instance
        
        if not CTM_AVAILABLE:
            self.logger.warning("CTM not available - topic modeling disabled")
    
    def prepare_data(
        self,
        texts: List[str],
        platform: Optional[str] = None,
        min_engagement: int = 5000,
        use_stopwords: bool = True
    ) -> Optional[Any]:
        """
        Prepare viral content data for topic modeling
        
        Args:
            texts: List of text documents (captions, posts)
            platform: Optional platform filter (instagram, tiktok, twitter)
            min_engagement: Minimum engagement threshold
            use_stopwords: Whether to remove stopwords
            
        Returns:
            Prepared training data for CTM
        """
        if not CTM_AVAILABLE:
            self.logger.error("CTM not available")
            return None
        
        if not texts or len(texts) == 0:
            self.logger.warning("No texts provided for topic modeling")
            return None
        
        self.logger.info(f"📊 Preparing {len(texts)} documents for topic modeling...")
        
        try:
            # Preprocessing
            if use_stopwords:
                sp = WhiteSpacePreprocessingStopwords(texts)
                preprocessed_docs, unpreprocessed_docs, vocab = sp.preprocess()
            else:
                preprocessed_docs = texts
                unpreprocessed_docs = texts
                vocab = list(set(" ".join(texts).split()))
            
            # Prepare data with embeddings
            self.tp = TopicModelDataPreparation("all-MiniLM-L6-v2")
            training_data = self.tp.fit(
                text_for_contextual=unpreprocessed_docs,
                text_for_bow=preprocessed_docs
            )
            
            self.logger.info(f"✅ Data prepared - Vocabulary size: {len(vocab)}")
            return training_data
            
        except Exception as e:
            self.logger.error(f"Error preparing data: {e}")
            return None
    
    def train_model(
        self,
        training_data: Any,
        num_topics: int = 10,
        model_type: str = "combined",
        num_epochs: int = 100,
        save_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Train a topic model on viral content
        
        Args:
            training_data: Prepared training data from prepare_data()
            num_topics: Number of topics to discover
            model_type: Type of model ("combined" or "zeroshot")
            num_epochs: Number of training epochs
            save_path: Optional path to save the model
            
        Returns:
            Path to saved model or None if training failed
        """
        if not CTM_AVAILABLE:
            self.logger.error("CTM not available")
            return None
        
        if training_data is None:
            self.logger.error("Training data is None")
            return None
        
        self.logger.info(f"🎓 Training {model_type} topic model with {num_topics} topics...")
        self.num_topics = num_topics
        self.model_type = model_type
        
        try:
            # Initialize model
            if model_type == "combined":
                self.model = CombinedTM(
                    bow_size=len(self.tp.vocab),
                    contextual_size=384,  # MiniLM embedding size
                    n_components=num_topics,
                    num_epochs=num_epochs
                )
            elif model_type == "zeroshot":
                self.model = ZeroShotTM(
                    bow_size=len(self.tp.vocab),
                    contextual_size=384,
                    n_components=num_topics,
                    num_epochs=num_epochs
                )
            else:
                self.logger.error(f"Unknown model type: {model_type}")
                return None
            
            # Train model
            self.model.fit(training_data)
            
            # Save model
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = str(self.models_dir / f"{model_type}_topics{num_topics}_{timestamp}")
            
            self.model.save(models_dir=save_path)
            
            self.logger.info(f"✅ Model trained and saved to: {save_path}")
            return save_path
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return None
    
    def load_model(self, model_path: str) -> bool:
        """
        Load a pre-trained topic model
        
        Args:
            model_path: Path to saved model
            
        Returns:
            True if successful, False otherwise
        """
        if not CTM_AVAILABLE:
            self.logger.error("CTM not available")
            return False
        
        try:
            # Determine model type from path
            if "combined" in model_path:
                self.model = CombinedTM(bow_size=1, contextual_size=384, n_components=10)
            else:
                self.model = ZeroShotTM(bow_size=1, contextual_size=384, n_components=10)
            
            self.model.load(model_path)
            self.logger.info(f"✅ Model loaded from: {model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False
    
    def get_topics(self, top_k: int = 10) -> List[List[str]]:
        """
        Get the top K words for each topic
        
        Args:
            top_k: Number of top words per topic
            
        Returns:
            List of topics, where each topic is a list of words
        """
        if not CTM_AVAILABLE or self.model is None:
            self.logger.error("Model not available")
            return []
        
        try:
            topics = self.model.get_topic_lists(top_k)
            return topics
        except Exception as e:
            self.logger.error(f"Error getting topics: {e}")
            return []
    
    def get_topic_labels(self, custom_labels: Optional[Dict[int, str]] = None) -> Dict[int, str]:
        """
        Generate human-readable labels for topics
        
        Args:
            custom_labels: Optional custom labels for topics
            
        Returns:
            Dictionary mapping topic ID to label
        """
        if custom_labels:
            return custom_labels
        
        topics = self.get_topics(top_k=5)
        labels = {}
        
        for idx, topic_words in enumerate(topics):
            # Create label from top 3 words
            label = ", ".join(topic_words[:3])
            labels[idx] = f"Topic {idx}: {label}"
        
        return labels
    
    def predict_topics(self, texts: List[str]) -> np.ndarray:
        """
        Predict topic distributions for new texts
        
        Args:
            texts: List of text documents
            
        Returns:
            Array of topic distributions (num_docs x num_topics)
        """
        if not CTM_AVAILABLE or self.model is None or self.tp is None:
            self.logger.error("Model or data preparation not available")
            return np.array([])
        
        try:
            # Prepare test data
            test_data = self.tp.transform(text_for_contextual=texts)
            
            # Get predictions
            predictions = self.model.get_doc_topic_distribution(test_data)
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting topics: {e}")
            return np.array([])
    
    def analyze_viral_content(
        self,
        platform: Optional[str] = None,
        min_engagement: int = 10000,
        limit: int = 500
    ) -> Dict[str, Any]:
        """
        Analyze viral content from the database to discover topics
        
        Args:
            platform: Optional platform filter
            min_engagement: Minimum engagement threshold
            limit: Maximum number of posts to analyze
            
        Returns:
            Dictionary with analysis results
        """
        self.logger.info(f"🔍 Analyzing viral content for topic discovery...")
        
        # Get viral content from database
        if hasattr(self.database, 'get_top_viral_content'):
            viral_posts = self.database.get_top_viral_content(
                platform=platform,
                limit=limit
            )
        else:
            self.logger.warning("Database does not support get_top_viral_content")
            viral_posts = []
        
        if not viral_posts or len(viral_posts) == 0:
            self.logger.warning("No viral content found in database")
            return {"error": "No viral content available"}
        
        # Extract texts
        texts = []
        for post in viral_posts:
            if isinstance(post, dict) and 'caption' in post:
                texts.append(post['caption'])
            elif isinstance(post, dict) and 'text' in post:
                texts.append(post['text'])
        
        if len(texts) < 10:
            self.logger.warning(f"Not enough texts for topic modeling: {len(texts)}")
            return {"error": f"Insufficient texts: {len(texts)}"}
        
        # Prepare and train model
        training_data = self.prepare_data(texts, platform=platform)
        if training_data is None:
            return {"error": "Failed to prepare data"}
        
        model_path = self.train_model(training_data, num_topics=self.num_topics)
        if model_path is None:
            return {"error": "Failed to train model"}
        
        # Get topics
        topics = self.get_topics(top_k=10)
        topic_labels = self.get_topic_labels()
        
        # Get topic distributions
        topic_distributions = self.predict_topics(texts[:100])  # Analyze first 100 for efficiency
        
        # Analyze topic prevalence
        topic_prevalence = {}
        if topic_distributions.size > 0:
            avg_distribution = np.mean(topic_distributions, axis=0)
            for i, prob in enumerate(avg_distribution):
                topic_prevalence[i] = float(prob)
        
        results = {
            "num_documents": len(texts),
            "num_topics": self.num_topics,
            "model_path": model_path,
            "topics": {i: words for i, words in enumerate(topics)},
            "topic_labels": topic_labels,
            "topic_prevalence": topic_prevalence,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save results
        results_path = self.data_dir / f"topic_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"✅ Topic analysis complete - Results saved to {results_path}")
        return results


def setup_topic_modeling(config: Any, database: Any) -> Optional[ViralTopicModeler]:
    """
    Setup and initialize topic modeling for viral content analysis
    
    Args:
        config: System configuration
        database: Database instance
        
    Returns:
        Initialized ViralTopicModeler or None if setup fails
    """
    logger = logging.getLogger(__name__)
    
    if not CTM_AVAILABLE:
        logger.warning("Contextualized Topic Models not available - skipping setup")
        return None
    
    try:
        modeler = ViralTopicModeler(config, database)
        logger.info("✅ Topic modeling setup complete")
        return modeler
    except Exception as e:
        logger.error(f"Failed to setup topic modeling: {e}")
        return None
