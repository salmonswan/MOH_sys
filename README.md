# MOH Uganda — Intern Placement System

Desktop application for distributing medical interns to health facility training centres across Uganda.

## Features

- **Fair distribution** — gender-proportional allocation and university diversity per facility
- **Reproducible** — seeded randomisation; same seed always gives the same result
- **Manual adjustments** — edit assignments via dropdown, lock rows, and re-distribute
- **Overflow handling** — choose to spread excess interns evenly or leave unassigned
- **Analytics** — summary tables and charts (qualification, gender, university, fill rate)
- **Excel export** — download the full schedule as `.xlsx`

## Input Files

### Interns File

Excel file (`.xlsx`, `.xls`, `.xlsm`, `.xlsb`, `.ods`) with columns:

| Column | Description |
|--------|-------------|
| Name | Full name |
| Sex | Male / Female |
| Qualification | MBChB, BDS, B.PHARM, BSN, or BSM |
| University | University of graduation |
| Year of Completion | Year completed |
| National Identification Number | NIN |
| Nationality | Intern's nationality |

### Carrying Capacity File

Excel file with columns:

| Column | Description |
|--------|-------------|
| Internship Training Centre | Facility name |
| MBChB | Available positions |
| BDS | Available positions |
| B.PHARM | Available positions |
| BSN | Available positions |
| BSM | Available positions |

> **Note:** The header row does not need to be on row 1. The system scans the first 20 rows automatically.

## Setup (from source)

```bash
conda create -n moh_sys python=3.12 -y
conda activate moh_sys
pip install -r requirements.txt
python main.py
```

## Build Executable

### Linux

```bash
conda activate moh_sys
pyinstaller --onefile --windowed --name "MOH_Intern_Placement" main.py
# Output: dist/MOH_Intern_Placement
```

### Windows

```powershell
conda activate moh_sys
pyinstaller --onefile --windowed --name "MOH_Intern_Placement" main.py
# Output: dist\MOH_Intern_Placement.exe
```

A GitHub Actions workflow is included that automatically builds the Windows `.exe` on every push to `master`. Download it from **Actions > Artifacts**.

## Distribution Algorithm

1. **Qualification matching** — interns only go to facilities accepting their qualification
2. **Gender proportionality** — each facility mirrors the overall male/female ratio for that qualification
3. **University diversity** — prioritises interns from least-represented universities at each facility
4. **Capacity overflow** — user chooses: spread evenly or leave unassigned
