# 📬 USPS Service Performance Analysis — Data Squad

**Challenge X Final Project** | 👥 Team: Nuhamin Teshome, Amanda Wei, Kalkidan Tefera, Mariamawit Berta

An end-to-end data pipeline and analysis platform for investigating USPS delivery performance disparities between rural and urban America, built on ~4 billion delivery records.

---

## 🚨 Problem Statement

USPS currently faces challenges meeting its delivery time standards, with roughly **14% of mail arriving late**. This project investigates whether rural ZIP codes are systematically underserved compared to urban ones, and whether different mail types are affected differently.

---

## 🏗️ Architecture Overview

```
USPS API (30k .gz files)
        │
        ▼
  [Data Ingestion]          injest.py
  Download → Validate → Convert to Parquet
        │
        ▼
  ☁️ Azure Blob Storage        (Raw Zone)
        │
        ▼
  [PySpark Analysis]        USPSAnalysisFinalNotebook.ipynb
  Merge with RUCA codes → Classify Urban/Rural → Aggregate
        │
        ▼
  ☁️ Azure Data Lake           (Analytics Zone)
        │
        ▼
  📊 Power BI Dashboard        USPS_Service_Performance_Dashboard.pbix
```

---

## 📁 Repository Structure

```
├── injest.py                                 # 📥 Data ingestion: download, validate, convert
├── main.py                                   # 🎛️ Orchestrator: parallel pipeline execution
├── azure_connection/
│   └── azure_setup.py                        # ☁️ Azure Blob Storage upload logic
├── logging_config/
│   └── config.py                             # 📝 Centralized logging setup
├── USPSAnalysisFinalNotebook.ipynb           # 🔬 PySpark analysis notebook (Synapse)
├── USPS_Service_Performance_Dashboard.pbix   # 📊 Power BI dashboard
└── completed.txt                             # ✅ Checkpoint file for resumable ingestion
```

---

## ⚙️ Data Pipeline (`injest.py` + `main.py`)

The ingestion pipeline downloads ~30,000 compressed files from the USPS Service Performance Metrics (SPM) API, validates them, and converts them to Parquet for efficient cloud analytics.

**Key features:**
- ⚡ Parallel downloads via `ThreadPoolExecutor` (3 workers)
- 🔁 Exponential backoff retry logic (up to 5 attempts per file)
- ✅ File size validation before and after download
- 🗜️ `.gz` → Parquet conversion using Polars
- 💾 Checkpoint/resume support via `completed.txt` to safely restart after failures
- ☁️ Automatic upload to Azure Blob Storage

---

## 🔬 Analysis (`USPSAnalysisFinalNotebook.ipynb`)

Runs on **Azure Synapse Analytics** with PySpark against ~4 billion records stored in Azure Data Lake.

**Pipeline:**
1. Load raw USPS Parquet data from Azure Data Lake
2. Load USDA RUCA (Rural-Urban Commuting Area) codes at the ZIP code level
3. Join USPS data to RUCA codes on origin and destination ZIP codes
4. Classify each origin/destination as **Urban** (RUCA 1–6) or **Rural** (RUCA 7–10)
5. Separate national-level (`-1` ZIP) from ZIP-level records
6. Analyze delivery scores and average days to delivery by area type, mail type, and time period

**Key columns used:**
`time_per`, `orgn_zip_5`, `destn_zip_5`, `Origin_Area_Type`, `Destination_Area_Type`, `prodt`, `mo`, `avg_days_to_delr`, `score`, `score_plus_1`

---

## 🗺️ Rural vs. Urban Classification

ZIP codes are classified using **USDA RUCA codes**, a federal standard that maps ZIP codes to urbanization levels based on population density and commuting patterns.

| RUCA Codes | Category | Classification |
|---|---|---|
| 1–3 | Metropolitan (50,000+ pop) | 🏙️ Urban |
| 4–6 | Micropolitan (10,000–49,999 pop) | 🏙️ Urban |
| 7–9 | Small town (2,500–9,999 pop) | 🌾 Rural |
| 10 | Rural (no urban core) | 🌾 Rural |

RUCA codes were chosen because they are available at the ZIP code level — a direct match to USPS routing data — and are a widely used federal standard (USDA, FORHP).

---

## ☁️ Note on Data Access

All data lives in a private Azure environment — the raw USPS `.gz` files, converted Parquet files, and the RUCA reference dataset are stored in Azure Blob Storage and Azure Data Lake. This repository contains only the code. The pipeline and notebook are not independently runnable without access to the team's Azure infrastructure.

---

## 📊 Results & Visualization

Findings are visualized in the **Power BI dashboard** (`USPS_Service_Performance_Dashboard.pbix`).

### 📅 Annual Overview — Rural vs. Urban Delivery Performance
![Annual Overview](annual.png)

Rural areas actually outperformed urban areas on on-time delivery (81.56% vs. 79.81%), though rural mail takes slightly longer on average (3.27 days vs. 3.35 days). Rural-to-rural routes had the best performance at 83.88%, while urban-to-urban was the worst at 79.76%. Urban areas account for the vast majority of mail volume (87.57%).

### 📦 Mail Product Performance — Rural vs. Urban
![Mail Product Performance](mail_product.png)

Marketing mail dominated the top performers in both rural and urban areas, scoring above 94%. The worst performers in both categories were Periodicals — scoring around 50% — suggesting a systemic issue with that mail class regardless of geography.

### 🗺️ District Analysis
![District Analysis](district.png)

WESTPAC was the top-performing delivery region (88.75%), while CENTRAL was the lowest (79.76%). At the district level, California 6, Hawaii, and Alaska led performance (90%+), while Ohio 2, Illinois 2, and Virginia were the lowest performers (~76–78%).

---

## 🧠 Conclusion

Contrary to expectations, **rural areas are not significantly underserved** compared to urban ones — in fact, rural delivery performance is marginally better overall. The real disparities lie elsewhere:

- 📮 **Mail type matters more than geography** — Periodicals consistently underperform (~50%) in both rural and urban areas, pointing to a systemic issue beyond just location
- 🗺️ **Regional and district differences are more pronounced** — the gap between the best (WESTPAC, 88.75%) and worst (CENTRAL, 79.76%) regions is larger than the rural/urban gap
- 🔁 **Route direction matters** — Rural-to-rural routes perform best (83.88%), while urban-to-urban perform worst (79.76%), suggesting urban density may actually hinder delivery efficiency

Overall, USPS service quality improvements would be better targeted at specific mail classes and underperforming districts rather than a blanket rural vs. urban framing.

---

## 👥 Team

| Name | Role |
|---|---|
| Nuhamin Teshome | 🔧 Data Engineering / Pipeline |
| Amanda Wei | 📊 Analysis / Visualization |
| Kalkidan Tefera | 🔍 Analysis / Classification |
| Mariamawit Berta | 🎨 Visualization / Presentation |

---

*🏆 Submitted for USPS Challenge X — Final Presentation*
