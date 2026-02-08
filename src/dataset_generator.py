import random
from typing import List, Tuple

def generate_dataset(n: int, alpha: float, D: int = 100) -> List[Tuple[float, float]]:
    """
    Generate uniform random interval dataset
    alpha controls overlap density:
        0.1 → High overlap
        1.0 → Medium
        5.0 → Low overlap
    """
    T = alpha * n * D
    jobs = []
    for _ in range(n):
        start = random.uniform(0, T)
        duration = random.uniform(1, D)
        finish = start + duration
        jobs.append((start, finish))
    
    return jobs