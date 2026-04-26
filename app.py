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
    st.session_state.selected_pet_id = None

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
        new_pet_id = f"pet_{len(st.session_state.pet_repo.get_all_pets()) + 1:03d}"
        pet = Pet(
            pet_id=new_pet_id,
            owner_id=st.session_state.owner.owner_id,
            name=pet_name,
            species=species,
            age_years=int(age),
        )
        st.session_state.pet_repo.add_pet(pet)
        st.session_state.selected_pet_id = new_pet_id
        st.success(f"✅ Pet '{pet_name}' added!")

    # Show all pets currently registered
    all_pets = st.session_state.pet_repo.get_all_pets()
    if all_pets:
        st.markdown("**Registered pets:**")
        st.table(
            [
                {
                    "Name": p.name,
                    "Species": p.species,
                    "Age": f"{p.age_years} yrs",
                    "Pet ID": p.pet_id,
                }
                for p in all_pets
            ]
        )
else:
    st.info("👈 Create an owner first!")

# ===== SELECT ACTIVE PET =====
st.divider()
all_pets = st.session_state.pet_repo.get_all_pets()

if st.session_state.owner and all_pets:
    st.subheader("Select Active Pet")
    pet_options = {p.pet_id: f"{p.name} ({p.species}, {p.age_years} yrs)" for p in all_pets}
    pet_ids = list(pet_options.keys())

    # Default to the last-added pet if selected_pet_id is unset or stale
    if st.session_state.selected_pet_id not in pet_ids:
        st.session_state.selected_pet_id = pet_ids[-1]

    selected_id = st.selectbox(
        "Which pet do you want to add tasks to / schedule for?",
        options=pet_ids,
        format_func=lambda pid: pet_options[pid],
        index=pet_ids.index(st.session_state.selected_pet_id),
        key="pet_selector",
    )
    st.session_state.selected_pet_id = selected_id
    active_pet = st.session_state.pet_repo.get_pet_by_id(selected_id)
else:
    active_pet = None

# ===== ADD TASKS =====
st.divider()
st.subheader("Add Care Tasks")

if st.session_state.owner and active_pet:
    st.caption(f"Adding tasks for: **{active_pet.name}**")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30, key="duration_input")
    with col3:
        category = st.selectbox(
            "Category",
            ["exercise", "feeding", "grooming", "play", "care", "health", "other"],
            key="category_select",
        )
    with col4:
        priority = st.selectbox(
            "Priority",
            [1, 2, 3, 4, 5],
            format_func=lambda x: f"{x} - {['Low', 'Medium', 'High', 'Critical', 'Critical'][x-1]}",
            key="priority_select",
        )
    preferred_time = st.time_input(
        "Preferred time",
        value=datetime.strptime("08:00", "%H:%M").time(),
        key="preferred_time_input",
    )

    is_required = st.checkbox("Required task?", value=False, key="required_checkbox")

    if st.button("Add Task", key="add_task_btn"):
        task = CareTask(
            task_id=f"task_{len(st.session_state.task_repo.get_all_tasks()) + 1:03d}",
            pet_id=active_pet.pet_id,
            title=task_title,
            category=category,
            duration_min=int(duration),
            priority=int(priority),
            is_required=bool(is_required),
            time=preferred_time.strftime("%H:%M"),
        )
        st.session_state.task_repo.add_task(task)
        active_pet.add_task(task)
        st.success(f"✅ Task '{task_title}' added to {active_pet.name}!")
else:
    st.info("👈 Create an owner and add at least one pet first!")

# ===== ALL PETS TASKS =====
st.divider()
st.subheader("All Pets — Tasks Overview")

all_pets = st.session_state.pet_repo.get_all_pets()
if all_pets and st.session_state.owner:
    for pet in all_pets:
        pet_tasks = st.session_state.task_repo.get_tasks_by_pet(pet.pet_id)
        with st.expander(f"🐾 {pet.name} ({pet.species}) — {len(pet_tasks)} task(s)", expanded=True):
            if not pet_tasks:
                st.write("No tasks yet.")
            else:
                sorted_tasks = st.session_state.scheduler.rank_tasks(pet_tasks)
                st.table(
                    [
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
                )
else:
    st.info("👈 Create an owner and add pets to see tasks here.")

# ===== GENERATE SCHEDULE =====
st.divider()
st.subheader("Generate Daily Schedule")

if active_pet:
    active_pet_tasks = st.session_state.task_repo.get_tasks_by_pet(active_pet.pet_id)

if st.session_state.owner and active_pet and active_pet_tasks:
    st.caption(f"Generating schedule for: **{active_pet.name}**")
    if st.button("Generate Schedule", key="generate_schedule_btn"):
        today = datetime.now().strftime("%Y-%m-%d")
        constraints = DailyConstraints(
            date=today,
            available_time_min=st.session_state.owner.daily_time_available_min,
        )

        tasks = st.session_state.task_repo.get_tasks_by_pet(active_pet.pet_id)
        ranked_tasks = st.session_state.scheduler.rank_tasks(tasks)

        # Pre-schedule conflict warnings based on requested task times
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
            active_pet.pet_id,
        )

        if pre_warnings:
            for warning in pre_warnings:
                st.warning(warning)
        else:
            st.success("No duplicate-time conflicts detected in requested task times.")

        plan = st.session_state.scheduler.build_plan(
            owner=st.session_state.owner,
            pet=active_pet,
            tasks=ranked_tasks,
            constraints=constraints,
        )

        st.markdown(plan.summarize_plan())

        st.markdown("### Scheduling Reasoning")
        explanations = st.session_state.scheduler.explain_choices(plan)
        for explanation in explanations:
            st.write(f"• {explanation}")

        schedule_warnings = st.session_state.scheduler.detect_conflicts(
            plan.schedule_items,
            active_pet.pet_id,
        )
        if schedule_warnings:
            for warning in schedule_warnings:
                st.warning(warning)
        else:
            st.success("Final schedule has no time overlaps for this pet.")
else:
    st.info("👈 Select a pet with at least one task to generate a schedule.")

# ===== GENERATE COMBINED SCHEDULE (ALL PETS) =====
st.divider()
st.subheader("Generate Combined Daily Schedule (All Pets)")

all_pets_for_combined = st.session_state.pet_repo.get_all_pets()
all_tasks_for_combined = []
if all_pets_for_combined:
    for p in all_pets_for_combined:
        all_tasks_for_combined.extend(st.session_state.task_repo.get_tasks_by_pet(p.pet_id))

if st.session_state.owner and len(all_pets_for_combined) > 0 and len(all_tasks_for_combined) > 0:
    pet_lookup = {p.pet_id: p.name for p in all_pets_for_combined}
    st.caption(
        f"Scheduling tasks across **{len(all_pets_for_combined)} pet(s)** — "
        f"{len(all_tasks_for_combined)} total task(s) — "
        f"{st.session_state.owner.daily_time_available_min} min available"
    )

    if st.button("Generate Combined Schedule", key="generate_combined_btn"):
        today = datetime.now().strftime("%Y-%m-%d")
        available_min = st.session_state.owner.daily_time_available_min

        ranked_all = st.session_state.scheduler.rank_tasks(all_tasks_for_combined)

        current_time = datetime.strptime(f"{today} 08:00", "%Y-%m-%d %H:%M")
        combined_items = []
        skipped_tasks = []
        total_used = 0

        for task in ranked_all:
            remaining = available_min - total_used
            if task.duration_min <= remaining:
                end_time = current_time + timedelta(minutes=task.duration_min)
                combined_items.append(
                    ScheduleItem(
                        task_id=task.task_id,
                        task=task,
                        start_time=current_time,
                        end_time=end_time,
                    )
                )
                total_used += task.duration_min
                current_time = end_time
            else:
                skipped_tasks.append(task)

        # Summary header
        total_remaining = available_min - total_used
        st.markdown(
            f"**📅 Combined Daily Plan — {today}**  \n"
            f"⏰ Available: {available_min} min | "
            f"✓ Scheduled: {total_used} min | "
            f"Remaining: {total_remaining} min"
        )

        if combined_items:
            st.markdown("#### Schedule")
            st.table(
                [
                    {
                        "Time": f"{item.start_time.strftime('%H:%M')} – {item.end_time.strftime('%H:%M')}",
                        "Pet": pet_lookup.get(item.task.pet_id, item.task.pet_id),
                        "Task": item.task.title,
                        "Duration": f"{item.task.duration_min}min",
                        "Priority": item.task.priority,
                        "Required": "Yes" if item.task.is_required else "No",
                        "Category": item.task.category,
                    }
                    for item in combined_items
                ]
            )
        else:
            st.warning("No tasks could be scheduled within the available time.")

        if skipped_tasks:
            st.markdown("#### Tasks that did not fit")
            for t in skipped_tasks:
                pet_name = pet_lookup.get(t.pet_id, t.pet_id)
                label = "⚠️ Required" if t.is_required else "Skipped"
                st.write(f"• {label}: **{t.title}** ({pet_name}, {t.duration_min}min)")
        else:
            st.success("All tasks fit within the available time.")
else:
    st.info("👈 Add at least one pet with tasks to generate a combined schedule.")
