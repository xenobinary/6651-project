from statistics import mean, pstdev
from typing import Dict, List, Tuple


def colors_used(coloring: Dict[int, int]) -> int:
    return max(coloring.values()) if coloring else 0


def compute_competitive_ratio(coloring: Dict[int, int], chromatic_number: int) -> float:
    if chromatic_number <= 0:
        raise ValueError("chromatic_number must be positive")
    return colors_used(coloring) / chromatic_number


def aggregate(ratios: List[float]) -> Tuple[float, float]:
    if not ratios:
        return 0.0, 0.0
    avg = mean(ratios)
    # population std dev consistent with definition over all generated graphs
    sd = pstdev(ratios) if len(ratios) > 1 else 0.0
    return avg, sd
