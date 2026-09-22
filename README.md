# 🌍 Climate Time-Series Data Sanitizer & Visualization Microservice

> An enterprise-grade, end-to-end data engineering pipeline designed to clean, normalize, and visualize corrupted monthly global temperature anomaly datasets (1880–2025). Containerized with **Docker** and served via **FastAPI** for real-time cloud inference.

🚀 **Live Interactive API Documentation**: [Try it on Render](https://climate-data-pipeline-p0qi.onrender.com/docs)

---

## 💡 System Architecture & Features

This pipeline automates the transformation of noisy, real-world meteorological sensor streams into standardized time-series analytics and high-publication-quality visualizations:

1. **🧹 Robust Data Sanitization Pipeline**
   - **Multi-Format Date Parsing**: Standardizes heterogeneous timestamp formats (e.g., `188001`, `Feb-1880`, `1880/03`, `1880.04`).
   - **Column & Schema Auto-Correction**: Detects and fixes inverted/swapped date and value fields.
   - **Anomalous Outlier Removal**: Filters noisy telemetry artifacts using the Interquartile Range (IQR) method.
   - **Time-Series Imputation**: Uses temporal linear interpolation to recover missing monthly sequence records.

2. **📊 Baseline Normalization**
   - Computes thermal anomaly deviations $d$ against the 1901–2000 historical baseline.
   - Standardizes values by generating Z-scores across the full time-series timeline.

3. **🎨 Dual-Encoded Visualization Engine**
   - Renders publication-grade charts using dual-encoding: vertical position represents temperature anomalies, while continuous color gradients reflect baseline deviations.
   - Exports high-resolution vector (`chart.pdf`) and raster (`chart.png`) graphics automatically.

4. **⚡ RESTful Microservice API**
   - Wraps the execution pipeline within a high-performance **FastAPI** application.
   - Exposes asynchronous endpoints allowing client applications to stream raw CSV files and receive sanitized datasets alongside analytic plots instantly.

---

## 🛠️ Tech Stack & Dependencies

- **Language & Runtime**: Python 3.11
- **API Framework**: FastAPI, Uvicorn, Python-Multipart
- **Data Engineering**: Pandas, NumPy
- **Data Visualization**: Matplotlib
- **Containerization & Deployment**: Docker, Render Cloud Platform

---

## 📁 Repository Structure

```text
.
├── app.py                      # FastAPI REST service routing & request handlers
├── clean.py                    # Core data cleaning engine & visualization algorithms
├── Dockerfile                  # Container build instructions for production deployment
├── requirements.txt            # Lightweight microservice dependencies
├── global_temp_dirty_v2.csv    # Raw corrupted input dataset (sample simulation)
├── cleaned_monthly.csv         # Standardized CSV output
├── cleaning_log.txt            # Audit trail & statistical pipeline summary
└── chart.png / chart.pdf       # Generated dual-encoded anomaly visualizations
⚙️ Quick Start
1. Run Locally with Python
Clone the repository and install dependencies:

Bash
git clone [https://github.com/Richard Li/climate-data-pipeline.git](https://github.com/YOUR_GITHUB_USERNAME/climate-data-pipeline.git)
cd climate-data-pipeline
pip install -r requirements.txt
Launch the pipeline via API server:

Bash
uvicorn app:app --reload
Open your browser and navigate to http://127.0.0.1:8000/docs to test the API locally.

2. Run with Docker Container
Build and run using Docker:

Bash
# Build Docker image
docker build -t climate-sanitizer-api .

# Launch container
docker run -d -p 8000:8000 --name climate-service climate-sanitizer-api
Access the service at http://localhost:8000/docs.

🌐 Public API Endpoint Usage
Interactive Swagger Docs: GET /docs

Data Sanitization Endpoint: POST /clean-data/

Upload raw CSV via multipart/form-data to receive standard CSV response output.

📜 License
Distributed under the MIT License. See LICENSE for more information.
