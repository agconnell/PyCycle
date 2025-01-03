import unittest

import src
from src.config_manager import *

class TestConfigManager(unittest.TestCase):

    def test_config_manager(self):
        config = ConfigManager()
        config.set(USER_NAME, 'Foo Bar')
        config.set(WORKOUT_BY_POWER, False)
        config.set(TV_MODE, True)
        config.set(HR_ZONES, [1, 2, 3, 4, 5])
        config.set(ROLLING_RESISTANCE, 1.0)
        config.set(DRAG_COEFFICIENT, 1.0)
        config.set(TRAINER_ID, 'xxaa-1245')
        config.save_config()
        self.assertFalse(config.get(WORKOUT_BY_POWER))
