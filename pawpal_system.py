from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Owner:
    """Represents a pet owner."""
    owner_id: str
    name: str
    daily_time_available_min: int
    preferences: List[str] = field(default_factory=list)

    def set_reminder_preference(self, enabled: bool) -> None:
        """Set reminder preference for the owner."""
        pass

    def update_daily_time(self, minutes: int) -> None:
        """Update the owner's available time for pet care."""
        pass


@dataclass
class Pet:
    """Represents a pet."""
    pet_id: str
    name: str
    species: str
    age_years: int
    special_needs: List[str] = field(default_factory=list)

    def add_special_need(self, need: str) -> None:
        """Add a special need for the pet."""
        pass

    def remove_special_need(self, need: str) -> None:
        """Remove a special need from the pet."""
        pass


@dataclass
class CareTask:
    """Represents a pet care task."""
    task_id: str
    title: str
    category: str
    duration_min: int
    priority: int
    is_required: bool
    preferred_time_window: Optional[str] = None

    def is_high_priority(self) -> bool:
        """Check if this task is high priority."""
        pass

    def update_priority(self, new_priority: int) -> None:
        """Update the task's priority."""
        pass


@dataclass
class DailyConstraints:
    """Represents constraints for daily scheduling."""
    date: str
    available_time_min: int
    blocked_time_windows: List[str] = field(default_factory=list)
    allow_task_splitting: bool = False

    def can_schedule(self, duration_min: int) -> bool:
        """Check if a task of given duration can be scheduled."""
        pass

    def remaining_minutes(self, used_min: int) -> int:
        """Calculate remaining available minutes after using some time."""
        pass


@dataclass
class ScheduleItem:
    """Represents a scheduled task in the daily plan."""
    task_id: str
    start_time: str
    end_time: str
    status: str = "pending"

    def calculate_duration(self) -> int:
        """Calculate the duration of this schedule item in minutes."""
        pass

    def mark_completed(self) -> None:
        """Mark this schedule item as completed."""
        pass


@dataclass
class DailyPlan:
    """Represents a daily care plan."""
    date: str
    owner_id: str
    pet_id: str
    total_planned_min: int = 0
    total_remaining_min: int = 0
    schedule_items: List[ScheduleItem] = field(default_factory=list)
    explanation_notes: List[str] = field(default_factory=list)

    def add_item(self, schedule_item: ScheduleItem) -> None:
        """Add a schedule item to the plan."""
        pass

    def remove_item(self, task_id: str) -> None:
        """Remove a schedule item from the plan by task ID."""
        pass

    def summarize_plan(self) -> str:
        """Generate a summary of the daily plan."""
        pass


class Scheduler:
    """Handles scheduling logic for daily pet care plans."""

    def rank_tasks(self, tasks: List[CareTask]) -> List[CareTask]:
        """Rank tasks based on priority and constraints."""
        pass

    def build_plan(
        self,
        owner: Owner,
        pet: Pet,
        tasks: List[CareTask],
        constraints: DailyConstraints,
    ) -> DailyPlan:
        """Build a daily plan based on owner, pet, tasks, and constraints."""
        pass

    def explain_choices(self) -> List[str]:
        """Explain the reasoning behind scheduling choices."""
        pass


class TaskRepository:
    """Manages storage and retrieval of care tasks."""

    def __init__(self):
        """Initialize the task repository."""
        self.tasks: List[CareTask] = []

    def add_task(self, task: CareTask) -> None:
        """Add a new care task to the repository."""
        pass

    def update_task(self, task: CareTask) -> None:
        """Update an existing care task."""
        pass

    def delete_task(self, task_id: str) -> None:
        """Delete a care task by ID."""
        pass

    def get_all_tasks(self) -> List[CareTask]:
        """Retrieve all care tasks."""
        pass
