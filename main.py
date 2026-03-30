"""
Demo script for PawPal+ - Pet Care Scheduling System
Shows how to create owners, pets, tasks, and generate a daily schedule.
"""

from datetime import datetime
from pawpal_system import (
    Owner,
    Pet,
    CareTask,
    DailyConstraints,
    TaskRepository,
    PetRepository,
    Scheduler,
)


def main():
    """Main demo function."""
    
    # ===== Setup: Create Repositories =====
    pet_repo = PetRepository()
    task_repo = TaskRepository()
    scheduler = Scheduler()
    
    # ===== Create Owner =====
    owner = Owner(
        owner_id="owner_001",
        name="Sarah",
        daily_time_available_min=120,  # 2 hours available
        preferences=["reminders_enabled"]
    )
    owner.set_reminder_preference(True)
    print(f"👤 Owner created: {owner.name}")
    print(f"   Available time: {owner.daily_time_available_min} minutes\n")
    
    # ===== Create Pets =====
    dog = Pet(
        pet_id="pet_001",
        owner_id=owner.owner_id,
        name="Max",
        species="Dog",
        age_years=3,
        special_needs=["loves outdoor walks", "needs water breaks"]
    )
    dog.add_special_need("reactive on leash")
    pet_repo.add_pet(dog)
    
    cat = Pet(
        pet_id="pet_002",
        owner_id=owner.owner_id,
        name="Luna",
        species="Cat",
        age_years=5,
        special_needs=["medication at noon"]
    )
    pet_repo.add_pet(cat)
    
    print(f"🐕 Pet created: {dog.name} ({dog.species})")
    print(f"   Special needs: {', '.join(dog.special_needs)}")
    print(f"🐱 Pet created: {cat.name} ({cat.species})")
    print(f"   Special needs: {', '.join(cat.special_needs)}\n")
    
    # ===== Create Tasks for Max (Dog) =====
    task1 = CareTask(
        task_id="task_001",
        pet_id=dog.pet_id,
        title="Morning Walk",
        category="exercise",
        duration_min=30,
        priority=5,  # Critical
        is_required=True,
        preferred_time_window="morning",
        time="08:30"
    )
    task_repo.add_task(task1)
    
    task2 = CareTask(
        task_id="task_002",
        pet_id=dog.pet_id,
        title="Afternoon Play Session",
        category="enrichment",
        duration_min=20,
        priority=4,  # High
        is_required=False,
        preferred_time_window="afternoon",
        time="14:00"
    )
    task_repo.add_task(task2)

    # Added out of order on purpose to demo time-based sorting.
    # This shares the same time as Morning Walk to demonstrate same-time tasks.
    task5 = CareTask(
        task_id="task_005",
        pet_id=dog.pet_id,
        title="Breakfast Feeding",
        category="care",
        duration_min=15,
        priority=5,
        is_required=True,
        time="08:30"
    )
    task_repo.add_task(task5)

    task6 = CareTask(
        task_id="task_006",
        pet_id=dog.pet_id,
        title="Evening Potty Break",
        category="care",
        duration_min=10,
        priority=3,
        is_required=True,
        time="18:00"
    )
    task_repo.add_task(task6)
    
    # ===== Create Task for Luna (Cat) =====
    task3 = CareTask(
        task_id="task_003",
        pet_id=cat.pet_id,
        title="Medication & Feeding",
        category="health",
        duration_min=15,
        priority=5,  # Critical
        is_required=True,
        preferred_time_window="noon"
    )
    task_repo.add_task(task3)
    
    # ===== Create Additional Task for Luna =====
    task4 = CareTask(
        task_id="task_004",
        pet_id=cat.pet_id,
        title="Litter Box Cleaning",
        category="care",
        duration_min=10,
        priority=2,  # Low
        is_required=False
    )
    task_repo.add_task(task4)
    
    print("📋 Tasks created:")
    for task in task_repo.get_all_tasks():
        priority_label = "🔴 Critical" if task.priority == 5 else (
            "🟠 High" if task.priority >= 4 else "🟡 Medium"
        )
        print(f"   • {task.title} ({task.duration_min}min) - {priority_label} - "
              f"{'Required' if task.is_required else 'Optional'}")
    print()
    
    # ===== Generate Schedules for Each Pet =====
    today = datetime.now().strftime("%Y-%m-%d")
    constraints = DailyConstraints(
        date=today,
        available_time_min=owner.daily_time_available_min,
        blocked_time_windows=[],
        allow_task_splitting=False
    )
    
    print("=" * 70)
    print("📅 TODAY'S SCHEDULE".center(70))
    print("=" * 70)
    print()
    
    # Schedule for Max
    dog_tasks = task_repo.get_tasks_by_pet(dog.pet_id)
    dog_plan = scheduler.build_plan(owner, dog, dog_tasks, constraints)
    print(dog_plan.summarize_plan())
    print()
    print("Scheduling Reasoning:")
    for explanation in scheduler.explain_choices(dog_plan):
        print(f"  • {explanation}")
    print()
    print("-" * 70)
    print()
    
    # Schedule for Luna
    cat_tasks = task_repo.get_tasks_by_pet(cat.pet_id)
    cat_plan = scheduler.build_plan(owner, cat, cat_tasks, constraints)
    print(cat_plan.summarize_plan())
    print()
    print("Scheduling Reasoning:")
    for explanation in scheduler.explain_choices(cat_plan):
        print(f"  • {explanation}")
    print()
    print("=" * 70)
    
    # ===== Query Examples =====
    print("\n📊 REPOSITORY QUERY EXAMPLES:\n")
    
    # Get all pets for owner
    owner_pets = pet_repo.get_pets_by_owner(owner.owner_id)
    print(f"All pets for {owner.name}: {', '.join(pet.name for pet in owner_pets)}")
    
    # Get high-priority tasks for a pet
    max_high_priority = task_repo.get_tasks_by_priority(dog.pet_id, min_priority=4)
    print(f"High-priority tasks for {dog.name}: {', '.join(t.title for t in max_high_priority)}")
    
    # Get all tasks by category
    exercise_tasks = task_repo.get_tasks_by_category("exercise")
    print(f"All exercise tasks: {', '.join(t.title for t in exercise_tasks)}")
    
    # Get required tasks
    required_tasks = task_repo.get_required_tasks(dog.pet_id)
    print(f"Required tasks for {dog.name}: {', '.join(t.title for t in required_tasks)}")

    # ===== New Sorting + Filtering Demo =====
    print("\n🧪 SORTING + FILTERING DEMO:\n")

    # Intentionally unsorted list by time.
    dog_tasks_unsorted = task_repo.get_tasks_by_pet(dog.pet_id)
    print(f"Unsorted tasks for {dog.name} (in insertion order):")
    for t in dog_tasks_unsorted:
        print(f"  • {t.title} @ {t.time or 'No time'} | Required={t.is_required} | Priority={t.priority}")

    print(f"\nSorted tasks for {dog.name} (required -> time -> priority):")
    dog_tasks_sorted = scheduler.rank_tasks(dog_tasks_unsorted)
    for t in dog_tasks_sorted:
        print(f"  • {t.title} @ {t.time or 'No time'} | Required={t.is_required} | Priority={t.priority}")

    print("\nFiltered tasks by pet name 'Max':")
    max_tasks = task_repo.get_tasks_by_pet_name("Max", pet_repo)
    for t in max_tasks:
        print(f"  • {t.title} ({t.category}) @ {t.time or 'No time'}")
    
    print("\n✅ Demo complete!\n")


if __name__ == "__main__":
    main()
