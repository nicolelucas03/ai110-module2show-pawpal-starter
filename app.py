import streamlit as st
from datetime import datetime, timedelta

from pawpal_system import (
    Owner,
    Pet,
    CareTask,
    ScheduleItem,
    DailyConstraints,
    Scheduler,
    TaskRepository,
    PetRepository,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Initialize session state repositories and objects
if "pet_repo" not in st.session_state:
    st.session_state.pet_repo = PetRepository()
    st.session_state.task_repo = TaskRepository()
    st.session_state.scheduler = Scheduler()
    st.session_state.owner = None
    st.session_state.current_pet = None

# ===== CREATE OWNER =====
st.subheader("Owner Information")
owner_name = st.text_input("Owner name", value="Jordan", key="owner_name_input")
daily_time_available = st.number_input(
    "Available time daily (minutes)", min_value=30, max_value=480, value=120
)

if st.button("Create/Update Owner", key="create_owner_btn"):
    st.session_state.owner = Owner(
        owner_id="owner_001",
        name=owner_name,
        daily_time_available_min=int(daily_time_available),
    )
    st.success(f"✅ Owner '{owner_name}' created with {daily_time_available} min/day available")

# ===== CREATE PET =====
st.divider()
st.subheader("Add a Pet")

if st.session_state.owner:
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
    species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"], key="species_select")
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    
    if st.button("Add Pet", key="add_pet_btn"):
        pet = Pet(
            pet_id=f"pet_{len(st.session_state.pet_repo.get_all_pets()) + 1:03d}",
            owner_id=st.session_state.owner.owner_id,
            name=pet_name,
            species=species,
            age_years=int(age),
        )
        st.session_state.pet_repo.add_pet(pet)
        st.session_state.current_pet = pet
        st.success(f"✅ Pet '{pet_name}' added!")
else:
    st.info("👈 Create an owner first!")

# ===== ADD TASKS =====
st.divider()
st.subheader("Add Care Tasks")

if st.session_state.owner and st.session_state.current_pet:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30, key="duration_input")
    with col3:
        category = st.selectbox(
            "Category",
            ["exercise", "feeding", "grooming", "play", "care", "health", "other"],
            key="category_select"
        )
    with col4:
        priority = st.selectbox("Priority", [1, 2, 3, 4, 5], format_func=lambda x: f"{x} - {['Low', 'Medium', 'High', 'Critical', 'Critical'][x-1]}", key="priority_select")
    preferred_time = st.time_input("Preferred time", value=datetime.strptime("08:00", "%H:%M").time(), key="preferred_time_input")
    
    is_required = st.checkbox("Required task?", value=False, key="required_checkbox")
    
    if st.button("Add Task", key="add_task_btn"):
        task = CareTask(
            task_id=f"task_{len(st.session_state.task_repo.get_all_tasks()) + 1:03d}",
            pet_id=st.session_state.current_pet.pet_id,
            title=task_title,
            category=category,
            duration_min=int(duration),
            priority=int(priority),
            is_required=bool(is_required),
            time=preferred_time.strftime("%H:%M"),
        )
        st.session_state.task_repo.add_task(task)
        st.session_state.current_pet.add_task(task)
        st.success(f"✅ Task '{task_title}' added!")
    
    # Display current pet's tasks
    if st.session_state.current_pet.task_count() > 0:
        st.markdown("### Current Tasks")
        unsorted_tasks = st.session_state.task_repo.get_tasks_by_pet(st.session_state.current_pet.pet_id)
        sorted_tasks = st.session_state.scheduler.rank_tasks(unsorted_tasks)

        st.success("Tasks ranked successfully by required status, time, and priority.")

        tasks_data = [
            {
                "Title": t.title,
                "Duration": f"{t.duration_min}min",
                "Time": t.time or "-",
                "Priority": t.priority,
                "Required": "Yes" if t.is_required else "No",
                "Category": t.category,
            }
            for t in sorted_tasks
        ]
        st.table(tasks_data)

        filtered_by_name = st.session_state.task_repo.get_tasks_by_pet_name(
            st.session_state.current_pet.name,
            st.session_state.pet_repo,
        )
        st.markdown("#### Filtered By Pet Name")
        st.table(
            [
                {
                    "Pet": st.session_state.current_pet.name,
                    "Task": t.title,
                    "Time": t.time or "-",
                    "Priority": t.priority,
                }
                for t in filtered_by_name
            ]
        )
else:
    st.info("👈 Create an owner and pet first!")

# ===== GENERATE SCHEDULE =====
st.divider()
st.subheader("Generate Daily Schedule")

if st.session_state.owner and st.session_state.current_pet and st.session_state.current_pet.task_count() > 0:
    if st.button("Generate Schedule", key="generate_schedule_btn"):
        # Create daily constraints
        today = datetime.now().strftime("%Y-%m-%d")
        constraints = DailyConstraints(
            date=today,
            available_time_min=st.session_state.owner.daily_time_available_min,
        )
        
        # Get tasks for current pet
        tasks = st.session_state.task_repo.get_tasks_by_pet(st.session_state.current_pet.pet_id)
        ranked_tasks = st.session_state.scheduler.rank_tasks(tasks)

        # Build pre-schedule conflict warnings based on requested task times.
        proposed_items = []
        for task in ranked_tasks:
            if task.time:
                start_time = datetime.strptime(f"{today} {task.time}", "%Y-%m-%d %H:%M")
                proposed_items.append(
                    ScheduleItem(
                        task_id=task.task_id,
                        task=task,
                        start_time=start_time,
                        end_time=start_time + timedelta(minutes=task.duration_min),
                    )
                )

        pre_warnings = st.session_state.scheduler.detect_conflicts(
            proposed_items,
            st.session_state.current_pet.pet_id,
        )

        if pre_warnings:
            for warning in pre_warnings:
                st.warning(warning)
        else:
            st.success("No duplicate-time conflicts detected in requested task times.")
        
        # Build the plan
        plan = st.session_state.scheduler.build_plan(
            owner=st.session_state.owner,
            pet=st.session_state.current_pet,
            tasks=ranked_tasks,
            constraints=constraints,
        )
        
        # Display the schedule
        st.markdown(plan.summarize_plan())
        
        # Display reasoning
        st.markdown("### Scheduling Reasoning")
        explanations = st.session_state.scheduler.explain_choices(plan)
        for explanation in explanations:
            st.write(f"• {explanation}")

        # Display post-schedule overlap warnings if any exist.
        schedule_warnings = st.session_state.scheduler.detect_conflicts(
            plan.schedule_items,
            st.session_state.current_pet.pet_id,
        )
        if schedule_warnings:
            for warning in schedule_warnings:
                st.warning(warning)
        else:
            st.success("Final schedule has no time overlaps for this pet.")
else:
    st.info("👈 Create an owner, pet, and at least one task first!")
