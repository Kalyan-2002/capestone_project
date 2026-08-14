Module -1--

\# Data Pipeline - Catalog Pricing and Availability



\## 1. Overview



This module implements a complete data-engineering pipeline for catalog-style product pricing and availability data.



The pipeline follows the workflow:



SCRAPE → CLEAN → CONVERT → STORE → QUERY → VALIDATE



The project uses Books to Scrape as the public scraping-practice data source.



Source:



https://books.toscrape.com/



The catalogue contains book products, but the pipeline mechanics are representative of a general product/catalog data-engineering workflow.



\---



\# 2. Requirements



Python 3.9 or newer is recommended.



Required Python packages:



\- requests

\- beautifulsoup4

\- pandas



SQLite is included with Python.



\---



\# 3. Installation



From the project root, install the dependencies:



```bash

pip install requests beautifulsoup4 pandas

\\-----------------------------------------



\&#x20;Titanic Analytics Project



\\## Overview



This project performs an end-to-end data analysis and machine learning workflow using the Titanic dataset.



The project is divided into two tasks:



Module -2 

\\- \\\*\\\*Task 1:\\\*\\\* Data profiling, cleaning, exploratory data analysis (EDA), and visualization.

\\- \\\*\\\*Task 2:\\\*\\\* Predictive modeling, model evaluation, class-imbalance handling, hyperparameter tuning, and regression.



\\---



\\# Project Structure



```text

project/

│

├── analytics/

│   ├── 01\\\_eda.ipynb

│   ├── 02\\\_modeling.ipynb

│   ├── titanic.csv

│   ├── full\\\_pipeline.joblib

│   ├── requirements.txt

│   └── README.md

│

├── README.md

└── .gitignore



\\----------------------------------------



\\# Module 3 -

\\- Zepto Support Assistant 



\\## Overview



This project implements a small GenAI support assistant for Zepto.



The system uses:



\\- Sentence Transformers

\\- all-MiniLM-L6-v2

\\- ChromaDB

\\- LangGraph

\\- TypedDict

\\- FastAPI

\\- Pydantic

\\- Deterministic MOCK\\\_LLM baseline



The default configuration is:



```text

MOCK\\\_LLM=1






