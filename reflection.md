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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
