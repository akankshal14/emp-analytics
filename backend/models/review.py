from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Review:

    review_id: Optional[int] = None

    employee_id: int = 0

    review_date: Optional[date] = None

    performance_rating: int = 3

    reviewer_id: Optional[int] = None

    comments: str = ""