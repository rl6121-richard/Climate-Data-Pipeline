# Global Temperature Anomaly Cleaning & Visualization

This project cleans a corrupted monthly global temperature anomaly dataset (1880–2025), normalizes it, and generates a dual-encoded chart. It also provides an API so users can upload their own CSV file and get cleaned results and a chart.

---

## What This Project Does

1. **Cleans** raw temperature data:
   - Parses many date formats (e.g., `188001`, `Feb-1880`, `1880/03`, `1880.04`)
   - Fixes swapped date/value columns
   - Removes duplicates
   - Removes outliers with the IQR method
   - Fills missing months with time interpolation

2. **Normalizes** the data:
   - Computes deviation `d` from the 1901–2000 mean
   - Computes Z-score `z` across the full series

3. **Visualizes** the data:
   - Dual-encoded chart: vertical position = anomaly, color = deviation from baseline
   - Saves `chart.pdf` and `chart.png`

4. **API**: Users can upload their own CSV and get cleaned data + chart back.

---

## Files

| File | Description |
| :--- | :--- |
| `clean.py` | Main cleaning + visualization script |
| `global_temp_dirty_v2.csv` | Raw input dataset (simulated) |
| `cleaned_monthly.csv` | Cleaned output (date, anomaly_c, z) |
| `cleaning_log.txt` | Log of cleaning steps and statistics |
| `chart.pdf`, `chart.png` | Dual-encoded visualization |


---

## Requirements

- Python 3.10+
- Install dependencies:

```bash
pip install pandas numpy matplotlib
