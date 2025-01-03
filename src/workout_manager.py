
from src.workout import Workout

class WorkoutManager():
    def __init__(self):
        self.workout = Workout()

    def set_target_power(self, power):
        print(f'Setting target power to {power} watts')

    def set_target_hr(self, hr_min, hr_max):
        print(f'Setting target HR range to {hr_min} - {hr_max} bpm')
    
    def set_gradient(self, gradient):
        print(f'Setting gradient to {gradient}%')   
    
    def set_wind_speed(self, wind_speed):
        print(f'Setting wind speed to {wind_speed} m/s')

    def start_workout(self):    
        self.workout.start_workout()

    def pause_workout(self, duration):
        self.workout.pause_workout()

    def stop_workout(self):
        self.workout.stop_workout()
