
import pytest
import asyncio
import time

from src.workout_manager import WorkoutManager

@pytest.mark.asyncio
async def test_workout_manager():
    print('testing workout manager')
    workout_manager = WorkoutManager()

    workout_manager.set_gradient(5)