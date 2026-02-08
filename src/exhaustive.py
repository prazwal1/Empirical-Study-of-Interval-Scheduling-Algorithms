# src/exhaustive.py
from typing import List, Tuple

class BruteForceScheduler:
    def __init__(self, jobs: List[Tuple[float, float]]):
        self.jobs = jobs

    def schedule_jobs(self) -> List[Tuple[float, float]]:
        """Find optimal schedule using exhaustive search (2^n)"""
        n = len(self.jobs)
        max_count = 0
        best_schedule = []

        # Try all 2^n subsets
        for mask in range(1 << n):
            subset = [self.jobs[i] for i in range(n) if (mask & (1 << i))]
            
            if self.is_valid(subset):
                if len(subset) > max_count:
                    max_count = len(subset)
                    best_schedule = subset[:]

        return best_schedule

    def is_valid(self, schedule: List[Tuple[float, float]]) -> bool:
        """Check if schedule has no overlapping intervals"""
        if not schedule:
            return True
        schedule = sorted(schedule, key=lambda x: x[1])  # sort by finish time
        for i in range(1, len(schedule)):
            if schedule[i][0] < schedule[i-1][1]:
                return False
        return True