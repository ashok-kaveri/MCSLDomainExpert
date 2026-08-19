# Booking & Appointment Plugin for WooCommerce 6.0.0 — Support Guide

Platform: WooCommerce (WordPress). Product: Booking & Appointment Plugin for WooCommerce. Version **6.0.0**, released **12 August 2026**. If a merchant does not see the behaviour described here, confirm their plugin version first.

Three themes run through the release: a new admin **Booking Edit** capability on the All Bookings page, with Screen Options and corrected counts alongside it; a rebuilt **Search Availability Widget** that now agrees with the real booking calendar; and **reminder and follow-up emails** moved onto one scheduled job per booking, with debug logging consolidated on the Diagnostics tab.

## Included Story Cards

| Story ID | Story Title | Trello card link |
|---|---|---|
| 920 | [New Feature] Implemented Booking Edit Feature for the All Bookings Page | [920](https://trello.com/c/VOIpkf9I) |
| 921 | [Improvement] Search Widget (SW) updates for normal booking product | [921](https://trello.com/c/0bIjRcrE) |
| 944 | [New Feature] Screen Options for the All Bookings Page | [944](https://trello.com/c/v0RjrOFw) |
| 929 | [Improvement] All Bookings page pagination count mismatch + improved load performance | [929](https://trello.com/c/s2LNE6LC) |
| 946 | [Improvement] Move Google Calendar Sync Debug Logging to the Diagnostics Tab | [946](https://trello.com/c/IwZR8qii) |
| 940 | [Improvement] Outlook Calendar Event Details Removal | [940](https://trello.com/c/LRkwzp4z) |
| 939 | [Improvement] Replace periodic scan crons with per-booking scheduled jobs for follow-up emails | [939](https://trello.com/c/EyAduFah) |
| 936 | [Improvement] Replace Periodic Reminder Email Scan Cron with Per-Booking Scheduled Jobs (Performance issue for Reminder Email) | [936](https://trello.com/c/GmamhiVR) |
| 924 | [Improvement] Fixed Duplicate Deposit Orders and Booking Status Issues | [924](https://trello.com/c/Hvmw7M1q) |

## 920 - [New Feature] Implemented Booking Edit Feature for the All Bookings Page

### Brief Description

Admins can now change an existing booking straight from the **All Bookings** list. A new **Edit** button opens a popup where the booking's dates and times, asset, participant counts, resources and notes can be changed — and every change is checked against exactly the same availability rules a customer has to satisfy when booking on the front end.

Before this release the only way to move a booking was the standard WooCommerce order edit screen, which wrote the new dates in without checking anything: it did not check the product's own availability, did not check whether the asset or resource was already taken, and did not enforce participant capacity. An admin could save an overbooked or unavailable booking without any warning. Booking Edit closes that gap — an invalid combination is refused with a specific reason before anything is saved, and nothing is part-saved when a check fails.

On a successful save the plugin also settles the payment position, re-syncs Google and Outlook calendars, writes an audit trail into the order notes, and always emails the customer the updated booking details.

### Prerequisites

- Plugin version 6.0.0 or later.
- The **Edit** button only appears once the **Manage / Actions** column is switched on from **Screen Options** on the All Bookings page. On a fresh update the column is hidden by default, so the button will look missing until it is enabled — see story 944.
- Access rule 1: **administrators can always edit bookings.** This never depends on the master setting or the roles list.
- Access rule 2: **every other role, including Shop Manager,** needs both of these — **Bookings → Settings → Advanced → Enable Booking Modification** switched on, **and** that role explicitly added to **Allow access to specific roles** on the same page. Having general WooCommerce management permission is no longer enough on its own.
- A non-administrator who opens the Advanced page sees the Booking Modification card in read-only mode with a short notice explaining why.
- Editing is not offered for these booking types: **Deposit, Non-adjustment, Recurring Deposit, and Product Add-on** bookings. Clicking Edit shows a "not supported for this booking type" message instead of the form.
- The Edit button is shown but disabled, with a tooltip giving the reason, when the booking has already started, the booking is Cancelled, or the order is Completed, Cancelled or Refunded.
- If the merchant wants to test with Editor, Author or Contributor roles, note that those roles cannot see the Bookings menu at all by default. They need WooCommerce management permission granted first (for example with the User Role Editor plugin) before the **Allow access to specific roles** setting has anything to act on. This is a WordPress menu-permission matter, separate from this feature's own roles list.

### Step-by-Step Support Walkthrough

**Setup — make the Edit button visible**

1. In WordPress Admin, go to **Bookings → Settings → Advanced** and switch on **Enable Booking Modification**. Add any non-administrator roles that should have access to **Allow access to specific roles**, then save.
2. Go to **Bookings → All Bookings**, open the **Screen Options** panel at the top right, tick the **Manage** column and save.
3. Confirm the **Manage** column now appears in the list with an **Edit** button on each row.

**Scenario A — a straightforward date change**

4. Pick a booking that has not started yet, on an order that is not Completed, Cancelled or Refunded, and click **Edit**.
5. Confirm the popup opens with **From**, **To**, **Status**, **Booking Status**, **Asset**, **Participants**, **Resources** and **Notes** filled in from the booking, and that the fields shown match how the product is configured — for example the Asset field only appears for products that use assets.
6. Move the booking to a different available slot and click **Update Booking**.
7. Confirm the change appears in **All Bookings**, on the **WooCommerce order** screen, on the customer's **My Account** page, in the product's and the asset's availability, and in the connected Google or Outlook calendar.
8. Confirm the slot the booking has left is released and can be booked again, and that the new slot now shows as taken.

**Scenario B — an edit that must be refused**

9. Open Edit on any booking and try to move it onto a date or time the product is not available for, or one already fully booked for that asset, or a participant count above the configured capacity, or a slot blocked by the product's buffer time.
10. Confirm the save is refused with a message naming the actual reason, and that reopening the booking shows the original details untouched — nothing is part-saved.
11. On a **Bookings Per Night** product, set From and To to the same date. Confirm this is refused because a stay must be at least one night; previously it was quietly accepted as one day.

**Scenario C — keeping the original price**

12. Open Edit on a booking and change something that would change the price.
13. Confirm price recalculation is **on by default**, and that the popup shows a payment summary and a **Customer Notification** dropdown.
14. Tick **Keep the original booking price** and confirm the payment summary and the notification dropdown disappear completely, not just grey out.
15. Save, and confirm the order total is unchanged and the customer still receives a Booking Updated email with the new booking details and no price or payment link in it.
16. Be clear with merchants on this point: **Keep the original booking price is a pricing control only.** It does not control whether the customer is emailed. The customer is always emailed on save; there is no separate "notify customer" option anymore.

**Scenario D — an edit that increases the price**

17. Take a fully paid booking and edit it so the new total is **higher** than what has been paid, leaving **Keep the original booking price** unticked.
18. With **Send Updated Booking Details + Payment Link** selected (the default), save and confirm the customer's email contains the updated details and a payment link, the order status moves to **Pending Payment**, the booking status moves to **Unpaid**, and a **Pay** button appears for the customer in **My Account**.
19. Have the customer pay through that link. Confirm only the outstanding balance is charged, the booking status becomes **Paid** and the order status becomes **Processing**.
20. Repeat with **Send Updated Booking (No Payment Link)** selected. Confirm the email carries the updated details with no payment link and no payment summary, but the order and booking statuses still update and the **Pay** button is still available in My Account so the customer can settle the balance.
21. On an order holding several bookings where only one was edited, confirm only that booking's Amount Paid and Balance Due change, the other bookings are untouched, and the Booking Updated email leaves out bookings that are fully paid and unchanged. The email includes a note that the payment link itself opens the full order summary.

**Scenario E — the two payment guards**

22. Edit a booking so the recalculated total lands exactly on the amount already paid. Confirm **Update Booking** is blocked with a message pointing the admin at **Keep the original booking price** — switching the notification dropdown does not clear it, because both options recalculate to the same unchanged figure.
23. Edit a fully paid booking so the recalculated total is **lower** than the amount paid, for example by removing a paid resource. Confirm **Update Booking** is disabled **and** **Keep the original booking price** is itself disabled and force-unticked, so it cannot be used to slip past the block. This is a hard block with no exceptions — a refund is never produced by an edit.

**Scenario F — statuses, confirmation and the audit trail**

24. On a fully paid booking, manually change the status to **Unpaid** and save. Confirm Amount Paid resets to zero, Balance Due becomes the current total, and the booking no longer shows as fully paid anywhere.
25. On a product using **Require Confirmation**, edit a booking sitting in Pending Confirmation with **Keep the original booking price** ticked, then confirm it. Confirm the original price holds until save, the price recalculates on save where applicable, and both the **Booking Confirmed** and **Booking Updated** emails go out once with the latest details.
26. Open the order and read the order notes for any edit made above.
    - Request/log fields to verify: the **order notes** on the edited order — price and payment changes and booking status changes are each recorded with their specific before/after detail, while changes to booking details such as date, time, asset or participants are recorded with the generic note `Booking details updated by admin`.
27. Confirm the popup and the list produce no on-screen errors when opening, saving or cancelling an edit.

### Expected Behaviour

An admin can move or adjust a booking from **All Bookings** and trust that anything the popup accepts is genuinely bookable — the same availability, buffer, duration, asset and participant-capacity rules that apply to a customer apply here, and they are re-checked on the server even if the screen lets a click through. A refused save changes nothing at all. A successful save updates the booking everywhere it is shown, recalculates the price unless the admin opts out, always emails the customer, and leaves a readable trail in the order notes. An edit can ask a customer for more money but can never produce a refund.

Two things to check first when a merchant says the feature is missing: whether the **Manage** column is enabled in **Screen Options**, and whether their role is covered by the access rules above. A hidden column is by far the more common cause.

**Known observation from testing:** when the admin leaves the **Notes** field empty in the popup, the notes section after the update can still show the note the customer originally added, rather than appearing empty. Treat a merchant report matching this as a known item and pass it back to the team rather than as a configuration problem.

## 921 - [Improvement] Search Widget (SW) updates for normal booking product

### Brief Description

The **Search Availability Widget** — the front-end search that lets a visitor look for bookable products by date, participants and asset — was working out availability with its own separate set of rules. Those rules did not match the real booking calendar on the product page, so a product could show up as available in search and then be refused at checkout, or be left out of the results when it was in fact bookable.

The widget now works out availability using the same engine the product page's own calendar uses, so results agree with the real calendar by design. Alongside that, the widget searches automatically as filters change, restores the chosen asset and participant count when a results page is reloaded or shared, and correctly converts times into the visitor's own timezone. The widget's two settings have also moved to their own card on the **Advanced** page.

### Prerequisites

- Plugin version 6.0.0 or later.
- The widget must be switched on at **Bookings → Settings → Advanced → Display Search Availability Widget**. The **Booking Availability View** setting sits with it on the same card.
- Both of those settings used to live under **Settings → Calendar Display**. They are the same settings with the same saved values — only the page they appear on has changed. Existing choices carry over automatically on update and are not reset to defaults, and the old location no longer shows these controls at all.
- These fixes apply to the **Search Availability Widget only**. The product page's own booking calendar is a separate path and its behaviour is unchanged.
- To see the timezone behaviour, the WordPress site timezone must be different from the visitor's own timezone.

### Step-by-Step Support Walkthrough

**Setup**

1. Go to **Bookings → Settings → Advanced** and confirm the **Search Availability Widget** card is present, with **Display Search Availability Widget** and **Booking Availability View** on it. Switch the widget on and choose a Booking Availability View.
2. Go to **Settings → Calendar Display** and confirm these two settings are no longer there, with no duplicate controls left behind.
3. On a site that was already using the widget before the update, confirm the previously saved on/off state and the previously chosen Booking Availability View both carried across to the Advanced page exactly as they were.

**Scenario A — searching happens on its own**

4. On the front end, open the page holding the search widget with only the **Fixed Date** filter configured. Choose a date and confirm the search runs without clicking **Search**.
5. Repeat with **From Date** and **To Date** configured. Confirm the search runs once both dates are chosen.
6. Repeat with **Date**, **Participants** and **Asset** all configured. Confirm the search runs once all the filters are set.
7. Confirm the manual **Search** button is still there and still works at all times.
8. Click a **Participants** or **Asset** dropdown twice and confirm it opens on the first click and closes on the second. Confirm the list scrolls when long and that the **Apply** button works.
9. Run a search, then reload the results page. Confirm the chosen **Asset** and **Participant Count** are still selected rather than reset.
10. Clear a booking with a redirect page configured, and confirm the visitor lands on the configured page — Home if Home is set, Shop if Shop is set.

**Scenario B — results now match the real calendar**

11. Take a day-based product sold in fixed 2-day blocks, and mark one day in the middle of a block unavailable. Search a range covering that block and confirm the product is left out of the results.
12. Search the same product over a range with no unavailable days and confirm it appears.
13. Understand how minimum and maximum duration is counted, because this is the most common source of confusion: **the minimum and maximum are a number of blocks, not a number of days, months or hours.** On a 2-day block product with a minimum of 1 block and a maximum of 4 blocks, the real allowed range is **2 to 8 days**, not 1 to 4 days. Search inside that range, for example 6 days, and confirm the product appears; search shorter than the minimum and longer than the maximum and confirm it is left out in both cases.
14. Repeat both of the above on a month-based product: a rule affecting a month inside a block leaves the product out, and a 2-month block product with a 1-to-2 block range allows 2 to 4 months.
15. On a time-based product with a fixed block size, search a duration that is a clean multiple of the block size and confirm the product appears; search a duration that is not a multiple and confirm it does not.
16. On a time-based product where the customer picks the duration, confirm same-day searches inside the block limits show the product and searches outside those limits do not.
17. With **Book Across Days** switched on, search a duration that crosses midnight and confirm the product appears with the same block count the real calendar would allow. With **Book Across Days** switched off, search a range spanning two calendar days and confirm the product is left out regardless of how few blocks it uses.

**Scenario C — opening and closing time boundaries**

18. Search with a start time **after** the product's closing time and confirm the product is left out, whether or not Book Across Days is on.
19. Search with a start time **exactly equal to** closing time and confirm the product is not excluded for that reason alone — the boundary counts as valid.
20. On a product closing at 23:00, search 23:00 to 23:05 the same day and confirm the product appears without needing to run into the next day.
21. With **Book Across Days** on and a **Buffer Before** set, for example 10 minutes, confirm a search whose end time falls before the real buffer-shifted first slot of that day leaves the product out.
22. Confirm the search's start and end must each land exactly on a real slot boundary — an end time equal to a slot's **start** time is refused, only an end matching a slot's actual **end** is accepted.
23. With buffers set before and after, search the product page's real maximum allowed range and confirm it shows available, then search one block beyond it and confirm it does not — matching the real calendar exactly.

**Scenario D — automatically assigned assets follow first-come order**

24. Set up a product with asset auto-assign, Asset 1 with capacity for one and no bookings yet, Asset 2 with capacity for two. Search with participants set to 2 and **no asset chosen**. Confirm the product is correctly shown as unavailable: Asset 1 alone cannot take two people, and Asset 2 is not considered until Asset 1 is used up.
25. Repeat the same search but explicitly choose **Asset 2** in the Asset filter. Confirm the product is still shown as unavailable — a customer cannot cherry-pick a later asset to jump the queue.
26. Book Asset 1 down to no remaining capacity, then repeat the search with and without Asset 2 chosen. Confirm the product now shows as available, and that **Book Now** puts Asset 2 in the cart.
27. Confirm on every one of these that the asset added to the cart by **Book Now** is the one the first-come rule allows, never an out-of-order asset the visitor happened to search with.

**Scenario E — participant labels, prices and timezones**

28. Set up a participant type whose label contains a **+** sign, or has extra spaces in it. Confirm the search no longer wrongly blocks a valid search, and that the label matches correctly all the way through: search results, the Book Now price, and the cart line item.
29. Book directly from a search result with participants, asset and resource costs configured. Confirm the cart price is the same as the product page would charge for exactly the same selection.
30. Book directly from a search result where the asset is auto-assigned. Confirm the asset and resource cost is included in the price rather than silently dropped, and that an auto-assign with no capacity left blocks add-to-cart instead of going through at a wrong price.
31. With the site timezone and the visitor timezone different, open the time picker. Confirm slots are shown in the visitor's local time, that daylight saving is handled, that slots which shift across a day boundary still appear on the right local day, and that choosing a converted slot searches the correct underlying time and returns matching results.

**Scenario F — no side effects elsewhere on the site**

32. Run a booking search, then browse unrelated pages: the shop page, an ordinary blog post, and a WooCommerce search that returns nothing found. Confirm all of them load normally.
    - Request/log fields to verify: the site error log at `wp-content/debug.log` — after a booking search and the page visits above, there must be no `WordPress database error` entries referring to `wp_term_relationships`.
33. Run an ordinary search and confirm the widget's own results are filtered exactly as before — only which query the filters attach to has changed.
34. On the shop page, run a search that matches exactly one product so WooCommerce sends the visitor straight to that product's page. Confirm the calendar or Direct Booking view on the destination page is filled in with the date and time that was searched, rather than left blank.

### Expected Behaviour

Search results and the product page's booking calendar now agree. A product shown as available in search can be booked, and a product left out of the results genuinely cannot take that request. Search runs by itself as filters change, the chosen asset and participant count survive a page reload, times display in the visitor's own timezone, and prices from **Book Now** match the product page for the same selection. Automatically assigned assets are always filled in order, first asset to capacity before the next, and a visitor cannot get around that by naming a later asset in the search.

If a merchant reports missing search results, check the minimum and maximum duration first — they are counted in blocks, and a 2-day block product with a 1-to-4 block setting genuinely refuses a 1-day search. If a merchant cannot find the widget settings after updating, they are on the **Advanced** page now, not under **Calendar Display**.

## 944 - [New Feature] Screen Options for the All Bookings Page

### Brief Description

The **All Bookings** admin list had a fixed set of columns and a fixed number of rows per page — every admin saw exactly the same thing with no way to hide the columns they never use. This release adds the standard WordPress **Screen Options** panel to the page, so each admin can choose which columns to show and how many bookings appear per page.

Column choices and the per-page count are saved for each WordPress user individually, so two admins on the same store can have completely different layouts. Bookings per page is capped at 200 to keep the page loading quickly.

### Prerequisites

- Plugin version 6.0.0 or later.
- The panel is opened from the **Screen Options** button at the top right of **Bookings → All Bookings**.
- Every existing column stays visible by default, so an existing store sees no change to the list after updating. The one exception is the new **Manage / Actions** column, which is hidden by default so nothing appears until an admin chooses to turn it on.
- The **Edit** button from the Booking Edit feature (story 920) lives in that Manage column, so it will look missing on a fresh update until the column is enabled here.

### Step-by-Step Support Walkthrough

**Scenario A — what an admin sees the first time**

1. Go to **Bookings → Settings → Advanced** and switch on **Enable Booking Modification**, so the Manage column is offered at all.
2. Go to **Bookings → All Bookings** and open **Screen Options**.
3. Confirm the **Manage** column is listed and is **unticked**, every other column — Order, Product, Booking Status, From, To, Asset, No of Participants, Booked by, iCal — is **ticked**, and **Items per page** shows **20**.
4. Confirm these defaults survive a plugin update: an existing store must not suddenly gain the Manage column on its own.

**Scenario B — changing rows per page**

5. Change **Items per page** from 20 to 40 and save.
6. Confirm the page reloads and shows up to 40 bookings per page.

**Scenario C — the 200 limit is enforced as you type**

7. In **Items per page**, type a value above 200, for example 201 or 400.
8. Confirm the field snaps straight back to **200** and a **Max limit is 200** message appears next to it — immediately, not silently corrected after saving.
9. Set the field at or near 200 and use the up-arrow spinner to push past it. Confirm the same clamp and the same message.
10. Save and reload, and confirm the stored value is 200.

**Scenario D — hiding a column and the Save button**

11. With the current options already saved, untick the **Participants** column and confirm the **Save** button becomes available.
12. Tick **Participants** again, back to its saved state, and confirm the **Save** button goes back to unavailable.
13. Untick a column, save, and reload the page. Confirm the column is still hidden.
14. Log in as a second admin and confirm their own column layout and per-page count are unaffected by the first admin's choices.
15. Open, change, save and reload Screen Options a few times over and confirm no on-screen errors appear at any point.

### Expected Behaviour

Each admin controls their own view of the All Bookings list — which columns appear and how many bookings show per page — and those choices persist across reloads and are not shared with other admins. Nothing about an existing store's list changes on update until an admin opts in, and the per-page value can never be pushed above 200 either from the keyboard or with the spinner.

## 929 - [Improvement] All Bookings page pagination count mismatch + improved load performance

### Brief Description

On the **All Bookings** list, filtering by date range, product, asset or status tab returned the correct rows but the wrong totals: the "N items" count and the page count kept showing the store's whole unfiltered total. A store with 5,360 bookings still read "5,360 items" on the **Paid** tab even when only 58 bookings matched it, which made the pagination misleading and, on a large store, made admins think a filter had not applied.

Both counts are now worked out from the filtered result set. The same change also removed a heavy database lookup that was running on every load of this page, so the list loads noticeably faster on stores with a large booking history.

### Prerequisites

- Plugin version 6.0.0 or later.
- Best confirmed on a store with more bookings than fit on one page, and with bookings spread across several statuses, products and assets.
- No setting to enable. The corrected counts apply to the All Bookings list straight away.

### Step-by-Step Support Walkthrough

**Scenario A — no filters applied**

1. Go to **Bookings → All Bookings** with no filters set.
2. Confirm the total booking count is correct, the number of pages matches that total, and the number of rows on a page matches the configured per-page value.

**Scenario B — each status tab**

3. Open each status tab in turn: **All**, **Paid**, **Un-paid**, **Requires Confirmation**, **Partially Paid**, and **Cancelled** where available.
4. For each one, confirm only bookings of that status are listed, the item count matches the number of bookings actually in that tab, and the page count is worked out from that filtered number rather than the store total.

**Scenario C — each individual filter**

5. Apply the **Product** filter. Confirm only that product's bookings are listed and both the item count and the page count match.
6. Apply a **Bookings Start Between** date range. Confirm only bookings starting inside that range are listed, with matching counts.
7. Apply a **Bookings End Between** date range. Confirm only bookings ending inside that range are listed, with matching counts.
8. Apply the **Asset** filter. Confirm only bookings on that asset are listed, with matching counts.
9. While checking the Asset filter, use a product whose asset label has been renamed from the default. Confirm the **Asset** column still shows its value correctly and is not left blank.

**Scenario D — filters combined**

10. Apply combinations: Status with Product, Status with a start date range, Status with an end date range, Status with Asset, Product with a date range, Product with Asset, and all four together.
11. For each combination, confirm only bookings matching **every** filter are listed, and that the item count and page count reflect just that set.
12. Add and remove filters and confirm the counts and page count update each time.

**Scenario E — moving between pages**

13. With a filter applied and more than one page of results, move forward and back through the pages.
14. Confirm the filtered count stays the same throughout and no bookings from outside the filter appear on later pages.

**Scenario F — load time on a large store**

15. On a store with a production-scale booking history, load the All Bookings page and compare against the previous release. Confirm the page loads at least as quickly as before, and that the status tabs and filters remain responsive.

### Expected Behaviour

The item count and the page count on All Bookings always describe the bookings actually matching the current filters — status tab, date range, product, asset, or any combination — and stay consistent while moving between pages. Renamed asset labels still display in the Asset column. On large stores the page loads faster than in the previous release, with no change to which bookings are listed.

## 946 - [Improvement] Move Google Calendar Sync Debug Logging to the Diagnostics Tab

### Brief Description

Google Calendar Sync used to keep its own **Debug log** checkbox on its own settings tab, separate from the debug options for reminder emails, follow-up emails and Outlook sync. That checkbox has moved onto the shared **Bookings → Settings → Diagnostics** tab, so every debug option now sits in one place.

The move also widened what gets recorded. Logging now covers an order being placed, a booking's status changing, an order created from a Google Calendar event that was imported into the store, and the cancel and update actions from two-way sync. What the sync itself does — connecting, pushing events out, pulling events in — is unchanged. Only where the switch lives and how much detail it captures have changed.

### Prerequisites

- Plugin version 6.0.0 or later.
- Google Calendar Sync must be enabled and connected under **Bookings → Settings → Google Calendar Sync** before the debug option can be used. When it is not, the row on Diagnostics is shown greyed out with a short message and a link back to that tab.
- Stores that already had the old **Debug log** checkbox switched on keep that behaviour: the setting is carried over automatically the first time the plugin loads after the update, with nothing to re-configure.

### Step-by-Step Support Walkthrough

1. Go to **Bookings → Settings → Google Calendar Sync** and confirm there is no **Debug log** checkbox anywhere on the tab any more.
2. Go to **Bookings → Settings → Diagnostics** and confirm a **Google Calendar Sync Debug Log** row is present alongside the Reminder, Follow-up and Outlook rows.
3. With Google Calendar Sync **not** enabled or connected, confirm the **Google Calendar Sync Debug Log** checkbox is greyed out and unusable, with a message telling the admin to enable Google Calendar Sync first and a working link to that tab.
4. Enable and connect Google Calendar Sync, return to **Diagnostics**, tick **Enable** under **Google Calendar Sync Debug Log**, click **Save changes**, then reload the page. Confirm the option is still ticked after the reload.
5. With the debug option on, place a test booking, or trigger a re-sync from an existing booking, then go to **WooCommerce → Status → Logs**.
    - Request/log fields to verify: a log file whose name begins `ph-bookings-google-calendar-` followed by the date, reachable both from that Logs screen and from the link on the Diagnostics tab. Opening it must show entries for the booking's sync, covering order placed, booking status changed, an order created from an imported Google Calendar event, and the two-way sync `Modify:cancel` and `Modify:update` actions.
6. Return to **Diagnostics**, untick **Enable** under **Google Calendar Sync Debug Log**, and save. Place another test booking.
7. Confirm no new entries are added to the log file for that second booking.
8. On a store that had the old checkbox switched on before updating, confirm logging is still active after the update without anyone re-enabling it.

### Expected Behaviour

All debug switches now live together on the Diagnostics tab, and the Google Calendar one is only usable when Google Calendar Sync is actually connected. Turning it on produces a dated log file covering the full sync lifecycle, reachable from the Diagnostics tab itself; turning it off stops new entries. Existing stores keep whatever they had switched on before.

When a merchant reports that Google Calendar Sync is misbehaving, this is the first thing to have them switch on — the log names the order and the action, which usually identifies the problem without further back-and-forth.

## 940 - [Improvement] Outlook Calendar Event Details Removal

### Brief Description

Outlook two-way sync used to rebuild an event's whole description from a template every time it pushed an update, throwing away anything the customer or the admin had typed into the event directly in Outlook. Because our own support guidance tells merchants to rename an event to make it sync, following that advice quietly wiped the event's description. This was reported by a customer.

The plugin now **merges** its own booking-details block into whatever description the event already has, so existing text is kept, and it uses the same format for events imported from Outlook and for bookings created normally through the store. It can also now read **Asset**, **Participant** and **Resource** choices out of an imported event's description and apply them to the booking it creates — previously only the product itself was recognised, from the event title. The Outlook debug switch has also moved to the shared **Diagnostics** tab.

### Prerequisites

- Plugin version 6.0.0 or later.
- An active Microsoft Outlook connection is required, set up under **Bookings → Settings → MS Outlook Sync**. This card cannot be exercised without a connected Outlook test account.
- Lines in an event description are read as `Label: Value` or `Label -> Value` — a colon or an arrow separator. For example `Asset: Room A`, `Adult: 2`, `Res 1: yes`. Only lines whose label matches an asset name, participant type or resource actually configured on that product are applied; everything else in the description is left exactly as written.
- **Important limitation:** events whose descriptions were already overwritten before this update are not restored. This change stops new text being lost; it does not recover text already gone.
- **Verification status:** this card had not been confirmed end to end against a live Outlook calendar in development, as it needs a connected Outlook account. Treat a merchant report here as worth checking closely rather than assuming it is covered.

### Step-by-Step Support Walkthrough

**Scenario A — existing description survives a sync**

1. In Outlook, create an event and type some description text of your own into it.
2. Rename the event so it matches a bookable product's name or ID, and let it sync.
3. Confirm a booking is created and the slot is blocked in the store.
4. Open the Outlook event again. Confirm the original text is still there, with the plugin's own **Booking Details** section added **below** it rather than in place of it.

**Scenario B — asset, participants and resources read from the event**

5. In Outlook, create an event whose description contains lines matching real configured values on the product, for example `Asset: Room A`, `Adult: 2`, `Res 1: yes`.
6. Let the event sync and open the resulting booking order in the store.
7. Confirm the asset, participant count and resource are applied to the booking exactly as a normal checkout would have produced them.
8. Confirm any other lines in the description that do not match a configured value are left untouched.

**Scenario C — repeated syncs do not stack up**

9. Take a booking created from an imported Outlook event that has already synced once.
10. Change the booking's dates or the customer's details in the store, and let it sync again.
11. Open the Outlook event and confirm there is exactly **one** Booking Details section, updated to the latest details — not several stacked copies.

**Scenario D — normal bookings still push their details**

12. Place an ordinary booking order through the website, not from an imported event.
13. Once the order is placed or paid, open the matching Outlook event.
14. Confirm the booking details are shown in the same format as in the scenarios above, with nothing missing.

**Scenario E — the Outlook debug switch**

15. With Outlook Calendar Sync enabled under **Bookings → Settings → MS Outlook Sync**, go to **Bookings → Settings → Diagnostics**.
    - Request/log fields to verify: an **MS Outlook Sync Debug Log** option must be present on the **Diagnostics** tab and no longer on the MS Outlook Sync tab, greyed out whenever Outlook sync itself is switched off, and any debug setting saved before the update must still be in effect.
16. Confirm switching Outlook sync off greys the option out, and switching it back on makes it usable again.

### Expected Behaviour

Syncing or renaming an Outlook event never deletes text already in its description — the plugin's booking details are added alongside it, in one section that updates in place on later syncs instead of duplicating. Asset, participant and resource values written into an imported event's description are applied to the booking when they match what the product is configured with. Bookings placed normally on the store push the same details in the same format. The Outlook debug switch sits with the others on the Diagnostics tab and is only usable while Outlook sync is on.

When a merchant reports missing description text on events synced before updating, be clear that this release prevents the loss going forward and does not recover the earlier text.

## 939 - [Improvement] Replace periodic scan crons with per-booking scheduled jobs for follow-up emails

### Brief Description

The follow-up email — the message sent to a customer a set time after their booking ends — used to be driven by a background task that re-read the store's entire order history every five to ten minutes, looking for bookings due a follow-up. It matched on an exact minute and had no second attempt, so a booking whose order was not yet marked **Completed** at that precise minute never received its follow-up at all, silently.

Follow-up emails now work the same way reminder emails do after story 936: each booking gets **its own scheduled job** the moment it is created, or when its dates are edited, timed at the booking's end plus the configured follow-up delay. If the order is not Completed when that time arrives, the job automatically tries again two days later; if it still is not Completed, the job is kept rather than deleted for up to a year, so it can still be triggered later if needed. Nothing is silently dropped. A new **Follow-up Email Debug Log** option on the Diagnostics tab makes the whole sequence visible.

### Prerequisites

- Plugin version 6.0.0 or later.
- **Follow-up Email** must be enabled under **Bookings → Settings → Reminder and Follow up Emails**, with a **Follow up delay time** configured.
- For any practical demonstration, set a very short follow-up delay, for example one minute. The real two-day retry and the year-long parking are time-based behaviour that cannot be observed by waiting during a support call — the Diagnostics log is the way to see the sequence happening.
- **Follow-up Email Debug Log** is switched on at **Bookings → Settings → Diagnostics**.
- Bookings made before this update are picked up automatically in the background the first time an admin loads any WordPress admin page after updating. No manual step is required.
- **Expected behaviour, not a fault:** switching Follow-up Email off and on again only affects new bookings and whatever would have fired while it was off. It does not retroactively stop or restart jobs already scheduled before the switch. Reminder emails have always behaved this way and this is deliberate.

### Step-by-Step Support Walkthrough

**Setup**

1. Go to **Bookings → Settings → Reminder and Follow up Emails**, enable **Follow-up Email**, and set a short **Follow up delay time** such as one minute for demonstration.
2. Go to **Bookings → Settings → Diagnostics** and enable **Follow-up Email Debug Log**, then save.

**Scenario A — a new booking sends its own follow-up**

3. Place a booking as a customer and mark the order **Completed**.
4. Wait for the configured delay after the booking's end time.
5. Confirm the customer receives the follow-up email, without any store-wide scan having to run.

**Scenario B — an order not yet completed**

6. Place another booking and leave the order in **Processing** rather than Completed.
7. Let the scheduled follow-up time pass.
8. Confirm no follow-up email is sent yet, and that the booking has not been lost — it is queued to be tried again rather than discarded.

**Scenario C — reading the Diagnostics log**

9. With the debug option on, open the log from the link on the **Diagnostics** tab after doing the two scenarios above.
    - Request/log fields to verify: the **Follow-up Email Debug Log**, reachable from **Bookings → Settings → Diagnostics** and from **WooCommerce → Status → Logs**. Each entry must name the order and the booking and say what happened — scheduled, sent, or skipped with the reason.
10. Confirm the log shows the scheduling of the follow-up, the successful send from Scenario A, and the skip with its reason from Scenario B.
11. Switch the debug option off, place another booking, and confirm nothing new is written to the log.

**Scenario D — switching follow-up email off**

12. Turn **Follow-up Email** off under **Bookings → Settings → Reminder and Follow up Emails**.
13. Let a booking's scheduled follow-up time arrive while it is off.
14. Confirm no email is sent, with no other action needed.

**Scenario E — bookings from before the update**

15. On a store with bookings placed on the previous version, update to 6.0.0 and load any WordPress admin page.
16. Confirm those older bookings are picked up in the background and go on to receive their follow-up at the expected time, with no manual step.

### Expected Behaviour

Each booking carries its own follow-up email schedule, so the store no longer runs a repeated scan of its whole order history and larger stores are noticeably lighter on resources. A completed booking receives its follow-up after the configured delay. A booking whose order is not yet Completed is neither emailed early nor lost — it is retried automatically, and kept if it still cannot send. Bookings from before the update are picked up without help. Turning Follow-up Email off stops new sends immediately.

The Diagnostics log is the fastest route to an answer when a merchant says a follow-up did not arrive: it names the order and says whether the email was scheduled, sent, or skipped and why.

## 936 - [Improvement] Replace Periodic Reminder Email Scan Cron with Per-Booking Scheduled Jobs (Performance issue for Reminder Email)

### Brief Description

The reminder email — sent to a customer a configured time before their booking starts — used to be driven by a background task that re-checked every active booking on the store every five to ten minutes, around the clock, whether or not any reminder was actually due. The more bookings a store held, the heavier this got, regardless of how busy the store was.

Each booking now gets **its own reminder job** at the moment it is placed, timed to the configured lead time before the booking starts. There is no repeated full scan any more. Exactly one automated send attempt is made per booking, with no retry — if it cannot send at that moment, for example because payment is not yet confirmed, the job is kept but never sends, and is cleared once the booking ends. This release also fixes a real customer problem: a reminder is no longer sent once the booking's own start time has already passed, however late the site's background processing happens to catch up.

### Prerequisites

- Plugin version 6.0.0 or later.
- **Reminder Email** must be enabled under **Bookings → Settings → Notifications**, with a **Notification Time** set. For demonstration, use a short lead time such as five minutes.
- The reminder settings screen itself is unchanged — enable/disable, notification time, subject and content all look and work exactly as before. Only the internal scheduling changed.
- Which orders qualify for a reminder is also unchanged. The same order statuses as before are used, so existing customers see no difference in **who** receives a reminder, only in how it is scheduled.
- Bookings made before this update are picked up by a one-time background migration that works in small batches so the site is not overloaded.
- **Expected behaviour, not a fault:** if Reminder Email is off at the moment a reminder would have fired, that reminder is skipped. Turning it back on afterwards does not send it retrospectively — only new or edited bookings pick up the new setting.

### Step-by-Step Support Walkthrough

**Scenario A — a reminder arrives on time**

1. Go to **Bookings → Settings → Notifications**, enable **Reminder Email** and set **Notification Time** to about five minutes so a test does not need a long wait.
2. Book any bookable product for a slot starting roughly ten minutes from now.
3. Wait until about five minutes before that booking's start time.
4. Confirm the reminder email reaches the customer's inbox at about that time. A missing email, or one arriving at the wrong time, is a failure.

**Scenario B — reminders off**

5. Repeat steps 1 and 2 with **Reminder Email** disabled.
6. Confirm no reminder email is received for that booking.

**Scenario C — a cancelled booking**

7. Make a new booking, then cancel it before its reminder would be due.
8. Confirm no reminder email is received after the cancellation.

**Scenario D — bookings from before the update**

9. On a store with future bookings placed on the previous version, update to 6.0.0 and wait a few minutes for the background migration.
10. Confirm those pre-existing bookings still receive their reminder at the expected time.

**Scenario E — the late-firing fix**

11. Book a slot, then leave the site with no traffic so its background processing does not run, until well past that booking's own start time.
12. Visit the site again to let the background processing catch up.
13. Confirm **no** reminder email is sent for that booking, even though its job was still waiting. A reminder arriving for a booking that has already started is the exact problem this release fixes — it came from a real customer order whose reminder went out three days after the booking had happened.

### Expected Behaviour

Reminders are scheduled one per booking instead of by a repeated store-wide scan, so the load no longer grows with the number of bookings held. A reminder arrives at the configured lead time before the booking starts, is not sent while Reminder Email is off, is not sent for a cancelled booking, and is never sent once the booking's start time has passed. Bookings placed before the update still get their reminders after the migration runs.

**Known limitation, already flagged for a future release:** a very large number of bookings sharing the exact same reminder time — for example a fully booked high-capacity slot — can slow the site's processing of that batch. It is not addressed in this release and is not a blocker for it.

## 924 - [Improvement] Fixed Duplicate Deposit Orders and Booking Status Issues

### Brief Description

When a store takes deposits, the balance or scheduled-payment orders that the deposits feature creates were appearing as their own separate rows in the admin **Bookings** list and were being counted in the status tabs. **All Bookings** therefore looked as though the store had more bookings than it really did, and the status-tab counts were inflated. Those balance orders are now left out of the Bookings list and its counts, so each booking is represented once, by its original order.

Separately, saving any order from **WooCommerce → Orders** — a new one or an edit — could fail outright with an error and crash the save. That happened on the ordinary path, for any order without a particular booking marker, which in practice meant every regular order. It is fixed.

### Prerequisites

- Plugin version 6.0.0 or later, with the PluginHive WooCommerce Deposits feature in use for the deposit scenarios.
- Worth confirming across all three deposit types — **Deposit Percentage**, **Fixed Deposit**, and **Scheduled Payment** — and under both remaining-balance settings: **Do not create any order for remaining balance** and **Create one order with balance payment for each deposit product**.
- The exclusion applies to both order-storage modes WooCommerce offers. Test with whichever the store uses, and ideally both if a test site is available for each.
- **Scope, to be clear with merchants:** balance and deposit orders are **not** deleted and are **not** hidden from **WooCommerce → Orders**. They are only left out of this plugin's own Bookings list and its status counts. The original booking order continues to show normally in both places, and the deposit and balance-payment flow itself — including the **Pay** button in My Account — is untouched.

### Step-by-Step Support Walkthrough

**Scenario A — balance order created manually by the admin**

1. Set **Do not create any order for remaining balance**, and use a deposit product. Repeat this scenario for Deposit Percentage, Fixed Deposit and Scheduled Payment.
2. Place a booking order as a customer. Confirm no remaining-balance order is created and only the original booking order appears in **Bookings → All Bookings**.
3. Open that order's edit page in WooCommerce and click **Generate Remaining Balance Order**. Confirm the balance order is created for the customer.
4. As the customer, pay that balance order from **My Account**. After payment completes, confirm it is still **not** shown in **Bookings → All Bookings** — only the original booking order is there.

**Scenario B — balance order created automatically**

5. Set **Create one order with balance payment for each deposit product**, again repeating for all three deposit types.
6. Place a booking order as a customer. Confirm the balance order is created but does not appear in the Bookings list.
7. Have the customer complete the balance payment, and confirm it still does not appear in the Bookings list at any point in its life.

**Scenario C — status tab counts**

8. With booking orders that have associated balance orders in the store, open **Bookings → All Bookings** and step through the status tabs.
9. Confirm the counts on each tab include only the original booking orders and never the balance orders. Read this together with story 929, which fixed the counts themselves being unfiltered.

**Scenario D — saving an order no longer fails**

10. In **WooCommerce → Orders**, create a new order containing a simple product and save it.
11. Confirm it saves successfully with no error and no crash. Repeat by editing an existing order and saving.

**Scenario E — two-way Google Calendar sync orders**

12. Create a booking through two-way Google Calendar sync, so the order is generated from a calendar event.
13. Confirm the booking appears in **Bookings → All Bookings**, the slot is correctly blocked, and no error occurs on save.
14. Repeat for a booking created against a simple product by two-way sync, which is the case that used to trigger the failure, and confirm the re-sync still happens as expected.
15. Across all of the above, confirm no errors appear while viewing the Bookings list, switching status tabs, generating a balance order or saving orders.

### Expected Behaviour

The Bookings list and its status-tab counts describe real bookings only. Deposit and balance-payment orders never appear there as separate rows and are never counted, at any point in their life, before or after the customer pays, for any deposit type and either remaining-balance setting. They remain fully visible and payable in WooCommerce → Orders and in My Account. Saving any WooCommerce order, and creating bookings through two-way Google Calendar sync, both work without error.

If a merchant says their booking count looks too high, this and story 929 are the two things to check together: whether balance orders were being listed, and whether the count was reflecting the applied filter.
