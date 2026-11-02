**WEEK 11  ·  MODULE 6  ·  PRODUCTION & CAPSTONE**

**Production — Observability, Cost & the Failure → Test Loop**

**Build Week**

*Make your app watch itself: find any bad answer, control its cost, and stop mistakes coming back.*

---
# **At a glance**
---

| **Module** | Week 11 · Module 6 — Production & Capstone |
| :--- | :--- |
| **Format** | Build week — hands-on, one deliverable |
| **Deliverable** | Per-request logging, a completed support drill, a measured cost-per-request improvement, and one failure turned into a test |
| **Mentor review** | Friday — informal, no marks |
| **Evaluated** | Week 12 · Monday |
# **What this week is about**
---In production nobody is watching your app — so it has to watch itself. This week you make it observable (you can see what it did), affordable (you know and control the cost), and self-improving (every real failure becomes a permanent test). This is what turns a demo into something you can actually run.
# **Why it matters**
---

| **Why is logging such a big deal?**When a customer says “it gave a wrong answer yesterday,” your only hope of finding it is a good log. If it isn’t logged, it didn’t happen. | **How do I stop costs from surprising me?**Measure cost per request first, then use tricks like caching and picking a cheaper model for easy questions. You can’t cut a cost you haven’t measured. | **What is the “failure-to-test loop”?**Every real production failure becomes a new test case, so the same mistake can never quietly come back. The app improves while you sleep. |
| --- | --- | --- |
# **What you’ll learn**
---- What to record for every request, so you can always find and replay it

- Seeing each step’s time and cost, not just one lump

- The support drill: finding one bad answer among thousands from a vague complaint

- Measuring cost per request, and cutting it with caching and smart model choice

- Planning for 10x the traffic — what breaks first, and your plan for it

- Turning a real production failure into a permanent test so it can’t return
# **Topics covered**
---*The exact concepts to study.*

| •  What to log per request | •  Traces & spans |
| :--- | :--- |
| •  LangSmith / Phoenix / OpenTelemetry | •  The support drill |
| •  Cost per query | •  Prompt caching |
| •  Semantic caching | •  Model routing (LiteLLM) |
| •  Fallbacks & rate limits | •  The data flywheel |
| •  The 10× plan | •  Fine-tuning (last resort) |
# **Your task this week**
---**Evaluated: Week 12 · Monday**

Add proper logging to your app so you can find any past answer, then practise finding a planted bad answer from a vague complaint. Measure your cost per request, make one improvement, and turn one real failure into a permanent test.
## **Assigned tracks**


| **Track** | **Topic** | **Deliverable** |
| :---: | :--- | :--- |
| **A** | Customer support tickets | Find the refund answer nobody logged a trace id for |
| **B** | Recipes & food | Find the dairy-free swap that wasn’t |
| **C** | HR policy | Find the wrong notice period in the logs |
| **D** | Insurance claims | Find the coverage answer that ignored an exclusion |
| **E** | Developer documentation | Find the code sample that used a deprecated method |
| **F** | Legal contracts | Find the answer that cited the wrong termination clause |
*Same task, six different topics — so everyone works on their own version. Download whichever you are assigned.*
# **How your mentor checks**
---**Friday · no marks**

A quick review of your task. Not a test — just a few things your mentor looks at, so you can fix anything before Monday.

- Can they find a specific past answer from the logs quickly?

- Do the logs show time and cost per step, not just one total?

- Did they measure cost per request and improve it?

- Did they turn a real failure into a test that now guards against it?
