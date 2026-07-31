"""Condense the ZI-580 (PostNL) section to just the added service codes."""
from pathlib import Path

MD = Path("data/handoff_docs/MCSL_382_Iteration_Backlog_Support_Guide_2026-06-24.md")
text = MD.read_text()

start_marker = "## ZI-580 - From SL: ZI-580"
end_marker = "## Migrate FedEx REST DG, Alcohol, and Battery shipment support from C2 to C39"

s = text.index(start_marker)
# keep the title block: from start to the first "### Feature Summary" after it
fs = text.index("### Feature Summary", s)
e = text.index(end_marker, s)

new_body = """### Feature Summary

This change adds the following **PostNL** service codes to the available PostNL service list in MCSL (PR #3109, `postNlConstants.js` / `serviceCodes.js`). Carrier scope: **PostNL only**. Validated platform: **Magento**.

| Service code | Service name |
|---|---|
| 6942 | Boxable Track & Trace (contract) |
| 6350 | Packet Track & Trace |
| 6405 | Packet Untracked |
| 6440 | Boxable Untracked |
| 6906 | Packet Track & Trace insured |
| 6972 | Boxable Track & Trace |

---

### What Support Should Confirm

- The store is on **MCSL 382 or later** — the codes appear only after the release is deployed.
- **PostNL** is configured and active under hamburger menu > Carriers.
- The service code(s) above appear in the PostNL service/product selector (hamburger menu > Carriers > PostNL).
- A rate is returned and a label generates for an EU Packet-eligible order using the selected code; the request log shows the correct service code in the payload.
- The printed label may display "Packet Tracked Standard" — this is PostNL's own label text for these service codes and is expected behaviour.

---

### Merchant-Safe Explanation

The PostNL service codes listed above are now selectable in your PluginHive Multi Carrier Shipping Label app, alongside your existing PostNL services. Select a code, fetch rates, and generate labels for eligible shipments as usual. The printed label may show "Packet Tracked Standard" — this is normal and comes directly from PostNL.

"""

text = text[:fs] + new_body + "\n" + text[e:]
MD.write_text(text)
print("ZI-580 section condensed.")
