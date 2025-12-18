# Standard Block Comparison Method

[![PyPI version](https://img.shields.io/pypi/v/standard-block-auditor.svg)](https://pypi.org/project/standard-block-auditor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17762960.svg)](https://doi.org/10.5281/zenodo.17762960)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17766254.svg)](https://doi.org/10.5281/zenodo.17766254)

**A quantitative auditing framework to break free from "number magic" and measure the true effectiveness of administrative measures.**

---

## 📖 Overview
Huge figures announced by governments and corporations, such as "cumulative total of X people" or "budget of Y billion yen," are often used to obscure the reality (ROI).
This project provides the **"Standard Block Comparison Method (SBCM),"** a technique to mathematically determine whether a measure functions as social infrastructure or is merely a statistical "error" by breaking these numbers down to the smallest unit: the "Standard Block" (Basic Municipality).

This repository contains the SBCM calculation tools and a Python library for detecting "budgetary distortion" in financial data.

## 🚀 Installation

This tool is available as a Python package. You can install it using pip:

```bash
pip install standard-block-auditor
```
*(Note: If you registered it under a different name, please replace the package name accordingly.)*

## ⚡ Quick Start

After installation, you can use the following commands directly from your terminal.

### 1. Verify a Single Metric (`sbcm-calc`)
Calculate the impact of a number (users or budget) announced by the government on a national scale.

```bash
# Example: "3,000 users" (Target: Total population)
sbcm-calc --value 3000 --target_ratio 1.0

# Example: "10 Billion JPY Budget"
sbcm-calc --value 10000000000
```

### 2. Audit Financial Statements (`sbcm-audit`)
Load financial data and automatically detect projects that are "High Cost but Low Reach" (Quadrant 4).

1.  Prepare a CSV file like `example_data.csv` (can be generated via AI prompts).
2.  Run the command:

```bash
# Specify city population (e.g., Kashiwa City: 435,000)
sbcm-audit example_data.csv --pop 435000
```
This outputs an analysis file (`distortion_analysis_result.csv`) and a visualization graph (`distortion_matrix.png`).

### 3. Statistical Verification (`sbcm-verify`)
Verify the robustness of the results using Monte Carlo simulations to counter arguments about estimation errors.

```bash
# Example: 3,000 users, Target ratio 15% (±3% uncertainty)
sbcm-verify --value 3000 --target_ratio 0.15 --ratio_sd 0.03
```

---

## 📐 Methodology

### Effectiveness Impact ($I$)
The index measuring the reach of a policy.

$$ I = \frac{V}{B} $$

The Standard Block ($B$) is defined based on Japan's demographics and administrative structure:

$$ B = \frac{P \times R}{N} $$

*   $P$: Total Population of Japan (124 Million)
*   $N$: Total Municipalities (1,718)
*   $R$: Target Attribute Ratio
*   **$B \approx 72,176 \times R$ (people)**

### The Verdict Criteria
| Impact ($I$) | Verdict | Benchmark |
| :--- | :--- | :--- |
| **$I < 1.0$** | **Error Level** | Out of scope. Cannot even cover one standard municipality. |
| **$1.0 \le I < 17$** | **Localized** | Experimental phase. Not even reaching early adopters. |
| **$172 \le I < 859$** | **Infrastructure** | Becoming a foundational public service (e.g., Water, Electricity). |
| **$I \ge 859$** | **Social OS** | Majority adoption. A prerequisite for modern society. |

---

## 📊 Budget Portfolio Analysis

An extension of SBCM that visualizes the balance between **"Invested Tax (Budget)"** and **"Achieved Outcome (Coverage)."**

### Budget Distortion Index ($D_{index}$)
$$ D_{index} = \frac{I_{budget}}{I_{coverage}} $$

Based on this index, projects are classified into four quadrants:

| Quadrant | Status | Verdict |
| :--- | :--- | :--- |
| **Q1** (High Cost / High Reach) | **Infrastructure** | Appropriate. Expensive but used by everyone (Roads, Waste collection). |
| **Q2** (Low Cost / High Reach) | **Innovation** | Excellent. Low budget, high impact (Digital transformation). |
| **Q4** (High Cost / Low Reach) | **【Distortion】** | **Audit Required. Huge taxes vanishing into the pockets of a few.** |

---

## 📂 Directory Structure

```text
Standard-Block-Comparison-Method/
├── sbcm/                  # Python Package Source Code
│   ├── __init__.py
│   ├── block_calculator.py
│   ├── budget_distortion_analyzer.py
│   ├── sensitivity_analysis.py
│   ├── config.py          # Shared Constants
│   └── visualizer.py      # Graph Plotting Module
│
├── prompts/               # AI Auditor Prompts
├── reports/               # Case Studies & Reports
├── example_data.csv       # Sample Data
├── google_sheets_script.js # Google Apps Script
├── pyproject.toml         # Package Configuration
└── README_EN.md           # This Document
```

## 📝 License

This project is released under the [MIT License](LICENSE).
Feel free to use it for administrative verification and auditing.

---

### Author
**Melnus** (GitHub: [Melnus](https://github.com/Melnus))

## 📝 Citation
If you use SBCM in your research or auditing, please cite the following paper:

> Koyama, H. (2025). Proposal for the Standard Block Comparison Method (SBCM) in the Quantitative Evaluation of Administrative Measures. Zenodo. https://doi.org/10.5281/zenodo.17762960
