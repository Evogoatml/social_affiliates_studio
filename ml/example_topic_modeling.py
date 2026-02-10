"""
Example: Topic Modeling on Viral Content
Demonstrates how to use ViralTopicModeler for content analysis
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Constants
MIN_TOPIC_PROBABILITY = 0.1  # Minimum probability threshold for displaying topics

# Example viral content texts
EXAMPLE_VIRAL_POSTS = [
    "Morning workout motivation! 💪 Start your day with these 5 exercises #fitness #motivation #workout",
    "Healthy meal prep for the week 🥗 Quick and easy recipes #healthy #mealprep #nutrition",
    "Top 10 productivity hacks for entrepreneurs 🚀 #productivity #business #entrepreneur",
    "Beautiful sunset timelapse 🌅 Nature is amazing #nature #sunset #photography",
    "How to start your own business in 2024 💼 #business #startup #entrepreneur",
    "Best travel destinations in Europe ✈️ #travel #europe #wanderlust",
    "Quick morning yoga routine for beginners 🧘‍♀️ #yoga #wellness #mindfulness",
    "Delicious vegan recipes you need to try 🌱 #vegan #food #recipes",
    "Crypto trading tips for beginners 📈 #crypto #trading #bitcoin",
    "Home workout equipment essentials 💪 #fitness #homeworkout #gym",
    "Mental health awareness tips 🧠 Take care of yourself #mentalhealth #wellness #selfcare",
    "Photography tips for Instagram 📸 #photography #instagram #tips",
    "Best coding practices for developers 💻 #coding #programming #developer",
    "Fashion trends for spring 2024 👗 #fashion #style #trends",
    "Pet care tips for new owners 🐕 #pets #dogs #cats",
    "DIY home decor ideas 🏠 #diy #homedecor #interior",
    "Sustainable living tips ♻️ #sustainability #ecofriendly #green",
    "Language learning hacks 📚 #language #learning #education",
    "Investment strategies for beginners 💰 #investing #finance #money",
    "Relationship advice and tips ❤️ #relationships #love #dating"
]


def run_topic_modeling_example():
    """Run a simple example of topic modeling"""
    
    print("\n" + "="*60)
    print("Topic Modeling Example for Viral Content Analysis")
    print("="*60 + "\n")
    
    try:
        # Download NLTK stopwords if needed
        import nltk
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("Downloading NLTK stopwords...")
            nltk.download('stopwords', quiet=True)
        
        from ml.topic_modeling import ViralTopicModeler
        
        # Mock config and database for example
        class MockConfig:
            def get(self, key, default=None):
                return default
        
        class MockDatabase:
            def get_top_viral_content(self, platform=None, limit=100):
                return []
        
        config = MockConfig()
        database = MockDatabase()
        
        # Initialize modeler
        print("1. Initializing ViralTopicModeler...")
        modeler = ViralTopicModeler(config, database)
        print("   ✅ Modeler initialized\n")
        
        # Prepare data
        print("2. Preparing data from example viral posts...")
        training_data = modeler.prepare_data(
            texts=EXAMPLE_VIRAL_POSTS,
            use_stopwords=True
        )
        
        if training_data is None:
            print("   ❌ Failed to prepare data")
            return
        
        print(f"   ✅ Prepared {len(EXAMPLE_VIRAL_POSTS)} documents\n")
        
        # Train model
        print("3. Training topic model (this may take a minute)...")
        model_path = modeler.train_model(
            training_data,
            num_topics=5,
            model_type="combined",
            num_epochs=50  # Reduced for faster demo
        )
        
        if model_path is None:
            print("   ❌ Failed to train model")
            return
        
        print(f"   ✅ Model trained and saved to: {model_path}\n")
        
        # Get topics
        print("4. Discovered Topics:")
        print("-" * 60)
        topics = modeler.get_topics(top_k=8)
        
        for i, topic_words in enumerate(topics):
            print(f"\n   Topic {i}: {', '.join(topic_words[:8])}")
        
        print("\n" + "-" * 60 + "\n")
        
        # Predict topics for new content
        print("5. Predicting topics for new content...")
        new_posts = [
            "Amazing fitness transformation journey! 💪 #fitness #transformation",
            "Starting my travel blog today ✈️ #travel #blog"
        ]
        
        predictions = modeler.predict_topics(new_posts)
        
        if predictions.size > 0:
            for i, post in enumerate(new_posts):
                print(f"\n   Post: {post}")
                print(f"   Top topics:")
                
                # Get top 3 topics for this post
                top_topic_indices = predictions[i].argsort()[-3:][::-1]
                for idx in top_topic_indices:
                    prob = predictions[i][idx]
                    if prob > MIN_TOPIC_PROBABILITY:
                        topic_label = ', '.join(topics[idx][:3])
                        print(f"      - Topic {idx} ({topic_label}): {prob:.1%}")
        
        print("\n" + "="*60)
        print("✅ Topic modeling example completed successfully!")
        print("="*60 + "\n")
        
        print("Next steps:")
        print("- Run on real viral content from your database")
        print("- Adjust number of topics based on your data")
        print("- Use topic insights to guide content strategy")
        print(f"- Model saved at: {model_path}\n")
        
    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease install required packages:")
        print("   pip install contextualized-topic-models\n")
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_topic_modeling_example()
