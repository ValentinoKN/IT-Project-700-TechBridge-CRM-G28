# Group 28 Phase 3 tasks and application plan

Prepared 1 October 2026 for Valentino and the group.

## What we are building

We are keeping the TechBridge MSP CRM as a small local web application. It should do the work promised in the submitted proposal and Planning Phase:

1. Staff log in as Administrator, Manager or Representative.
2. Add a company, then a contact under that company.
3. Capture a lead and update its status.
4. Convert the lead into a deal and update the deal stage and value.
5. Record a call, email, meeting or note against a contact or deal.
6. Search records, check the dashboard and export the permitted filtered lists.

The local source is a prototype, not a completed or tested Phase 5 application. Docker was not available in the current execution session, and the application was not started. No source code was changed for this plan.

We will keep the Python, Django, PostgreSQL and Docker approach from the submissions. The first version does not need payments, live email, a customer portal or outside services.

## Phase order

| Phase | Due date | What needs to be ready |
| --- | --- | --- |
| Phase 3 Analysis | 9 October 2026 | Current process, information-gathering basis, data rules, weaknesses, requirements and proposed data model. |
| Phase 4 System Design | 30 October 2026 | Architecture, physical and database design, pseudocode, screens and security/backup design matching the intended application. |
| Phase 5 Implementation | 9 November 2026 | Working code, testing, system test cases and evaluation, installation instructions and actual evidence. |

The iterative approach in our proposal allows an early prototype to inform the analysis and design. Having code early does not mean the implementation phase is finished. Requirements and design decisions still need checking, then implementation and testing must prove the final behaviour.

The guidelines allocate 50% of the overall project to documentation and 50% to individual presentation. Everyone needs to understand the application and their contribution.

## Tasks to give the group now

These are proposed assignments based on the responsibilities in the submitted Phase 2 document. They are not a claim that the work has already happened.

| Member | Phase 3 task | What to bring back |
| --- | --- | --- |
| Valentino Naidoo | Keep one agreed copy, compare requirements with the submissions and organise a short review meeting. Check the installation prerequisites on this PC. | A requirements checklist, actual meeting notes and a list of tools installed or still needed. |
| Rene Louw | Read FR-01 to FR-12 and NFR-01 to NFR-08. Check that the wording is clear and the acceptance checks can be demonstrated. | Suggested corrections and at least three examples of invalid form input with the expected response. |
| Tokelo Mashiane | Check Company and Contact fields, the data dictionary and relationships against the local models. Review the proposed Role-table simplification. | Annotated ERD/data dictionary and fictional example company/contact records. |
| Logan Carolus | Walk through the lead/deal process on paper. Check the status lists, conversion and open pipeline calculation. | One normal workflow and examples for repeated conversion, a lost lead and a won/lost deal. |
| Yache Perumal | Review who can open, change and export each record type. Check the rule that an Activity links to exactly one Contact or Deal. | A role-access checklist and examples for valid/invalid Activity links. |
| Ryan Barnabas | Review the setup instructions as someone using a different PC. Prepare test cases for login, records, search, conversion and exports. | A setup checklist and test-case sheet. Record actual results only when the app is run. |

Suggested internal target: return notes by 6 October, review the document together on 7 October and make corrections on 8 October. The Moodle deadline is 9 October; check Moodle for the actual cutoff time.

## A useful group walkthrough

Use fictional records. One member acts as a Representative, another as Manager and another as Administrator. Walk through an enquiry, decide what must be saved, and check what each role should see. If the app is not running yet, do this on paper; describe it as a paper walkthrough, not an application test.

Record the real date, who attended, questions raised, decisions and changes required. This gives us actual participatory evidence for section 3.2. If it is completed before submission, revise that section to describe what happened and what was learned. Until then, the document correctly describes desk-based analysis without completed interviews or walkthroughs.

## Keep the code understandable

Use ordinary Python indentation, short functions, descriptive names and simple Django forms/views. Keep shared permission rules in one understandable place. Comments should explain a decision or a business rule rather than repeat each line of code.

Example comment style:

```python
# Reps only get the records assigned to them.
# Keep the lead so we can still see where the deal started.
# Leave this blank if we do not know the close date yet.
```

Each person should edit and explain their own allocated part. Deliberately odd spacing, unnecessary mistakes or misleading comments would make the application harder to maintain. Plain comments can match our wording while the code stays readable.

## Required implementation checks

Before the application is accepted as complete, finish and test the gaps already noted in Phase 3:

- Apply the active search term to CSV exports as well as role restrictions.
- Include the activity count promised by the Planning Phase and define what “recent” means consistently in Phase 4.
- Make lead conversion atomic, prevent repeated/simultaneous duplicate conversion and stop manual Converted status from bypassing creation of a deal.
- Add the agreed company duplicate checks, non-negative deal values and database-level Activity constraint.
- Check administration permissions, related-record dropdowns and direct URLs for every role.
- Decide and document safe administrative deletion behaviour so linked history is not removed unexpectedly.
- Run automated and manual tests and record failures, corrections and the final actual results.

These are requirements to complete, not completed test results. Keep the original backup unchanged and use a separate working copy when development starts.

## Installation approach for Phase 5

Section 5.5 of the supplied guidelines asks for software application installation. It does not specify a Windows executable installer. The submitted project is already a browser-based Django application using Docker.

The planned installation pack can contain the project folder, Docker configuration, requirements, a README and a small Windows start/stop launcher. The existing GitHub repository can be used for group collaboration, and a ZIP can be supplied for installation handover. The ZIP is a delivery package, not a substitute for documenting installation.

The user installs Docker Desktop and its required Windows/WSL support first. The launcher then checks that Docker is available/running, starts the Django application and PostgreSQL with Docker Compose, and gives the browser address. Startup applies database migrations and creates demo accounts without overwriting existing CRM records. The first setup will normally need internet access to obtain container images and dependencies.

The start launcher is not a standalone application installer and will not silently install Docker. A normal stop action must preserve the database. A destructive reset must remain a separate clearly labelled action. Installation tests should cover a clean setup on another PC, login, adding a record, stopping/restarting and checking that the record remains.

No launcher or installer has been built yet. This is the intended Phase 5 delivery approach. If the lecturer later specifies a different packaging format, update the plan before building it.

## Keeping the documents and application aligned

Phase 3 already explains the six-entity model refinements and prototype gaps. Phase 4 must turn them into a specific design, including owner relationships, constraints, conversion pseudocode, dashboard definitions and installation/security arrangements.

Suggested wording for a simple interface decision:

> We are keeping the first version as a local web application with simple forms and list pages. This makes it easier for the group to build, test and explain. The customer, lead, deal and activity features from the earlier submissions remain in scope.

Do not describe a required feature as removed just because it has not been built yet. For any real scope change, record the earlier requirement, the new decision, the reason and the affected document sections/test cases. A change to PostgreSQL, user roles or filtered export would need explicit documentation rather than silently changing the application.

The aim is a working, explainable application that meets the assessment requirements. A pass or particular mark cannot be guaranteed without the lecturer's evaluation.
