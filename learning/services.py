from __future__ import annotations

from datetime import timedelta
from django.utils import timezone

def next_due_for_result(is_correct: bool, current_streak: int):
    """Tiny helper for scheduling next review.

    This is NOT a full SRS algorithm (like SM-2). It's a simple demo:
    - correct => increase streak, next due later
    - wrong   => reset streak, next due soon
    """
    now = timezone.now()
    if is_correct:
        streak = current_streak + 1
        # 1d, 2d, 4d, 7d, 14d...
        days = 1 if streak == 1 else (2 if streak == 2 else (4 if streak == 3 else (7 if streak == 4 else 14)))
        return streak, now + timedelta(days=days)
    return 0, now + timedelta(hours=6)
