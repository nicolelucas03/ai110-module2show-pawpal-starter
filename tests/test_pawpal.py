from datetime import datetime, timedelta

import pytest

from pawpal_system import CareTask, Pet, ScheduleItem, Scheduler, TaskRepository, PetRepository, DailyPlan, Owner, DailyConstraints


def test_task_completion_changes_status() -> None:
	task = CareTask(
		task_id="t1",
		pet_id="p1",
		title="Walk",
		category="exercise",
		duration_min=30,
		priority=5,
		is_required=True,
	)
	item = ScheduleItem(
		task_id=task.task_id,
		task=task,
		start_time=datetime(2026, 3, 30, 8, 0),
		end_time=datetime(2026, 3, 30, 8, 30),
	)

	assert item.status == "pending"
	item.mark_complete()
	assert item.status == "completed"


def test_adding_task_to_pet_increases_task_count() -> None:
	pet = Pet(
		pet_id="p1",
		owner_id="o1",
		name="Max",
		species="Dog",
		age_years=4,
	)
	task = CareTask(
		task_id="t2",
		pet_id=pet.pet_id,
		title="Feed",
		category="care",
		duration_min=10,
		priority=3,
		is_required=True,
	)

	before = pet.task_count()
	pet.add_task(task)

	assert pet.task_count() == before + 1


def test_scheduler_ranks_by_required_then_hhmm_time_then_priority() -> None:
	scheduler = Scheduler()
	tasks = [
		CareTask(
			task_id="t1",
			pet_id="p1",
			title="Later required",
			category="care",
			duration_min=20,
			priority=5,
			is_required=True,
			time="10:00",
		),
		CareTask(
			task_id="t2",
			pet_id="p1",
			title="Earlier required",
			category="care",
			duration_min=20,
			priority=4,
			is_required=True,
			time="09:00",
		),
		CareTask(
			task_id="t3",
			pet_id="p1",
			title="Optional no explicit time",
			category="care",
			duration_min=20,
			priority=5,
			is_required=False,
		),
	]

	ranked = scheduler.rank_tasks(tasks)

	assert [task.task_id for task in ranked] == ["t2", "t1", "t3"]


def test_get_tasks_by_pet_name_filters_case_insensitive() -> None:
	pet_repo = PetRepository()
	task_repo = TaskRepository()

	max_pet = Pet(
		pet_id="p_max",
		owner_id="o1",
		name="Max",
		species="Dog",
		age_years=4,
	)
	luna_pet = Pet(
		pet_id="p_luna",
		owner_id="o1",
		name="Luna",
		species="Cat",
		age_years=3,
	)
	pet_repo.add_pet(max_pet)
	pet_repo.add_pet(luna_pet)

	task_repo.add_task(
		CareTask(
			task_id="t_max_1",
			pet_id=max_pet.pet_id,
			title="Walk",
			category="exercise",
			duration_min=30,
			priority=5,
			is_required=True,
		)
	)
	task_repo.add_task(
		CareTask(
			task_id="t_luna_1",
			pet_id=luna_pet.pet_id,
			title="Feed",
			category="care",
			duration_min=10,
			priority=4,
			is_required=True,
		)
	)

	max_tasks = task_repo.get_tasks_by_pet_name("max", pet_repo)

	assert [task.task_id for task in max_tasks] == ["t_max_1"]


def test_get_tasks_by_pet_name_raises_for_empty_name() -> None:
	pet_repo = PetRepository()
	task_repo = TaskRepository()

	with pytest.raises(ValueError, match="Pet name cannot be empty"):
		task_repo.get_tasks_by_pet_name("   ", pet_repo)


def test_complete_schedule_item_creates_next_daily_instance() -> None:
	task_repo = TaskRepository()
	scheduler = Scheduler()
	recurring_task = CareTask(
		task_id="daily_walk",
		pet_id="p1",
		title="Daily Walk",
		category="exercise",
		duration_min=30,
		priority=5,
		is_required=True,
		time="09:15",
		recurrence="daily",
	)
	task_repo.add_task(recurring_task)

	item = ScheduleItem(
		task_id=recurring_task.task_id,
		task=recurring_task,
		start_time=datetime(2026, 3, 30, 9, 15),
		end_time=datetime(2026, 3, 30, 9, 45),
	)

	next_task = scheduler.complete_schedule_item(item, task_repo)

	assert item.status == "completed"
	assert next_task is not None
	assert next_task.recurrence == "daily"
	assert next_task.time == "09:15"
	assert next_task.task_id != recurring_task.task_id
	assert task_repo.get_task_by_id(next_task.task_id) is not None


def test_complete_schedule_item_returns_none_for_non_recurring_task() -> None:
	task_repo = TaskRepository()
	scheduler = Scheduler()
	non_recurring_task = CareTask(
		task_id="one_time_feed",
		pet_id="p1",
		title="Feed",
		category="care",
		duration_min=10,
		priority=4,
		is_required=True,
	)
	task_repo.add_task(non_recurring_task)

	item = ScheduleItem(
		task_id=non_recurring_task.task_id,
		task=non_recurring_task,
		start_time=datetime(2026, 3, 30, 7, 0),
		end_time=datetime(2026, 3, 30, 7, 10),
	)

	next_task = scheduler.complete_schedule_item(item, task_repo)

	assert item.status == "completed"
	assert next_task is None


def test_detect_conflicts_returns_warning_messages() -> None:
	scheduler = Scheduler()
	task1 = CareTask(
		task_id="t1",
		pet_id="p1",
		title="Morning Walk",
		category="exercise",
		duration_min=30,
		priority=5,
		is_required=True,
	)
	task2 = CareTask(
		task_id="t2",
		pet_id="p1",
		title="Medication",
		category="health",
		duration_min=15,
		priority=5,
		is_required=True,
	)

	item1 = ScheduleItem(
		task_id=task1.task_id,
		task=task1,
		start_time=datetime(2026, 3, 30, 9, 0),
		end_time=datetime(2026, 3, 30, 9, 30),
	)
	item2 = ScheduleItem(
		task_id=task2.task_id,
		task=task2,
		start_time=datetime(2026, 3, 30, 9, 15),
		end_time=datetime(2026, 3, 30, 9, 30),
	)

	warnings = scheduler.detect_conflicts([item1, item2], "p1")

	assert len(warnings) == 1
	assert "Time conflict" in warnings[0]


def test_add_item_with_warning_does_not_raise_on_overlap() -> None:
	scheduler = Scheduler()
	owner = Owner(owner_id="o1", name="Alex", daily_time_available_min=120)
	pet = Pet(pet_id="p1", owner_id="o1", name="Max", species="Dog", age_years=4)
	constraints = DailyConstraints(date="2026-03-30", available_time_min=120)
	plan = DailyPlan(date="2026-03-30", owner=owner, pet=pet, constraints=constraints)

	task1 = CareTask(
		task_id="t1",
		pet_id="p1",
		title="Walk",
		category="exercise",
		duration_min=30,
		priority=5,
		is_required=True,
	)
	task2 = CareTask(
		task_id="t2",
		pet_id="p1",
		title="Vet Prep",
		category="care",
		duration_min=20,
		priority=4,
		is_required=True,
	)

	first = ScheduleItem(
		task_id=task1.task_id,
		task=task1,
		start_time=datetime(2026, 3, 30, 9, 0),
		end_time=datetime(2026, 3, 30, 9, 30),
	)
	second = ScheduleItem(
		task_id=task2.task_id,
		task=task2,
		start_time=datetime(2026, 3, 30, 9, 10),
		end_time=datetime(2026, 3, 30, 9, 30),
	)

	assert scheduler.add_item_with_warning(plan, first) is None
	warning = scheduler.add_item_with_warning(plan, second)

	assert warning is not None
	assert "overlaps with" in warning
	assert len(plan.schedule_items) == 1
