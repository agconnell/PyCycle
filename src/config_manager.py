import json
import os

# Constants for the configuration keys
USER_NAME = 'user_name'
WORKOUT_BY_POWER = 'workout_by_power'
TV_MODE = 'tv_mode'
HR_ZONES = 'hr_zones'
ROLLING_RESISTANCE = 'rolling_resistance'
DRAG_COEFFICIENT = 'drag_coefficient'
TRAINER_ID = 'trainer_id'

# Class to manage the configuration of the application
class ConfigManager():

    def __init__(self, config_file=None):
        if config_file:
            self.config_file = config_file
        else:
            self.config_file = os.path.join(os.getcwd(), 'config', 'config.json')

        if os.path.exists(self.config_file):
            self.load_config()
        else:
            self.config = {
                USER_NAME: 'Alan Connell',
                WORKOUT_BY_POWER: False,
                TV_MODE: False,
                HR_ZONES: [120, 140, 155, 165],
                ROLLING_RESISTANCE: 0.0,
                DRAG_COEFFICIENT: 0.0,
                TRAINER_ID: 'FB:4A:F1:1F:1B:73'
            }
            self.save_config()
        # print(f'self.config: {self.config}')

    def load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

    def save_config(self, file_path=None):
        if file_path:
            self.config_file = file_path
        else:
            if not os.path.exists(os.path.dirname(self.config_file)):
                os.makedirs(os.path.dirname(self.config_file))

        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def get(self, key):
        return self.config[key]

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
