from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QLabel
from PySide6.QtCore import Qt


HELP_HTML = """
<style>
    body { font-family: sans-serif; font-size: 13px; line-height: 1.6; color: #1f2937; }
    h2 { color: #1e40af; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }
    h3 { color: #374151; margin-top: 16px; }
    code { background: #f3f4f6; padding: 2px 6px; border-radius: 3px; font-size: 12px; }
    ul { margin: 4px 0; padding-left: 20px; }
    li { margin-bottom: 4px; }
    .note { background: #fef3c7; padding: 8px 12px; border-left: 3px solid #f59e0b; margin: 8px 0; }
    .step { background: #eff6ff; padding: 8px 12px; border-left: 3px solid #3b82f6; margin: 6px 0; }
</style>

<h2>MOH Uganda — Intern Placement System</h2>
<p>This application distributes medical interns to health facility training centres
based on qualification, while ensuring gender fairness and university diversity.</p>

<h2>Getting Started</h2>

<div class="step"><b>Step 1:</b> Go to the <b>Input</b> tab and load your two Excel files.</div>
<div class="step"><b>Step 2:</b> Set the random seed (or leave the default). The same seed always produces the same result.</div>
<div class="step"><b>Step 3:</b> Click <b>Distribute Interns</b>.</div>
<div class="step"><b>Step 4:</b> Review results in the <b>Results</b> tab, then export to Excel.</div>

<h2>Input Files</h2>

<h3>Interns File</h3>
<p>An Excel file (<code>.xlsx</code>, <code>.xls</code>, <code>.xlsm</code>, <code>.xlsb</code>, or <code>.ods</code>) with the following columns:</p>
<ul>
    <li><b>Name</b> — Full name of the intern</li>
    <li><b>Sex</b> — Gender (e.g., Male / Female)</li>
    <li><b>Qualification</b> — Must match one of: MBChB, BDS, B.PHARM, BSN, BSM</li>
    <li><b>University</b> — University of graduation</li>
    <li><b>Year of Completion</b> — Year the intern completed their studies</li>
    <li><b>National Identification Number</b> — NIN</li>
    <li><b>Nationality</b> — Intern's nationality</li>
</ul>

<h3>Carrying Capacity File</h3>
<p>An Excel file with facility names and available slots per qualification:</p>
<ul>
    <li><b>Internship Training Centre</b> — Name of the health facility</li>
    <li><b>MBChB, BDS, B.PHARM, BSN, BSM</b> — Number of available positions for each qualification</li>
</ul>

<div class="note">
    <b>Note:</b> The header row does not need to be on row 1. The system automatically
    scans the first 20 rows to find the correct header row.
</div>

<h2>Distribution Logic</h2>
<p>The system uses a fair distribution algorithm with the following priorities:</p>
<ol>
    <li><b>Qualification matching</b> — Interns are only assigned to facilities that accept their qualification.</li>
    <li><b>Gender proportionality</b> — Each facility receives a male/female ratio that mirrors
    the overall ratio for that qualification. E.g., if 60% of BSN interns are female,
    each facility gets approximately 60% female BSN interns.</li>
    <li><b>University diversity</b> — Within each facility, the system prioritises interns from
    universities that are least represented at that facility, ensuring a mix of institutions.</li>
    <li><b>Capacity respect</b> — Facilities are filled up to their stated capacity first.
    If there are more interns than positions, the system prompts you to choose how to handle the overflow.</li>
</ol>

<h2>Random Seed</h2>
<p>The seed controls the randomisation. Key points:</p>
<ul>
    <li><b>Same seed = same result</b> — useful for reproducibility and auditing.</li>
    <li><b>Different seed = different result</b> — try multiple seeds to compare distributions.</li>
    <li>Default seed is <code>42</code>. You can change it in the Input tab.</li>
</ul>

<h2>Results Tab</h2>

<h3>Viewing & Editing</h3>
<ul>
    <li>The table shows all interns with their assigned facility.</li>
    <li>The <b>Assigned Health Facility</b> column has a dropdown — you can manually change any assignment.</li>
    <li>The dropdown only shows facilities that accept that intern's qualification.</li>
</ul>

<h3>Lock & Re-distribute</h3>
<ol>
    <li>Tick the <b>Lock</b> checkbox next to any assignments you want to keep.</li>
    <li>Click <b>Re-distribute Unlocked</b> — locked assignments stay, everything else is reshuffled.</li>
</ol>

<h3>Overflow Handling</h3>
<p>When there are more interns than available positions for a qualification, a dialog appears with options:</p>
<ul>
    <li><b>Spread evenly beyond capacity</b> — distributes extra interns round-robin across all facilities for that qualification.</li>
    <li><b>Leave unassigned</b> — keeps them without an assignment (shown as blank in the table).</li>
</ul>

<h3>Export</h3>
<p>Click <b>Export to Excel</b> to save the full schedule as an <code>.xlsx</code> file with auto-sized columns.</p>

<h2>Analytics Tab</h2>
<p>After distribution, the Analytics tab shows:</p>
<ul>
    <li><b>Summary stats</b> — total, assigned, and unassigned counts</li>
    <li><b>Facility × Qualification</b> — cross-tabulation table</li>
    <li><b>Charts</b> — qualification breakdown (pie), gender distribution (bar),
    university distribution (bar), fill rate per facility (bar), and interns per facility (bar)</li>
</ul>
<p>Fill rate bars are <span style="color:#10b981"><b>green</b></span> when at or below capacity,
and <span style="color:#ef4444"><b>red</b></span> when over capacity.</p>

<h2>About</h2>
<p><b>Version:</b> 1.0<br>
<b>Purpose:</b> Ministry of Health Uganda — Intern Placement System<br>
<b>Supported qualifications:</b> MBChB, BDS, B.PHARM, BSN, BSM</p>
"""


class HelpTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(HELP_HTML)
        layout.addWidget(browser)
