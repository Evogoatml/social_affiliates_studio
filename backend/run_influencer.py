import datetime

class InfluencerContentGenerator:
    def __init__(self, influencer_name, niche):
        self.influencer_name = influencer_name
        self.niche = niche

    def generate_post(self):
        current_time = datetime.datetime.now()
        caption = f"{self.influencer_name} is sharing insights on {self.niche} at {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        return caption

if __name__ == '__main__':
    influencer = InfluencerContentGenerator('Jane Doe', 'Fitness')
    post = influencer.generate_post()
    print(post)