# FedEx Flow Parity Notes

## Current FedEx workflow traced

FedEx no longer uses one combined `Release QA` tab. The current QA flow is split into:

1. `User Story`
- requirement research first
- generate user story + AC
- Trello board-first card creation flow

2. `Move Cards`
- board-first bulk move flow

3. `🧾 Validate AC`
- load board/list/release
- inspect card requirements
- detect toggle prerequisites
- generate or review AI AC
- save/comment/skip/share AC
- run domain validation
- apply fixes and re-validate

4. `🧪 Generate TC`
- reuse loaded release context
- generate and review test cases
- regenerate with feedback
- publish test cases
- share TCs through Slack

5. `🤖 AI QA Verifier`
- run AI QA using generated test cases
- handle `qa_needed`
- review failed findings
- notify devs
- ask domain expert
- final approve and save

6. `⚙️ Generate Automation Script`
- write automation code
- bulk approve remaining cards when needed
- run automation and post results to Slack

7. `History`
- show approved pipeline runs

8. `Sign Off`
- compose sign-off from approved cards

9. `Handoff Docs`
- release handoff/support docs

## Current MCSL parity status

MCSL now matches the FedEx split-tab QA structure:

- `🧾 Validate AC`
- `🧪 Generate TC`
- `🤖 AI QA Verifier`
- `⚙️ Generate Automation Script`

And already includes these parity items:

- board-first Trello flow
- requirement-research-backed User Story flow
- AC action panel:
  - save to Trello description
  - post Trello comment
  - skip keep existing
  - Slack DM
  - Slack channel
- domain validation
- apply-fixes and re-validate
- TC generation/review/regenerate
- TC Slack DM/channel
- TC-first AI QA
- `qa_needed` rerun flow
- failed-finding selection and notify-dev path
- ask-domain-expert step
- final approval with sheet tab handling and duplicate review
- publish test cases
- write automation
- release-level run-tests and Slack post
- handoff docs tab

## MCSL-specific differences that are intentional

MCSL should not copy FedEx navigation.

Different by design:
- Shopify embedded app navigation
- multi-carrier domain model
- carrier-aware request/response expectations
- Shopify verification flows
- automation-backed MCSL setup and log handling

## Toggle parity status

MCSL toggle flow is now close to FedEx in orchestration:
- detect toggles
- notify Ashok
- poll replies
- escalate to dev
- unblock QA after confirmation

But there is one MCSL-specific next step still open:
- stop relying mainly on store name / store URL
- capture `storeUUID` and `accountUUID` from MCSL APIs
- capture `/toggles` API status to know if a toggle is already enabled

That is the main remaining toggle-flow enhancement.

## Remaining parity work

- keep polishing wording/layout where QA expects exact FedEx phrasing
- implement UUID-based toggle context for MCSL
- continue checking `Generate Automation Script` for any missed FedEx behavior
- continue real-card testing to patch any missing UI variant in AI QA execution
