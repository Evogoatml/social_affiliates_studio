# Brain Auto Initialization

This script initializes the brain of the agent automatically using the contents of AGENT.md files.

import os

class BrainAutoInitializer:
    def __init__(self, agent_directory):
        self.agent_directory = agent_directory
        self.agents = []

    def load_agents(self):
        for filename in os.listdir(self.agent_directory):
            if filename.endswith('.md') and 'AGENT' in filename:
                with open(os.path.join(self.agent_directory, filename), 'r') as file:
                    self.agents.append(file.read())

    def initialize_brain(self):
        self.load_agents()
        # Further initialization logic goes here
        print('Brain initialized with the following agents:')
        for agent in self.agents:
            print(agent)

if __name__ == '__main__':
    initializer = BrainAutoInitializer('./agents')
    initializer.initialize_brain()