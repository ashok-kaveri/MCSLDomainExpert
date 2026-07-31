"""Re-render the lane-382 support guide PDF from the (edited) markdown. No LLM."""
from pathlib import Path

import config  # noqa: F401
from pipeline import handoff_docs as hd

MD = Path("data/handoff_docs/MCSL_382_Iteration_Backlog_Support_Guide_2026-06-24.md")
PDF = Path("data/handoff_docs/MCSL_382_Iteration_Backlog_Support_Guide_2026-06-24.pdf")

md = MD.read_text()
title = "MCSL 382 Release"
PDF.write_bytes(hd.render_pdf_bytes(title, md))
print("PDF re-rendered:", PDF)
