# Influencer Persona Definitions

class Influencer:
    def __init__(self, name, niche, follower_count, engagement_rate):
        self.name = name
        self.niche = niche
        self.follower_count = follower_count
        self.engagement_rate = engagement_rate

    def __repr__(self):
        return f"<Influencer(name={self.name}, niche={self.niche}, follower_count={self.follower_count}, engagement_rate={self.engagement_rate})>"

# Example influencer personas

influencers = [
    Influencer("Alice", "Fitness", 120000, 0.05),
    Influencer("Bob", "Fashion", 80000, 0.07),
    Influencer("Charlie", "Technology", 200000, 0.04),
    Influencer("Diana", "Food", 150000, 0.06)
]