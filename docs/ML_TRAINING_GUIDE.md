# ML Training Setup & Quick Start Guide

## 🎯 Overview
This guide will help you set up and run the Hugging Face-powered ML training pipeline for the Autonomous Influencer System.

---

## 📋 Prerequisites

### 1. System Requirements
- **Python**: 3.8 or higher
- **RAM**: 16GB minimum (32GB recommended for training)
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Disk Space**: 20GB minimum for models and datasets

### 2. Accounts & Tokens
- **Hugging Face Account**: https://huggingface.co/join
- **Hugging Face Token**: https://huggingface.co/settings/tokens (Read & Write access)
- **OpenAI API Key** (optional): For baseline comparisons

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
cd /home/user/webapp

# Install core ML libraries
pip install transformers datasets accelerate peft bitsandbytes
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install diffusers huggingface_hub sentencepiece protobuf

# Install topic modeling
pip install contextualized-topic-models

# Optional: For faster training
pip install flash-attn --no-build-isolation
```

### Step 2: Authenticate with Hugging Face
```bash
# Login to Hugging Face
huggingface-cli login

# Enter your token from https://huggingface.co/settings/tokens
# Choose: Write access for uploading models/datasets
```

### Step 3: Configure Environment
```bash
# Add to .env file
echo "HUGGINGFACE_TOKEN=hf_your_token_here" >> .env
echo "HF_HOME=./ml/cache" >> .env
```

### Step 4: Run First Training
```python
# Run automated training pipeline
python -c "
from ml.training import setup_training_pipeline
from core.config import Config
from core.database import Database

config = Config()
database = Database()

trainer, model_path = setup_training_pipeline(config, database)
print(f'✅ Training complete! Model saved to: {model_path}')
"
```

---

## 📚 Detailed Setup

### A. Install PyTorch (Choose Your Version)

#### CPU Only (Lightweight)
```bash
pip install torch torchvision torchaudio
```

#### NVIDIA GPU (CUDA 11.8)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### NVIDIA GPU (CUDA 12.1)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### B. Install Transformers & Datasets
```bash
pip install transformers==4.36.0
pip install datasets==2.15.0
pip install accelerate==0.25.0
pip install peft==0.7.0
pip install bitsandbytes==0.41.3  # For 8-bit/4-bit quantization
```

### C. Optional: Install Image Generation Libraries
```bash
pip install diffusers==0.25.0
pip install invisible-watermark transformers accelerate safetensors
```

### D. Verify Installation
```bash
python -c "
import torch
import transformers
import datasets
print(f'✅ PyTorch: {torch.__version__}')
print(f'✅ Transformers: {transformers.__version__}')
print(f'✅ Datasets: {datasets.__version__}')
print(f'✅ CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'✅ GPU: {torch.cuda.get_device_name(0)}')
"
```

---

## 🎓 Training Workflows

### Workflow 1: Caption Generation (Recommended First)
```python
from ml.training import ViralContentTrainer
from ml.dataset_builder import ViralDatasetBuilder
from core.config import Config
from core.database import Database

# Initialize
config = Config()
database = Database()
builder = ViralDatasetBuilder(database)

# Build dataset
dataset = builder.build_caption_dataset(
    min_engagement=10000,
    platforms=['instagram', 'tiktok']
)

# Initialize trainer
trainer = ViralContentTrainer(config, database)
trainer.load_model("mistralai/Mistral-7B-Instruct-v0.3")

# Fine-tune
model_path = trainer.fine_tune(
    dataset=dataset,
    output_name="viral-caption-model-v1",
    epochs=3,
    learning_rate=2e-5,
    batch_size=4
)

# Test generation
caption = trainer.generate_caption(
    "Create a viral Instagram post about morning motivation"
)
print(caption)
```

### Workflow 2: Engagement Prediction
```python
# Build engagement dataset
engagement_dataset = builder.build_engagement_prediction_dataset(
    min_engagement=5000
)

# Train predictor model
trainer.load_model("bert-base-uncased")
model_path = trainer.fine_tune(
    dataset=engagement_dataset,
    output_name="engagement-predictor-v1",
    epochs=5,
    learning_rate=3e-5
)
```

### Workflow 3: Hashtag Recommendation
```python
# Build hashtag dataset
hashtag_dataset = builder.build_hashtag_recommendation_dataset()

# Export for analysis
builder.export_to_csv(hashtag_dataset, "hashtag_analysis")
```

---

## 🔄 Automated Training Pipeline

### Enable Continuous Learning
Add to `core/orchestrator.py`:

```python
async def _train_on_viral_data(self):
    """Train model on newly scraped viral content (weekly)"""
    
    if datetime.now().weekday() == 0:  # Monday
        self.logger.info("🎓 Starting weekly model training...")
        
        from ml.training import ViralContentTrainer
        from ml.dataset_builder import ViralDatasetBuilder
        
        # Build dataset from last week's viral content
        builder = ViralDatasetBuilder(self.database)
        dataset = builder.build_caption_dataset(min_engagement=10000)
        
        if dataset and len(dataset['train']) > 100:
            # Train new model
            trainer = ViralContentTrainer(self.config, self.database)
            trainer.load_model()
            
            model_path = trainer.fine_tune(
                dataset=dataset,
                output_name=f"viral-model-{datetime.now().strftime('%Y%m%d')}",
                epochs=3
            )
            
            if model_path:
                # Register new model
                from ml.model_manager import ModelManager
                manager = ModelManager()
                model_id = manager.register_model(
                    model_path=model_path,
                    name="Viral Caption Generator",
                    description="Trained on weekly viral content"
                )
                
                # Set as active
                manager.set_active_model(model_id)
                
                self.logger.info(f"✅ New model deployed: {model_id}")
```

---

## 📊 Model Management

### List All Models
```python
from ml.model_manager import ModelManager

manager = ModelManager()
models = manager.list_models()

for model in models:
    print(f"ID: {model['id']}")
    print(f"Name: {model['name']}")
    print(f"Status: {model['status']}")
    print(f"Path: {model['path']}")
    print(f"Metrics: {model.get('metrics', {})}")
    print("---")
```

### Compare Models
```python
# Compare two models
comparison = manager.compare_models([
    "viral-model-20240101_120000",
    "viral-model-20240108_120000"
])

print(comparison)
```

### Set Active Model
```python
# Use best performing model
best_model = manager.get_best_model(metric='eval_loss', minimize=True)
if best_model:
    manager.set_active_model(best_model['id'])
```

### Export Model
```python
# Export for deployment
manager.export_model_for_deployment(
    model_id="viral-model-20240101_120000",
    output_path="./deployment/models/production"
)
```

---

## 🎨 Using Trained Models

### Generate Captions
```python
from ml.training import ViralContentTrainer
from ml.model_manager import ModelManager

# Load active model
manager = ModelManager()
active_model = manager.get_active_model()

if active_model:
    trainer = ViralContentTrainer(config, database)
    
    # Generate caption
    caption = trainer.generate_caption(
        prompt="Create an engaging TikTok caption about fitness motivation",
        model_path=active_model['path'],
        max_length=150
    )
    
    print(caption)
```

### Batch Generation
```python
prompts = [
    "Create a viral Instagram reel caption about travel",
    "Write a motivational LinkedIn post",
    "Generate a funny TikTok caption about work"
]

for prompt in prompts:
    caption = trainer.generate_caption(prompt)
    print(f"\nPrompt: {prompt}")
    print(f"Caption: {caption}")
    print("---")
```

---

## 📈 Monitoring & Evaluation

### Training Metrics
Check training logs:
```bash
# View training logs
cat ml/logs/viral-caption-model-v1/trainer_state.json

# View TensorBoard (if installed)
tensorboard --logdir ml/logs/
```

### Model Performance
```python
# Evaluate model
from ml.training import ViralContentTrainer

trainer = ViralContentTrainer(config, database)
metrics = trainer.evaluate_model(
    model_path="ml/models/viral-model-v1",
    test_dataset=dataset['test']
)

print(metrics)
```

---

## 🚦 Troubleshooting

### Issue: Out of Memory (OOM)
**Solution**: Reduce batch size
```python
model_path = trainer.fine_tune(
    dataset=dataset,
    batch_size=2,  # Reduce from 4 to 2
    epochs=3
)
```

### Issue: Slow Training
**Solution**: Enable mixed precision & gradient checkpointing
```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    fp16=True,  # Mixed precision
    gradient_checkpointing=True,  # Save memory
    per_device_train_batch_size=2
)
```

### Issue: Model Not Loading
**Solution**: Check CUDA availability
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If False, reinstall PyTorch with CUDA support.

### Issue: Hugging Face Token Error
**Solution**: Re-authenticate
```bash
huggingface-cli logout
huggingface-cli login
```

---

## 🎯 Best Practices

### 1. Data Quality
- ✅ Filter for high-engagement content (>10k interactions)
- ✅ Remove duplicates and low-quality posts
- ✅ Balance dataset across platforms

### 2. Training Strategy
- ✅ Start with small model (Mistral 7B)
- ✅ Use LoRA for efficient fine-tuning
- ✅ Train in stages (3-5 epochs)
- ✅ Monitor validation loss

### 3. Model Versioning
- ✅ Register all trained models
- ✅ Compare performance before deploying
- ✅ Keep backups of best models

### 4. Continuous Learning
- ✅ Retrain weekly on new viral content
- ✅ A/B test model performance
- ✅ Update active model if improvement >5%

---

## 📦 Recommended Models

### Caption Generation
- **Mistral-7B-Instruct-v0.3** (Best overall)
- **Llama-3.1-8B-Instruct** (Higher quality, slower)
- **GPT-2-Medium** (Fast, lightweight)

### Engagement Prediction
- **BERT-base-uncased** (Good baseline)
- **RoBERTa-large** (Better performance)
- **twitter-roberta-base-sentiment** (Pre-trained on social media)

### Topic Modeling
- **Contextualized Topic Models (CTM)** (Combines BERT embeddings with topic modeling)
- **CombinedTM** (Best for general topic discovery)
- **ZeroShotTM** (Best for multilingual or cross-lingual analysis)

### Image Generation
- **Stable Diffusion XL** (High quality)
- **SDXL-Turbo** (Fast generation)

---

## 🎯 Topic Modeling for Viral Content

### Overview
The system now includes Contextualized Topic Models (CTM) for discovering themes and patterns in viral content. This helps understand what topics resonate with audiences.

### Quick Start: Topic Modeling
```python
from ml.topic_modeling import ViralTopicModeler
from core.config import Config
from core.database import Database

# Initialize
config = Config()
database = Database()
modeler = ViralTopicModeler(config, database)

# Analyze viral content
results = modeler.analyze_viral_content(
    platform="instagram",
    min_engagement=10000,
    limit=500
)

print(f"Discovered {results['num_topics']} topics:")
for topic_id, words in results['topics'].items():
    print(f"Topic {topic_id}: {', '.join(words[:5])}")
```

### Manual Topic Modeling Workflow
```python
# 1. Prepare your texts
texts = [
    "Amazing workout routine for beginners...",
    "Morning motivation tips...",
    "Healthy meal prep ideas..."
]

# 2. Prepare data
training_data = modeler.prepare_data(texts, use_stopwords=True)

# 3. Train model
model_path = modeler.train_model(
    training_data,
    num_topics=5,
    model_type="combined",
    num_epochs=100
)

# 4. Get topics
topics = modeler.get_topics(top_k=10)
for i, topic in enumerate(topics):
    print(f"Topic {i}: {topic}")

# 5. Predict topics for new content
new_texts = ["New fitness motivation post..."]
topic_dist = modeler.predict_topics(new_texts)
print(f"Topic distribution: {topic_dist}")
```

### Model Types

#### CombinedTM (Default)
Best for general-purpose topic modeling. Combines bag-of-words with contextual embeddings.
```python
modeler.train_model(training_data, model_type="combined")
```

#### ZeroShotTM
Best for multilingual content or when vocabulary might be incomplete.
```python
modeler.train_model(training_data, model_type="zeroshot")
```

### Integration with Content Strategy
```python
# Analyze what topics are trending
results = modeler.analyze_viral_content(platform="tiktok", limit=1000)

# Identify top performing topics
top_topics = sorted(
    results['topic_prevalence'].items(),
    key=lambda x: x[1],
    reverse=True
)[:3]

print("Top 3 trending topics:")
for topic_id, prevalence in top_topics:
    print(f"{results['topic_labels'][topic_id]}: {prevalence:.2%}")
```

### Best Practices for Topic Modeling
- ✅ Use at least 100-200 documents for reliable topics
- ✅ Start with 5-10 topics, adjust based on results
- ✅ Filter content by engagement (>10k recommended)
- ✅ Re-run analysis weekly to track topic trends
- ✅ Use topic insights to guide content creation

---

## 🔗 Resources

### Documentation
- Transformers: https://huggingface.co/docs/transformers
- Datasets: https://huggingface.co/docs/datasets
- PEFT (LoRA): https://huggingface.co/docs/peft
- Contextualized Topic Models: https://github.com/MilaNLProc/contextualized-topic-models

### Tutorials
- Fine-tune LLMs: https://huggingface.co/blog/llama2
- LoRA Training: https://huggingface.co/blog/lora
- CTM Documentation: https://contextualized-topic-models.readthedocs.io

### Community
- Forum: https://discuss.huggingface.co/
- Discord: https://discord.gg/hugging-face

---

## 🎉 Next Steps

1. ✅ Complete setup steps
2. ✅ Run first training workflow
3. ✅ Generate test captions
4. ✅ Integrate into content engine
5. ✅ Enable automated training
6. ✅ Run topic modeling on viral content
7. ✅ Monitor performance
8. ✅ Iterate and improve

---

**🚀 Ready to train? Start with the Quick Start guide above!**
