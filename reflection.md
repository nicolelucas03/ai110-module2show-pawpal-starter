# PawPal+ Project Reflection

## 1. System Design

### Core Actions 
1. User should track walks, feedings, meds, and enrichment. 
2. User should be able to produce a daily plan. 
3. User should enter fields such as owner and pet information.
4. User can edit and add tasks. 

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial design was quite simple. Included objects such as Pet, Owner, Schedule, and Task. The Pet class included attributes such as name, species, and age. The Owner class included name, time availability, and preferences. Schedule included methods such as calculateDuration() and isCompleted() and attributes such as start_time and end_time. Task included methods such as addTask, updateTask,  and deleteTask. 


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

After consulting and brainstorming with Copilot, I realized that my classes were a bit vague and I needed to rename some classes for multi-use purposes. There were also some missing relationships, such as Pet class storing owner_id, CareTask storing pet_id, and ScheduleItem storing CareTask reference. ScheduleItem was changed to use objects instead of strings for start_time and end_time variables. Overall, the improvements suggested were to make my classes more descriptive and robust.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler currently considers several practical constraints:

1. Daily available minutes from the owner (`available_time_min`).
2. Task duration (`duration_min`) so tasks only fit when enough time remains.
3. Required vs optional tasks (`is_required`) so required care is scheduled first.
4. Priority score (`priority`) to rank tasks with the same required status.
5. Preferred clock time (`time` in `HH:MM`) to sort tasks earlier vs later.
6. Time overlap detection for the same pet, which returns warnings and skips conflicting adds.

I decided these constraints mattered most by focusing on pet health and realism. Required tasks and high-priority health/safety tasks should never be treated the same as optional enrichment when time is limited. After that, ordering by explicit time makes the plan easier to follow in real life. Conflict warnings are important because users need feedback without the app crashing or acting out. 

**b. Tradeoffs**

One tradeoff is that the scheduler uses a simple greedy strategy: it ranks tasks, then schedules in order until time runs out, instead of searching for a globally optimal schedule. This is reasonable for this scenario because pet owners need understandable behavior more than mathematical optimality. The greedy approach is easy to explain and good enough for day-to-day planning. It also keeps the system maintainable while still protecting core outcomes. 


---

## 3. AI Collaboration

**a. How you used AI**

I used AI to design and implement some logic throughout the project. Early on, I used it for brainstorming class design and responsibilities so my model could better represent real relationships between owner, pet, task, and schedule entities. During implementation, I used AI to help refactor methods, add recurrence logic, improve scheduling rules, and make the Streamlit app more user-friendly. I also used AI to generate focused tests for sorting, conflict detection, and recurring task behavior.

The most helpful prompts were specific and action-oriented. Prompts like "add a method to filter tasks by pet name," "sort tasks by HH:MM," and "create tests for recurrence and duplicate-time conflicts" produced testable changes. Requests that included expected behavior and concrete inputs/outputs gave the best results.

**b. Judgment and verification**

One moment I did not accept AI output was when I hit a runtime error in Streamlit (`NameError: ScheduleItem is not defined`). Instead of assuming all generated changes were correct, I reviewed the traceback, checked imports, and confirmed that `ScheduleItem` was referenced in the UI logic but missing from the import block. I then applied a minimal fix and re-validated the file.


---

## 4. Testing and Verification

**a. What you tested**

I tested core scheduling and data-management behaviors:

1. Task completion status updates (`pending` to `completed`).
2. Pet task management (adding tasks increases count).
3. Sorting correctness for required tasks and chronological HH:MM ordering.
4. Filtering tasks by pet name (including case-insensitive lookup and empty-name validation).
5. Recurrence logic (completing daily tasks creates a next occurrence).
6. Conflict detection and warning behavior for overlapping or duplicate-time tasks.
7. Non-crashing conflict handling when adding overlapping schedule items.

These tests were important because they cover both correctness and safety.

**b. Confidence**

I am moderately to highly confident that the scheduler works correctly for the implemented feature set. Core ranking, filtering, recurrence, and conflict-warning behavior are now covered by targeted tests and runtime checks. My Schedule format might not look like expected though. 

If I had more time, I would add edge-case tests for:

1. Weekly recurrence date rollover across months/year boundaries.
2. Tasks with invalid or missing time formats in mixed datasets.
3. Multiple pets with same name under one owner.

---

## 5. Reflection

**a. What went well**

The part I am most satisfied with is how the system evolved from a simple class sketch into a more robust scheduler with realistic constraints. I am especially happy with the improvements to data relationships, conflict handling, and test coverage, because those changes made the app both more useful and more reliable.

**b. What you would improve**

In another iteration, I would redesign scheduling to support more advanced optimization and richer constraints (for example, blocked windows, travel/buffer times, and personalized preference weighting). I would also improve persistence so recurring tasks and schedule history are stored across sessions, and I would expand UI controls for editing/reordering tasks directly in Streamlit.

**c. Key takeaway**

My key takeaway is that good system design is iterative. Clear models, explicit constraints, and small testable changes matter more than trying to get everything perfect on the first pass. I also learned that AI is most valuable when used with precise prompts and active verification, and not as a replacement for engineering judgment. AI may not always be right, but with the right context, I can get closer to the right direction. 
