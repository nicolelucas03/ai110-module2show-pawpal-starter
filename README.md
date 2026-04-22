# PawPal+

A Python + Streamlit scheduling assistant that helps pet owners plan daily care tasks with clear priorities, time constraints, and explainable scheduling decisions.

PawPal+ was built as an object-oriented software design project with a focus on clean domain modeling, testable scheduling logic, and an interactive UI.

## Why This Project Matters

Pet care is full of recurring responsibilities (walks, feeding, medication, enrichment), but real life imposes time limits. PawPal+ turns that complexity into a structured daily plan by combining:

- Task priority and required vs optional status
- Preferred task times (when provided)
- Daily time constraints
- Conflict detection and human-readable scheduling explanations

## Core Features

- Owner and pet profile modeling
- Task creation with:
	- Category
	- Duration
	- Priority (1-5)
	- Required/optional status
	- Optional preferred time
	- Optional recurrence (daily/weekly)
- Intelligent task ranking based on:
	- Required tasks first
	- Earlier requested times first
	- Higher priority next
- Daily plan generation with remaining-time tracking
- Scheduling explanation output for transparency
- Time-overlap conflict detection
- Recurrence logic that generates the next task instance when a recurring task is completed
- Repository pattern for pets and tasks
- Automated test coverage with pytest

## Tech Stack

- Python 3
- Streamlit (UI)
- pytest (unit testing)
- Dataclasses + type hints (domain model)

## Project Structure

ai110-module2show-pawpal-starter/
- app.py                # Streamlit application
- main.py               # CLI demo script showcasing system behavior
- pawpal_system.py      # Domain models, repositories, and scheduling engine
- tests/
	- test_pawpal.py      # Unit tests for ranking, recurrence, conflicts, and core behavior
- requirements.txt

## Architecture Overview

The system is organized into three layers:

- Domain models:
	- Owner
	- Pet
	- CareTask
	- DailyConstraints
	- ScheduleItem
	- DailyPlan
- Service layer:
	- Scheduler (ranking, plan building, explanations, conflict handling, recurrence completion)
- Data access layer:
	- TaskRepository
	- PetRepository

This separation keeps business logic independent from UI code and makes core behavior easier to test.

## Getting Started

### 1. Clone and enter the project

git clone <your-repo-url>
cd ai110-module2show-pawpal-starter

### 2. Create and activate a virtual environment

Windows (PowerShell):

python -m venv .venv
.venv\Scripts\Activate.ps1

macOS/Linux:

python -m venv .venv
source .venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

## Run the App

Launch the Streamlit interface:

streamlit run app.py

Then open the local URL shown in your terminal (typically http://localhost:8501).

## Run the Demo Script

To see a console-based walkthrough of owners, pets, tasks, ranking, and schedule generation:

python main.py

## Run Tests

pytest -q

Current tests validate key behaviors such as:

- Task completion state changes
- Ranking order correctness
- Case-insensitive task filtering by pet name
- Conflict detection and safe warning behavior
- Recurring task rollover (daily)

## Example User Flow in the UI

1. Create or update an owner with daily available minutes.
2. Add a pet profile.
3. Add one or more care tasks.
4. Generate a schedule.
5. Review schedule reasoning and any conflict warnings.

## Engineering Highlights

- Prioritized explainable scheduling over opaque automation
- Applied object-oriented design with clear responsibilities
- Added robust input validation (priority bounds, duration, time format, recurrence values)
- Protected scheduling operations with overlap and capacity checks
- Built tests around practical edge cases and safety behavior

## Future Improvements

- Multi-pet unified schedule optimization
- User-defined blocked time windows in scheduling algorithm
- Persistent storage (SQLite/PostgreSQL)
- Calendar export (ICS/Google Calendar)
- Notification and reminder integrations
- Advanced heuristics for fairness and workload balancing

## Portfolio Context

This project demonstrates end-to-end software development workflow:

- Requirements translation into domain design
- Incremental implementation of scheduling logic
- Automated testing of critical behaviors
- Delivery through an interactive Streamlit interface

If you are reviewing this for hiring or collaboration, the most representative files are:

- pawpal_system.py (core architecture + business logic)
- tests/test_pawpal.py (behavioral test coverage)
- app.py (product-facing UI integration)
