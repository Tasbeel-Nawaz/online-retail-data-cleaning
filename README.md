
# Online Retail II — Data Cleaning Project

## Project Overview
An end-to-end data cleaning and data quality analysis project using Python and Pandas. The project processes the Online Retail II dataset and identifies common data quality issues while preserving the original raw data.

## Objectives
- Identify and remove exact duplicate records.
- Analyze missing values and recover missing product descriptions where possible.
- Investigate negative quantities and classify special transactions.
- Investigate negative prices and unusual accounting records.
- Generate data quality reports and an audit log.
- Validate the cleaned dataset.

## Technologies Used
- Python
- Pandas
- OpenPyXL
- Git and GitHub

## Key Results
- Original records: 1,067,371
- Duplicate records removed: 34,335
- Records after duplicate removal and cleaning: 1,033,036
- Missing product descriptions recovered: 2,974
- Remaining missing product descriptions: 1,301
- Negative quantity records investigated: 22,496
- Negative price records investigated: 5

## Project Structure
```text
Online Retail II/
├── Data/
│   ├── Raw/
│   └── Cleaned/
├── reports/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup and Usage

### 1. Clone the repository
```bash
git clone https://github.com/Tasbeel-Nawaz/online-retail-data-cleaning.git
cd online-retail-data-cleaning
```

### 2. Create a virtual environment
```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 5. Add the raw dataset
Place the Online Retail II Excel workbook at:
```text
Data/Raw/online_retail_II.xlsx
```

### 6. Run the pipeline
```bash
python main.py
```

## Data Quality and Validation
The pipeline produces cleaning reports, investigates data quality issues, and validates the resulting dataset. Missing customer IDs are retained for investigation rather than automatically removed. Negative quantities and prices are investigated instead of being blindly deleted.

## Notes
- The raw dataset is kept separate from the cleaned output.
- The raw dataset and generated reports are excluded from Git tracking.
- Download or obtain the Online Retail II dataset separately before running the pipeline.

## Author
Tasbeel Nawaz
