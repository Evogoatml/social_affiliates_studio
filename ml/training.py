"""
Viral Content AI Trainer
Fine-tunes language models on scraped viral content for improved performance
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

# Hugging Face imports
try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        Trainer,
        TrainingArguments,
        DataCollatorForLanguageModeling
    )
    from datasets import Dataset, DatasetDict
    from peft import LoraConfig, get_peft_model, TaskType
    import torch
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logging.warning("Hugging Face libraries not installed. Run: pip install transformers datasets peft torch")


class ViralContentTrainer:
    """
    Trains and fine-tunes AI models on viral social media content
    """
    
    def __init__(self, config: Any, database: Any):
        """
        Initialize the trainer
        
        Args:
            config: System configuration
            database: Database instance for accessing viral content
        """
        self.config = config
        self.database = database
        self.logger = logging.getLogger(__name__)
        
        # Paths
        self.models_dir = Path("ml/models")
        self.datasets_dir = Path("ml/datasets")
        self.logs_dir = Path("ml/logs")
        
        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Model configuration
        self.base_model = "mistralai/Mistral-7B-Instruct-v0.3"  # Smaller, faster model
        self.model = None
        self.tokenizer = None
        
        self.logger.info("🤖 Viral Content Trainer initialized")
    
    def prepare_dataset(self, min_engagement: int = 10000) -> Optional[Dataset]:
        """
        Prepare training dataset from viral content database
        
        Args:
            min_engagement: Minimum engagement threshold for viral content
            
        Returns:
            Hugging Face Dataset or None if no data
        """
        if not HF_AVAILABLE:
            self.logger.error("❌ Hugging Face libraries not available")
            return None
        
        self.logger.info(f"📊 Preparing dataset (min engagement: {min_engagement})")
        
        try:
            # Get viral content from database
            viral_data = self.database.get_viral_content(min_engagement=min_engagement)
            
            if not viral_data:
                self.logger.warning("⚠️ No viral content found in database")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(viral_data)
            
            self.logger.info(f"✅ Loaded {len(df)} viral posts")
            
            # Prepare training examples
            training_examples = []
            
            for _, row in df.iterrows():
                # Create instruction-following format
                prompt = self._create_training_prompt(row)
                training_examples.append({
                    'text': prompt,
                    'engagement_score': row.get('engagement_score', 0),
                    'platform': row.get('platform', 'unknown'),
                    'content_type': row.get('content_type', 'post')
                })
            
            # Convert to Hugging Face Dataset
            dataset = Dataset.from_pandas(pd.DataFrame(training_examples))
            
            # Split into train/validation
            dataset_dict = dataset.train_test_split(test_size=0.1, seed=42)
            
            # Save to disk
            dataset_path = self.datasets_dir / f"viral_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dataset_dict.save_to_disk(str(dataset_path))
            
            self.logger.info(f"✅ Dataset prepared: {len(dataset_dict['train'])} train, {len(dataset_dict['test'])} validation")
            
            return dataset_dict
            
        except Exception as e:
            self.logger.error(f"❌ Error preparing dataset: {e}")
            return None
    
    def _create_training_prompt(self, row: pd.Series) -> str:
        """
        Create instruction-following training prompt from viral content
        
        Args:
            row: DataFrame row with viral content data
            
        Returns:
            Formatted training prompt
        """
        platform = row.get('platform', 'social media')
        content_type = row.get('content_type', 'post')
        caption = row.get('caption', '')
        hashtags = row.get('hashtags', [])
        engagement = row.get('engagement_score', 0)
        
        # Format hashtags
        hashtags_str = ' '.join(hashtags[:10]) if hashtags else ''
        
        # Create instruction prompt
        instruction = f"Create a viral {content_type} caption for {platform} that will get high engagement (target: {engagement}+ interactions)."
        
        prompt = f"""<s>[INST] {instruction} [/INST]

Caption: {caption}

Hashtags: {hashtags_str}

Engagement: {engagement:,} interactions
</s>"""
        
        return prompt
    
    def load_model(self, model_name: Optional[str] = None):
        """
        Load base model and tokenizer
        
        Args:
            model_name: Model identifier from Hugging Face Hub
        """
        if not HF_AVAILABLE:
            self.logger.error("❌ Hugging Face libraries not available")
            return
        
        model_name = model_name or self.base_model
        
        self.logger.info(f"📥 Loading model: {model_name}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            
            # Set padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with 8-bit quantization for efficiency
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                load_in_8bit=True,
                trust_remote_code=True
            )
            
            self.logger.info("✅ Model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading model: {e}")
    
    def fine_tune(
        self,
        dataset: DatasetDict,
        output_name: str = "viral-content-model",
        epochs: int = 3,
        learning_rate: float = 2e-5,
        batch_size: int = 4
    ) -> Optional[str]:
        """
        Fine-tune model on viral content dataset using LoRA
        
        Args:
            dataset: Training dataset
            output_name: Name for the fine-tuned model
            epochs: Number of training epochs
            learning_rate: Learning rate
            batch_size: Batch size per device
            
        Returns:
            Path to saved model or None if failed
        """
        if not HF_AVAILABLE:
            self.logger.error("❌ Hugging Face libraries not available")
            return None
        
        if self.model is None or self.tokenizer is None:
            self.logger.error("❌ Model not loaded. Call load_model() first")
            return None
        
        self.logger.info(f"🚀 Starting fine-tuning: {output_name}")
        
        try:
            # Configure LoRA
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=16,  # LoRA rank
                lora_alpha=32,
                lora_dropout=0.05,
                target_modules=["q_proj", "v_proj"]  # Mistral attention modules
            )
            
            # Apply LoRA to model
            self.model = get_peft_model(self.model, lora_config)
            
            self.logger.info(f"✅ LoRA configured (trainable params: {self.model.print_trainable_parameters()})")
            
            # Tokenize dataset
            def tokenize_function(examples):
                return self.tokenizer(
                    examples['text'],
                    padding='max_length',
                    truncation=True,
                    max_length=512
                )
            
            tokenized_dataset = dataset.map(
                tokenize_function,
                batched=True,
                remove_columns=dataset['train'].column_names
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False
            )
            
            # Training arguments
            output_dir = self.models_dir / output_name
            
            training_args = TrainingArguments(
                output_dir=str(output_dir),
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                num_train_epochs=epochs,
                learning_rate=learning_rate,
                fp16=True,  # Mixed precision training
                save_steps=500,
                eval_steps=500,
                logging_steps=100,
                evaluation_strategy="steps",
                save_total_limit=2,
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                report_to="none",  # Disable wandb
                logging_dir=str(self.logs_dir / output_name)
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=tokenized_dataset['train'],
                eval_dataset=tokenized_dataset['test'],
                data_collator=data_collator,
            )
            
            # Train
            self.logger.info("🏋️ Training started...")
            train_result = trainer.train()
            
            # Save model
            trainer.save_model()
            self.tokenizer.save_pretrained(str(output_dir))
            
            # Save training metrics
            metrics = {
                'train_loss': train_result.training_loss,
                'train_runtime': train_result.metrics['train_runtime'],
                'train_samples_per_second': train_result.metrics['train_samples_per_second'],
                'epochs': epochs,
                'learning_rate': learning_rate,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(output_dir / 'training_metrics.json', 'w') as f:
                json.dump(metrics, f, indent=2)
            
            self.logger.info(f"✅ Training complete! Model saved to: {output_dir}")
            self.logger.info(f"📊 Final loss: {train_result.training_loss:.4f}")
            
            return str(output_dir)
            
        except Exception as e:
            self.logger.error(f"❌ Error during fine-tuning: {e}")
            return None
    
    def generate_caption(
        self,
        prompt: str,
        model_path: Optional[str] = None,
        max_length: int = 150
    ) -> str:
        """
        Generate caption using fine-tuned model
        
        Args:
            prompt: Input prompt
            model_path: Path to fine-tuned model (optional)
            max_length: Maximum generation length
            
        Returns:
            Generated caption
        """
        if not HF_AVAILABLE:
            return "Error: Hugging Face libraries not available"
        
        try:
            # Load model if path provided
            if model_path and model_path != str(self.models_dir):
                self.load_model(model_path)
            
            if self.model is None or self.tokenizer is None:
                return "Error: Model not loaded"
            
            # Format prompt
            formatted_prompt = f"<s>[INST] {prompt} [/INST]"
            
            # Tokenize
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)
            
            # Generate
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract response (remove prompt)
            response = generated_text.split("[/INST]")[-1].strip()
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error generating caption: {e}")
            return f"Error: {str(e)}"
    
    def evaluate_model(self, model_path: str, test_dataset: Dataset) -> Dict:
        """
        Evaluate fine-tuned model performance
        
        Args:
            model_path: Path to model to evaluate
            test_dataset: Test dataset
            
        Returns:
            Evaluation metrics
        """
        if not HF_AVAILABLE:
            return {'error': 'Hugging Face libraries not available'}
        
        try:
            # Load model
            self.load_model(model_path)
            
            # TODO: Implement evaluation metrics
            # - Perplexity
            # - BLEU score
            # - Engagement prediction accuracy
            
            metrics = {
                'model_path': model_path,
                'test_samples': len(test_dataset),
                'timestamp': datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Error evaluating model: {e}")
            return {'error': str(e)}
    
    def export_to_huggingface(
        self,
        model_path: str,
        repo_name: str,
        token: Optional[str] = None
    ):
        """
        Export fine-tuned model to Hugging Face Hub
        
        Args:
            model_path: Path to local model
            repo_name: Repository name on HF Hub (username/model-name)
            token: Hugging Face API token
        """
        if not HF_AVAILABLE:
            self.logger.error("❌ Hugging Face libraries not available")
            return
        
        try:
            from huggingface_hub import HfApi
            
            api = HfApi(token=token)
            
            self.logger.info(f"📤 Uploading model to: {repo_name}")
            
            api.upload_folder(
                folder_path=model_path,
                repo_id=repo_name,
                repo_type="model"
            )
            
            self.logger.info(f"✅ Model uploaded: https://huggingface.co/{repo_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Error uploading to Hugging Face: {e}")


def setup_training_pipeline(config, database):
    """
    Set up automated training pipeline
    
    Args:
        config: System configuration
        database: Database instance
        
    Returns:
        Configured trainer
    """
    trainer = ViralContentTrainer(config, database)
    
    # Prepare dataset
    dataset = trainer.prepare_dataset(min_engagement=10000)
    
    if dataset:
        # Load base model
        trainer.load_model()
        
        # Fine-tune
        model_path = trainer.fine_tune(
            dataset=dataset,
            output_name=f"viral-model-{datetime.now().strftime('%Y%m%d')}",
            epochs=3,
            learning_rate=2e-5,
            batch_size=4
        )
        
        return trainer, model_path
    
    return trainer, None
