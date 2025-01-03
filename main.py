import time
import asyncio

from src.config_manager import ConfigManager
from src.config_manager import USER_NAME, WORKOUT_BY_POWER,TV_MODE,HR_ZONES,ROLLING_RESISTANCE,DRAG_COEFFICIENT,TRAINER_ID
from src.workout_manager import WorkoutManager

def main():
    config = ConfigManager()
    print(f'User name: {config.get(USER_NAME)}')

    workout_manager = WorkoutManager()
    workout_manager.start_workout()

if __name__ == '__main__':  
    main()