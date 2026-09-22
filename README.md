# Climate Data Pipeline (1880–2025)

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Pipeline Status](https://img.shields.io/badge/pipeline-passing-brightgreen)

An end-to-end Python data engineering pipeline designed to ingest, sanitize, interpolate, and standardize corrupted historical climate time-series data spanning from January 1880 to December 2025.

---

## 📌 Architecture & Repository Structure

```text
.
├── clean.py               # Core ETL cleaning pipeline & plot generator
├── global_temp_dirty_v2.csv # Raw input dataset with string corruption & missing fields
├── cleaned_monthly.csv    # Sanitized and continuous monthly temperature anomaly dataset
├── cleaning_log.txt       # Automated execution logs and data quality metrics
├── chart.png              # Generated high-resolution anomaly trend plot
└── README.md              # Project documentation
