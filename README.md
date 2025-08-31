# Smart Weather Insights Platform 🌦️

A **production-grade weather data platform** that ingests, processes, and analyzes weather datasets, providing predictions and insights via APIs and dashboards. This project evolves alongside a master’s curriculum, demonstrating a progressive, hands-on application of data engineering, statistics, and machine learning.

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Features](#features)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Project Roadmap](#project-roadmap)  
- [GitHub Branch Strategy](#github-branch-strategy)  
- [Portfolio Story](#portfolio-story)  

---

## Project Overview

**Goal:** Build a cloud-deployed data platform that:  

- Ingests weather and related datasets (historical and real-time).  
- Processes and cleans data efficiently.  
- Applies statistical and ML models to generate predictions.  
- Exposes insights via APIs and dashboards for end-users.  

**Core Principle:** Every milestone integrates mathematical concepts learned, demonstrating practical mastery of data engineering, analytics, and cloud deployment.

---

## Features

### M1 – ETL Skeleton (Foundation)
- Fetch weather data from APIs using the `LoadFromApi` Python class.  
- Store raw JSON data in PostgreSQL.  
- Normalize timestamps, temperature, humidity, and other key fields.  
- Tools: Python, `requests`, PostgreSQL, SQLAlchemy, OpenMeteoAPI.

<!-- ### M2 – Data Cleaning + Scheduling
- Clean datasets: remove nulls, standardize units.  
- Schedule daily ETL runs using Apache Airflow (local execution).

### M3 – Initial EDA & Storage Design
- Use pandas for exploratory data analysis.  
- Store summary statistics in PostgreSQL tables.  
- Provide reproducible Jupyter notebooks for exploration.

### Later Phases
- Regression and classification models (temperature prediction, extreme weather detection).  
- Model monitoring with alerts.  
- Distributed processing with Spark/Dask.  
- Streaming data ingestion and integration.  
- Cloud deployment with Docker, AWS ECS/EKS, CI/CD pipelines.  
- FastAPI endpoints and Streamlit dashboards for interactive insights. -->

---

## Installation

```bash
git clone https://github.com/PearlPearl-Pearl/smart-weather-platform.git
cd smart-weather-platform

python -m venv venv
source venv/bin/activate
venv\Scripts\activate

pip install -r requirements.txt
