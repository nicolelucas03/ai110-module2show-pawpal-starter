from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime, time, timedelta


@dataclass
class Owner:
    """Represents a pet owner."""
    owner_id: str
    name: str
    daily_time_available_min: int
    preferences: List[str] = field(default_factory=list)

    def set_reminder_preference(self, enabled: bool) -> None:
        """Set reminder preference for the owner."""
        preference = "reminders_enabled" if enabled else "reminders_disabled"
        if preference not in self.preferences:
            self.preferences.append(preference)
        else:
            opposite = "reminders_disabled" if enabled else "reminders_enabled"
            if opposite in self.preferences:
                self.preferences.remove(opposite)

    def update_daily_time(self, minutes: int) -> None:
        """Update the owner's available time for pet care."""
        if minutes < 0:
            raise ValueError("Daily time available cannot be negative")
        self.daily_time_available_min = minutes


@dataclass
class Pet:
    """Represents a pet."""
    pet_id: str
    owner_id: str
    name: str
    species: str
    age_years: int
    special_needs: List[str] = field(default_factory=list)
    tasks: List['CareTask'] = field(default_factory=list)

    def add_special_need(self, need: str) -> None:
        """Add a special need for the pet."""
        if need not in self.special_needs:
            self.special_needs.append(need)

    def remove_special_need(self, need: str) -> None:
        """Remove a special need from the pet."""
        if need in self.special_needs:
            self.special_needs.remove(need)

    def add_task(self, task: 'CareTask') -> None:
        """Add a care task to this pet."""
        if task.pet_id != self.pet_id:
            raise ValueError("Task pet_id does not match this pet")
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return number of tasks assigned to this pet."""
        return len(self.tasks)


@dataclass
class CareTask:
    """Represents a pet care task."""
    task_id: str
    pet_id: str
    title: str
    category: str
    duration_min: int
    priority: int  # Valid range: 1-5 (1=low, 5=critical)
    is_required: bool
    preferred_time_window: Optional[str] = None

    def __post_init__(self):
        """Validate priority bounds after initialization."""
        if not 1 <= self.priority <= 5:
            raise ValueError("Priority must be between 1 (low) and 5 (critical)")
        if self.duration_min <= 0:
            raise ValueError("Duration must be positive")

    """Return True when this task's priority is 4 or higher."""
    def is_high_priority(self) -> bool:
        """Check if this task is high priority (priority >= 4)."""
        return self.priority >= 4

    def update_priority(self, new_priority: int) -> None:
        """Update the task's priority."""
        if not 1 <= new_priority <= 5:
            raise ValueError("Priority must be between 1 (low) and 5 (critical)")
        self.priority = new_priority


@dataclass
class DailyConstraints:
    """Represents constraints for daily scheduling."""
    date: str
    available_time_min: int
    blocked_time_windows: List[str] = field(default_factory=list)
    allow_task_splitting: bool = False

    def can_schedule(self, duration_min: int) -> bool:
        """Check if a task of given duration can be scheduled."""
        # For now, simple check: does it fit in available time?
        # A more sophisticated version would factor in blocked windows
        return duration_min <= self.available_time_min

    def remaining_minutes(self, used_min: int) -> int:
        """Calculate remaining available minutes after using some time."""
        remaining = self.available_time_min - used_min
        return max(0, remaining)


@dataclass
class ScheduleItem:
    """Represents a scheduled task in the daily plan."""
    task_id: str
    task: 'CareTask'  # Reference to the actual task object
    start_time: datetime
    end_time: datetime
    status: str = "pending"  # pending, completed, skipped

    def calculate_duration(self) -> int:
        """Calculate the duration of this schedule item in minutes."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)

    def mark_completed(self) -> None:
        """Mark this schedule item as completed."""
        self.status = "completed"

    def mark_complete(self) -> None:
        """Compatibility alias for mark_completed."""
        self.mark_completed()


@dataclass
class DailyPlan:
    """Represents a daily care plan."""
    date: str
    owner: 'Owner'  # Reference to the owner
    pet: 'Pet'  # Reference to the pet
    constraints: 'DailyConstraints'  # Constraints used to build this plan
    total_planned_min: int = 0
    total_remaining_min: int = 0
    schedule_items: List[ScheduleItem] = field(default_factory=list)
    explanation_notes: List[str] = field(default_factory=list)

    def add_item(self, schedule_item: ScheduleItem) -> None:
        """Add a schedule item to the plan with validation."""
        # Validate time order
        if schedule_item.start_time >= schedule_item.end_time:
            raise ValueError("Start time must be before end time")
        
        # Check for duplicate tasks
        if any(item.task_id == schedule_item.task_id for item in self.schedule_items):
            raise ValueError(f"Task {schedule_item.task_id} already scheduled")
        
        # Check for time overlaps
        for existing_item in self.schedule_items:
            if not (schedule_item.end_time <= existing_item.start_time or 
                    schedule_item.start_time >= existing_item.end_time):
                raise ValueError(
                    f"Time conflict: overlaps with {existing_item.task_id} "
                    f"({existing_item.start_time} - {existing_item.end_time})"
                )
        
        # Calculate total time if item is added
        new_duration = schedule_item.calculate_duration()
        current_used_time = sum(item.calculate_duration() for item in self.schedule_items)
        total_needed = current_used_time + new_duration
        
        if total_needed > self.constraints.available_time_min:
            raise ValueError(
                f"Total time ({total_needed}min) exceeds available time "
                f"({self.constraints.available_time_min}min)"
            )
        
        # All checks passed, add the item
        self.schedule_items.append(schedule_item)
        self.total_planned_min = total_needed
        self.total_remaining_min = self.constraints.available_time_min - total_needed

    def remove_item(self, task_id: str) -> None:
        """Remove a schedule item from the plan by task ID."""
        self.schedule_items = [item for item in self.schedule_items if item.task_id != task_id]
        
        # Recalculate totals
        self.total_planned_min = sum(item.calculate_duration() for item in self.schedule_items)
        self.total_remaining_min = self.constraints.available_time_min - self.total_planned_min

    def summarize_plan(self) -> str:
        """Generate a summary of the daily plan."""
        lines = [
            f"📅 Daily Plan for {self.pet.name} on {self.date}",
            f"⏰ Available time: {self.constraints.available_time_min} minutes",
            f"✓ Scheduled: {self.total_planned_min} minutes | Remaining: {self.total_remaining_min} minutes",
            ""
        ]
        
        if not self.schedule_items:
            lines.append("No tasks scheduled.")
        else:
            lines.append("Schedule:")
            for item in self.schedule_items:
                duration = item.calculate_duration()
                time_str = item.start_time.strftime("%H:%M") + " - " + item.end_time.strftime("%H:%M")
                lines.append(f"  • {item.task.title} ({duration}min) - {time_str} [{item.status}]")
        
        if self.explanation_notes:
            lines.append("")
            lines.append("Reasoning:")
            for note in self.explanation_notes:
                lines.append(f"  • {note}")
        
        return "\n".join(lines)


class Scheduler:
    """Handles scheduling logic for daily pet care plans."""

    def __init__(self):
        """Initialize the scheduler."""
        self.last_plan: Optional[DailyPlan] = None

    def rank_tasks(self, tasks: List[CareTask]) -> List[CareTask]:
        """Rank tasks based on priority and constraints."""
        # Sort by: required first, then by priority (descending)
        ranked = sorted(
            tasks,
            key=lambda t: (-int(t.is_required), -t.priority),
            reverse=False
        )
        return ranked

    def build_plan(
        self,
        owner: Owner,
        pet: Pet,
        tasks: List[CareTask],
        constraints: DailyConstraints,
    ) -> DailyPlan:
        """Build a daily plan based on owner, pet, tasks, and constraints."""
        plan = DailyPlan(
            date=constraints.date,
            owner=owner,
            pet=pet,
            constraints=constraints
        )
        
        # Rank tasks
        ranked_tasks = self.rank_tasks(tasks)
        
        # Try to schedule tasks, starting at 8:00 AM
        current_time = datetime.strptime(f"{constraints.date} 08:00", "%Y-%m-%d %H:%M")
        scheduled_items = []
        
        for task in ranked_tasks:
            # Check if task fits in remaining time
            remaining = constraints.remaining_minutes(
                sum(item.calculate_duration() for item in scheduled_items)
            )
            
            if task.duration_min <= remaining:
                # Create schedule item with end time
                end_time = current_time + timedelta(minutes=task.duration_min)
                schedule_item = ScheduleItem(
                    task_id=task.task_id,
                    task=task,
                    start_time=current_time,
                    end_time=end_time,
                    status="pending"
                )
                
                try:
                    plan.add_item(schedule_item)
                    scheduled_items.append(schedule_item)
                    plan.explanation_notes.append(
                        f"Scheduled '{task.title}' (priority {task.priority}, {task.duration_min}min)"
                    )
                    current_time = end_time
                except ValueError as e:
                    plan.explanation_notes.append(f"Skipped '{task.title}': {str(e)}")
            else:
                if task.is_required:
                    plan.explanation_notes.append(
                        f"⚠️ Required task '{task.title}' could not fit in schedule (needs {task.duration_min}min, "
                        f"only {remaining}min available)"
                    )
        
        self.last_plan = plan
        return plan

    def explain_choices(self, plan: DailyPlan) -> List[str]:
        """Explain the reasoning behind scheduling choices for a given plan."""
        if not plan:
            return ["No plan to explain."]
        
        explanations = [
            f"Generated plan for {plan.pet.name} on {plan.date}:",
            f"Available time: {plan.constraints.available_time_min} minutes for pet owner {plan.owner.name}"
        ]
        
        explanations.extend(plan.explanation_notes)
        
        return explanations

    def get_owner_all_tasks(
        self,
        owner: Owner,
        pet_repo: 'PetRepository',
        task_repo: 'TaskRepository',
    ) -> List[CareTask]:
        """Retrieve all tasks for all of an owner's pets."""
        pets = pet_repo.get_pets_by_owner(owner.owner_id)
        all_tasks = []
        for pet in pets:
            tasks = task_repo.get_tasks_by_pet(pet.pet_id)
            all_tasks.extend(tasks)
        return all_tasks


class TaskRepository:
    """Manages storage and retrieval of care tasks."""

    def __init__(self):
        """Initialize the task repository."""
        self.tasks: Dict[str, CareTask] = {}  # task_id -> CareTask

    def add_task(self, task: CareTask) -> None:
        """Add a new care task to the repository."""
        if task.task_id in self.tasks:
            raise ValueError(f"Task {task.task_id} already exists")
        self.tasks[task.task_id] = task

    def update_task(self, task: CareTask) -> None:
        """Update an existing care task."""
        if task.task_id not in self.tasks:
            raise ValueError(f"Task {task.task_id} not found")
        self.tasks[task.task_id] = task

    def delete_task(self, task_id: str) -> None:
        """Delete a care task by ID."""
        if task_id in self.tasks:
            del self.tasks[task_id]

    def get_all_tasks(self) -> List[CareTask]:
        """Retrieve all care tasks."""
        return list(self.tasks.values())

    def get_task_by_id(self, task_id: str) -> Optional[CareTask]:
        """Retrieve a specific task by ID."""
        return self.tasks.get(task_id)

    def get_tasks_by_pet(self, pet_id: str) -> List[CareTask]:
        """Retrieve all tasks for a specific pet."""
        return [task for task in self.tasks.values() if task.pet_id == pet_id]

    def get_tasks_by_category(self, category: str) -> List[CareTask]:
        """Retrieve all tasks in a specific category."""
        return [task for task in self.tasks.values() if task.category == category]

    def get_required_tasks(self, pet_id: str) -> List[CareTask]:
        """Retrieve all required tasks for a specific pet."""
        return [
            task
            for task in self.tasks.values()
            if task.pet_id == pet_id and task.is_required
        ]

    def get_tasks_by_priority(self, pet_id: str, min_priority: int) -> List[CareTask]:
        """Retrieve tasks for a pet with priority >= min_priority."""
        return [
            task
            for task in self.tasks.values()
            if task.pet_id == pet_id and task.priority >= min_priority
        ]


class PetRepository:
    """Manages storage and retrieval of pets."""

    def __init__(self):
        """Initialize the pet repository."""
        self.pets: Dict[str, Pet] = {}  # pet_id -> Pet

    def add_pet(self, pet: Pet) -> None:
        """Add a new pet to the repository."""
        if pet.pet_id in self.pets:
            raise ValueError(f"Pet {pet.pet_id} already exists")
        self.pets[pet.pet_id] = pet

    def update_pet(self, pet: Pet) -> None:
        """Update an existing pet."""
        if pet.pet_id not in self.pets:
            raise ValueError(f"Pet {pet.pet_id} not found")
        self.pets[pet.pet_id] = pet

    def delete_pet(self, pet_id: str) -> None:
        """Delete a pet by ID."""
        if pet_id in self.pets:
            del self.pets[pet_id]

    def get_all_pets(self) -> List[Pet]:
        """Retrieve all pets."""
        return list(self.pets.values())

    def get_pet_by_id(self, pet_id: str) -> Optional[Pet]:
        """Retrieve a specific pet by ID."""
        return self.pets.get(pet_id)

    def get_pets_by_owner(self, owner_id: str) -> List[Pet]:
        """Retrieve all pets owned by a specific owner."""
        return [pet for pet in self.pets.values() if pet.owner_id == owner_id]
