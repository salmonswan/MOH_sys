from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser


HELP_HTML = """
<h2 style="color: #1e40af;">MOH Uganda - Intern Placement System</h2>
<p>This application distributes medical interns to health facility training centres
based on qualification, while ensuring gender fairness and university diversity.</p>

<hr>

<h2 style="color: #1e40af;">Getting Started</h2>
<table border="0" cellpadding="4">
<tr><td><b>Step 1:</b></td><td>Go to the <b>Input</b> tab and load your two Excel files.</td></tr>
<tr><td><b>Step 2:</b></td><td>Set the random seed (or leave the default). The same seed always produces the same result.</td></tr>
<tr><td><b>Step 3:</b></td><td>Click <b>Distribute Interns</b>.</td></tr>
<tr><td><b>Step 4:</b></td><td>Review results in the <b>Results</b> tab, then export to Excel.</td></tr>
</table>

<hr>

<h2 style="color: #1e40af;">Input Files</h2>

<h3>Interns File</h3>
<p>An Excel file (.xlsx, .xls, .xlsm, .xlsb, or .ods) with the following columns:</p>
<table border="1" cellpadding="6" cellspacing="0" width="100%">
<tr><td><b>Name</b></td><td>Full name of the intern</td></tr>
<tr><td><b>Sex</b></td><td>Gender (e.g., Male / Female)</td></tr>
<tr><td><b>Qualification</b></td><td>Must match one of: MBChB, BDS, B.PHARM, BSN, BSM</td></tr>
<tr><td><b>University</b></td><td>University of graduation</td></tr>
<tr><td><b>Year of Completion</b></td><td>Year the intern completed their studies</td></tr>
<tr><td><b>National Identification Number</b></td><td>NIN</td></tr>
<tr><td><b>Nationality</b></td><td>Intern's nationality</td></tr>
</table>

<h3>Carrying Capacity File</h3>
<p>An Excel file with facility names and available slots per qualification:</p>
<table border="1" cellpadding="6" cellspacing="0" width="100%">
<tr><td><b>Internship Training Centre</b></td><td>Name of the health facility</td></tr>
<tr><td><b>MBChB, BDS, B.PHARM, BSN, BSM</b></td><td>Number of available positions for each qualification</td></tr>
</table>

<br>
<p><b>Note:</b> The header row does not need to be on row 1. The system automatically
scans the first 20 rows to find the correct header row.</p>

<hr>

<h2 style="color: #1e40af;">Distribution Logic</h2>
<p>The system uses a fair distribution algorithm with the following priorities:</p>
<ol>
<li><b>Qualification matching</b> - Interns are only assigned to facilities that accept their qualification.</li>
<li><b>Gender proportionality</b> - Each facility receives a male/female ratio that mirrors
the overall ratio for that qualification. E.g., if 60% of BSN interns are female,
each facility gets approximately 60% female BSN interns.</li>
<li><b>University diversity</b> - Within each facility, the system prioritises interns from
universities that are least represented at that facility, ensuring a mix of institutions.</li>
<li><b>Capacity respect</b> - Facilities are filled up to their stated capacity first.
If there are more interns than positions, the system prompts you to choose how to handle the overflow.</li>
</ol>

<hr>

<h2 style="color: #1e40af;">Random Seed</h2>
<p>The seed controls the randomisation. Key points:</p>
<ul>
<li><b>Same seed = same result</b> - useful for reproducibility and auditing.</li>
<li><b>Different seed = different result</b> - try multiple seeds to compare distributions.</li>
<li>Default seed is 42. You can change it in the Input tab.</li>
</ul>

<hr>

<h2 style="color: #1e40af;">Results Tab</h2>

<h3>Viewing and Editing</h3>
<ul>
<li>The table shows all interns with their assigned facility.</li>
<li>The <b>Assigned Health Facility</b> column has a dropdown - you can manually change any assignment.</li>
<li>The dropdown only shows facilities that accept that intern's qualification.</li>
</ul>

<h3>Lock and Re-distribute</h3>
<ol>
<li>Tick the <b>Lock</b> checkbox next to any assignments you want to keep.</li>
<li>Click <b>Re-distribute Unlocked</b> - locked assignments stay, everything else is reshuffled.</li>
</ol>

<h3>Overflow Handling</h3>
<p>When there are more interns than available positions for a qualification, a dialog appears with options:</p>
<ul>
<li><b>Spread evenly beyond capacity</b> - distributes extra interns round-robin across all facilities for that qualification.</li>
<li><b>Leave unassigned</b> - keeps them without an assignment (shown as blank in the table).</li>
</ul>

<h3>Export</h3>
<p>Click <b>Export to Excel</b> to save the full schedule as an .xlsx file with auto-sized columns.</p>

<hr>

<h2 style="color: #1e40af;">Analytics Tab</h2>
<p>After distribution, the Analytics tab shows:</p>
<ul>
<li><b>Summary stats</b> - total, assigned, and unassigned counts</li>
<li><b>Facility x Qualification</b> - cross-tabulation table</li>
<li><b>Charts</b> - qualification breakdown (pie), gender distribution (bar),
university distribution (bar), fill rate per facility (bar), and interns per facility (bar)</li>
</ul>
<p>Fill rate bars are <b>green</b> when at or below capacity and <b>red</b> when over capacity.</p>

<hr>

<h2 style="color: #1e40af;">About</h2>
<p><b>Version:</b> 1.0<br>
<b>Purpose:</b> Ministry of Health Uganda - Intern Placement System<br>
<b>Supported qualifications:</b> MBChB, BDS, B.PHARM, BSN, BSM</p>
"""


class HelpTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("QTextBrowser { font-size: 13px; line-height: 1.5; }")
        browser.setHtml(HELP_HTML)
        layout.addWidget(browser)
