import pytest
from app.rpg_utils import (
    calculate_boss_phase,
    get_phase_name,
    BOSS_DIFFICULTY,
    calculate_region_progress,
    calculate_world_progress,
)


class TestBossDifficulty:
    def test_boss_hp_by_difficulty(self):
        # Test different difficulties
        easy_config = BOSS_DIFFICULTY["EASY"]
        medium_config = BOSS_DIFFICULTY["MEDIUM"]
        hard_config = BOSS_DIFFICULTY["HARD"]
        epic_config = BOSS_DIFFICULTY["EPIC"]

        assert easy_config["max_hp"] == 1000
        assert medium_config["max_hp"] == 2500
        assert hard_config["max_hp"] == 5000
        assert epic_config["max_hp"] == 10000


class TestBossPhase:
    def test_boss_phase_calculation(self):
        # Phase 1 (100% -> 80%)
        phase = calculate_boss_phase(10000, 10000)
        assert phase == 1

        # Phase 2 (80% -> 60%)
        phase = calculate_boss_phase(7500, 10000)
        assert phase == 2

        # Phase 3 (60% -> 40%)
        phase = calculate_boss_phase(5000, 10000)
        assert phase == 3

        # Phase 4 (40% -> 20%)
        phase = calculate_boss_phase(2500, 10000)
        assert phase == 4

        # Phase 5 (20% -> 0%)
        phase = calculate_boss_phase(1000, 10000)
        assert phase == 5

    def test_boss_defeat_detection(self):
        phase = calculate_boss_phase(0, 10000)
        assert phase == 5  # Final phase or defeated state


class TestRegionProgress:
    def test_region_progress_calculation(self):
        # No quests
        progress = calculate_region_progress("Work", 0, 0)
        assert progress == 0

        # All quests completed
        progress = calculate_region_progress("Work", 10, 10)
        assert progress == 100

        # Half completed
        progress = calculate_region_progress("Work", 5, 10)
        assert progress == 50

    def test_world_progress_average(self):
        # All regions at 0%
        region_progresses = {
            "Work": 0,
            "Learning": 0,
            "Health": 0,
            "Creative": 0,
            "Wellness": 0,
        }
        world_progress = calculate_world_progress(region_progresses)
        assert world_progress == 0

        # All regions at 100%
        region_progresses = {
            "Work": 100,
            "Learning": 100,
            "Health": 100,
            "Creative": 100,
            "Wellness": 100,
        }
        world_progress = calculate_world_progress(region_progresses)
        assert world_progress == 100

        # Mixed progress
        region_progresses = {
            "Work": 50,
            "Learning": 75,
            "Health": 25,
            "Creative": 100,
            "Wellness": 0,
        }
        world_progress = calculate_world_progress(region_progresses)
        assert world_progress == 50  # Average of 50, 75, 25, 100, 0 = 250/5 = 50
