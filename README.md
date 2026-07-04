# 🏆 World Cup 2026 Sweepstake Hub

An automated, data-driven dashboard built to orchestrate and track a high-stakes World Cup sweepstake. This project implements a full ETL (Extract, Transform, Load) data pipeline that processes real-time match data, handles complex edge cases in live sports APIs, and visualizes participant standings through an interactive web application.

---

## 🛠️ System Architecture & Tech Stack

The platform is split into three decoupled components to maintain high availability and seamless data flow without server overhead:

*   **Frontend & Analytics:** `Streamlit` (Python)
*   **Data Processing Engine:** `Pandas` & `NumPy`
*   **Automation Pipeline:** `GitHub Actions` (CI/CD workflows acting as serverless cron jobs)
*   **Data Serialization:** `JSON` (raw ingest) and `CSV` (transformed application state)

---

## ⚙️ Core Technical Capabilities

### 1. Automated ETL Pipeline (GitHub Actions)
*   **Extraction:** A scheduled GitHub workflow triggers every 4 hours to poll the live Football Data API and securely dump raw match data into the repository.
*   **Fault-Tolerant Transformation:** The parsing layer (`transform.py`) handles live API anomalies, such as converting asynchronous `null` score fields for future fixtures into safe application states using inline dict evaluations (`or {}`) to prevent engine runtime crashes.

### 2. Multi-Column Tie-Breaker Logic (Pandas Engine)
Unlike standard sports apps, this sweepstake requires niche, tiered sorting rules to determine financial prize winners. The calculation layer (`metrics.py`) runs strict multi-column matrix sorting:
*   **Golden Boot Team:** Highest goals scored → broken by lowest goals conceded.
*   **Underdog Bracket:** Most goals conceded → broken by highest goals scored.
*   **The Stalemate Prize:** Most **90-minute draws** (isolated from extra-time/penalty API overrides using `regularTime` API nodes) → broken by highest total goals scored exclusively during those draws.
*   **Giant-Slayer Metric:** Algorithms parse match results against static June 2026 FIFA World Ranking deltas to automatically compute the tournament’s objectively "Biggest Upset".

### 3. Highly Scannable Live Dashboard (Streamlit UI)
*   Features a real-time financial prize distribution board mapping payouts instantly as data updates.
*   Interactive dynamic visualization charts allowing users to toggle between different tournament metric leaders.
*   Decoupled fixture tracking sections splitting live-updating tournament matchday schedules from completed outcomes.

---

## 📈 Database Schema Structure

The application state relies on a local relational structure:
*   `sweepstakeplayers.csv`: Maps real-world pool participants to their randomly assigned countries, entry financial status, and fixed baseline metrics (FIFA ranks).
*   `matches_2026.csv`: Statically archived state of all live, completed, and TBD tournament fixtures generated dynamically by the pipeline.
*   `team_stats_2026.csv`: The aggregated metrics matrix that fuels the final Streamlit presentation layer.

---

> **Design Philosophy Note:** This project was architected to run completely serverless with zero overhead costs. By leveraging GitHub Actions for orchestration and flat-file caching for the data layer, the app guarantees immediate load times on Streamlit Cloud without the dependency of an active database server.
