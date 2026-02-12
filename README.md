# Twitter Word Count Analyzer

An interactive statistical analysis tool for exploring tweet length patterns and summary statistics. Built with Python, Streamlit, and modern data science libraries.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)


## Overview

<img width="1030" height="950" alt="Image" src="https://github.com/user-attachments/assets/ae0c896a-b3a1-4922-9d2b-f20fb65986a8" />

Twitter Word Count Analyzer provides an intuitive interface for understanding tweet length patterns through comprehensive summary statistics. The tool helps analyze how celebrities communicate on Twitter, track changes over time, and compare different accounts—all with no API key required.


## Why This Project?

Understanding social media communication patterns through statistics offers valuable insights into:

- **Communication evolution:** How do tweeting habits change over years?  
- **User behavior:** What are the characteristic patterns of different celebrities?  
- **Content strategy:** What tweet lengths generate the most engagement?  
- **Statistical literacy:** Learn to interpret mean, median, skewness, kurtosis, and more  

---

## Features

### Core Statistical Analysis

#### Comprehensive Summary Statistics

- **Central tendency:** Mean, Median, Mode  
- **Dispersion:** Standard deviation, Variance, Range, IQR  
- **Shape:** Skewness, Kurtosis  
- **Position:** Percentiles (1st–99th), Quartiles  

#### Distribution Visualization

- Interactive histograms with KDE overlay  
- Box plots for group comparisons  
- Q-Q plots for normality assessment  
- Percentile bar charts  

#### Trend Detection

- Year-over-year mean/median tracking  
- Volatility (standard deviation) analysis  
- Statistical significance testing (t-test)  
- Percentage change calculations  

#### Multi-User Comparison

- Side-by-side metric comparison  
- Industry grouping analysis  
- Engagement correlation studies  

---

## Project Structure

```text
tweet-analyzer/
├── app.py                         # Main Streamlit application
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── data/                          # Generated sample data
└── src/
    ├── __init__.py
    ├── collect_tweets.py          # Free Twitter data collection (no API key)
    └── calculate_stats.py         # Comprehensive summary statistics engine
```

---

## Installation

### Prerequisites

- Python 3.12 or higher  
- pip package manager  
- 500MB free disk space  

### Setup

#### 1. Clone or download the project

```bash
git clone https://github.com/sefabilicier/Tweet-Statistic-Analyzer.git
cd tweet-analyzer
```

#### 2. Create a virtual environment (recommended)

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**
```bash
python3.12 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Dependencies
```text

| Package     | Version   | Purpose                            |
|------------|----------|--------------------------------------|
| streamlit  | ≥1.32.0  | Web application framework            |
| pandas     | ≥2.1.4   | Data manipulation and analysis       |
| numpy      | ≥1.26.0  | Numerical computations               |
| matplotlib | ≥3.8.0   | Q-Q plots and static visualizations  |
| seaborn    | ≥0.13.0  | Statistical visualizations           |
| plotly     | ≥5.18.0  | Interactive charts                   |
| scipy      | ≥1.11.4  | Statistical tests and KDE            |
| twikit     | ≥0.1.0   | Optional Twitter scraping (3.12+)    |

```

---

## Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at:

```
http://localhost:8501
```

---

## Usage Guide

### Getting Started

### Option 1: Sample Data (Recommended)

Includes 5 celebrity accounts with realistic tweeting patterns:

- **Elon Musk (Tech)** — Erratic, short tweets with high variability  
- **Taylor Swift (Music)** — Consistent, medium-length tweets  
- **NASA (Science)** — Professional, informative content  
- **Barack Obama (Politics)** — Thoughtful, longer-form communication  
- **Bill Gates (Tech)** — Informative, balanced tweet length  

### Option 2: Upload Your Own CSV

Upload any Twitter dataset with these columns:

- `date` — Tweet timestamp  
- `username` — Twitter handle  
- `content` — Tweet text  
- `word_count` (optional — auto-calculated)  

Optional engagement metrics:
- `like_count`
- `retweet_count`
- `reply_count`

### Option 3: Live Collection (Experimental)

Enter a Twitter username and date range.  
The tool returns filtered sample data (mock implementation) — no API key required.

---

## Statistical Concepts Explained

### Summary Statistics Dashboard

```text 

| Metric   | What It Tells You | Interpretation Guide |
|----------|------------------|----------------------|
| Mean     | Average tweet length | Center of distribution |
| Median   | Middle value (50th percentile) | Robust to outliers |
| Std Dev  | How much tweets vary | Higher = less consistent |
| IQR      | Middle 50% range | Typical tweet length spread |
| Skewness | Symmetry of distribution | >0.5: Right-skewed (few long tweets)<br><-0.5: Left-skewed (few short tweets) |
| Kurtosis | Tail heaviness | >3: Heavy tails (extreme outliers)<br><3: Light tails |
| CV       | Relative variability | >50%: High relative spread |

```

## Visual Analysis Guide

### Histogram + KDE

- **Peak location:** Most common tweet length  
- **Spread:** Horizontal width indicates variability  
- **Shape:** Symmetric vs. skewed distribution  
- **Mean/Median lines:** Quick skewness check  

### Box Plot

- **Box:** Middle 50% of tweets (IQR)  
- **Line in box:** Median  
- **Whiskers:** Typical range (1.5× IQR)  
- **Points:** Outliers (unusually long/short tweets)  

### Q-Q Plot

- Points follow red line → Normal distribution  
- S-shaped curve → Heavy tails  
- Curved away from line → Skewed distribution  

### Year-over-Year Trend

- **Line slope:** Increasing/decreasing trend  
- **Shaded band:** ±1 standard deviation (volatility)  
- **Gap between mean/median:** Skewness persistence  


**That was it, thank you for reviewing the project!**