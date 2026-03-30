from datetime import datetime, timedelta

from pawpal_system import CareTask, Pet, ScheduleItem


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
