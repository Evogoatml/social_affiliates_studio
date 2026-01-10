"""
Viral - Marketing Social Media Dataset Loader
Author: Auto-generated
Date: 2025-01-05
Description: Script to load and explore the marketing social media dataset from HuggingFace
"""

from datasets import load_dataset

def load_marketing_dataset():
    """
    Loads the marketing social media dataset from HuggingFace.
    
    Returns:
        Dataset object containing the marketing social media data
        
    Raises:
        Exception: If dataset loading fails
    """
    try:
        ds = load_dataset("RafaM97/marketing_social_media")
        return ds
    except Exception as e:
        print(f"Error loading dataset: {e}")
        raise


if __name__ == "__main__":
    # Load the dataset
    ds = load_marketing_dataset()
    
    # Display dataset information
    print("Dataset loaded successfully!")
    print(f"Dataset splits: {list(ds.keys())}")
    
    # Print information about each split
    for split_name, split_data in ds.items():
        print(f"\n{split_name} split:")
        print(f"  Number of examples: {len(split_data)}")
        print(f"  Features: {split_data.features}")
        
        # Show first example if available
        if len(split_data) > 0:
            print(f"  First example keys: {list(split_data[0].keys())}")
            print(f"\n  Sample data (first example):")
            first_example = split_data[0]
            for key, value in first_example.items():
                # Truncate long values for display
                display_value = str(value)
                if len(display_value) > 200:
                    display_value = display_value[:200] + "..."
                print(f"    {key}: {display_value}")
