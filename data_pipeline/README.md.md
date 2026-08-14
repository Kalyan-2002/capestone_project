# Data Pipeline - Catalog Pricing and Availability

## 1. Overview

This module implements a complete data-engineering pipeline for catalog-style product pricing and availability data.

The pipeline follows the workflow:

SCRAPE → CLEAN → CONVERT → STORE → QUERY → VALIDATE

The project uses Books to Scrape as the public scraping-practice data source.

Source:

https://books.toscrape.com/

The catalogue contains book products, but the pipeline mechanics are representative of a general product/catalog data-engineering workflow.

---

# 2. Requirements

Python 3.9 or newer is recommended.

Required Python packages:

- requests
- beautifulsoup4
- pandas

SQLite is included with Python.

---

# 3. Installation

From the project root, install the dependencies:

```bash
pip install requests beautifulsoup4 pandas