# Pakistan Air Quality Analysis and Forecasting

## Project Description

This project focuses on analyzing and forecasting air quality in Pakistan using historical PM2.5 data. PM2.5 is one of the most harmful air pollutants and poses serious health risks, especially in urban areas.
The project implements an end-to-end machine learning pipeline that includes data ingestion, cleaning, preprocessing, exploratory data analysis, model training, inference, and evaluation. The main goal is to understand pollution trends and predict future PM2.5 levels using historical data. Frontend deployment is not the primary focus; instead, emphasis is placed on the core technical workflow and model development.

---

## Dataset Source

The dataset used in this project is sourced from **OpenAQ**, an open-source platform that provides publicly available air quality data collected from monitoring stations worldwide.

* Pollutant: PM2.5
* Region: Pakistan
* Format: CSV
* Data Type: Time-stamped air quality measurements

The raw data contains missing values and inconsistencies, which are handled during the preprocessing stage.

---

## How to Run the Project

Follow the steps below to run the project locally:

### 1. Clone the Repository

```bash
git clone https://github.com/madeeharehan/pakistan-air-quality-project.git
cd pakistan-air-quality-project
```

### 2. Install Dependencies

Make sure Python is installed, then run:

```bash
pip install -r requirements.txt
```

### 3. Data Ingestion

Run the data fetching script to download and store PM2.5 data:

```bash
python fetch_data.py
```

### 4. Data Cleaning and Preprocessing

Clean and merge the raw datasets:

```bash
python clean_and_merge.py
```

Label air quality levels using AQI standards:

```bash
python label_aqi.py
```

### 5. Exploratory Data Analysis

Generate visualizations and analyze PM2.5 trends:

```bash
python exploratory_data_analysis.py
```

### 6. Model Training and Forecasting

Train the forecasting model and generate predictions:

```bash
python train_forecast_model.py
```

### 7. Evaluation

Model performance is evaluated using MAE and RMSE, which are printed after training.

---

## Project Folder Structure

```text
pakistan-air-quality-project/
│
├── data/
│   ├── raw/                 # Raw PM2.5 data from OpenAQ
│   ├── cleaned/             # Cleaned and merged datasets
│   └── labeled/             # AQI-labeled datasets
│
├── models/                  # Trained models and related files
│
├── forecasts/               # Generated prediction outputs
│
├── visualizations/          # Plots and graphs from EDA
│
├── frontend/                # React frontend (optional / experimental)
│
├── fetch_data.py            # Data ingestion script
├── clean_and_merge.py       # Data cleaning and merging
├── label_aqi.py             # AQI labeling logic
├── exploratory_data_analysis.py  # EDA scripts
├── train_forecast_model.py  # Model training and inference
│
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
└── .gitignore               # Git ignore file
```

---

## Reproducibility Notes

* All experiments are reproducible using the provided scripts.
* No pretrained models are used.
* The same dataset and scripts can be rerun to obtain comparable results.
* Version control is maintained through GitHub with meaningful commits.

---

## SDG Alignment

This project contributes to **UN Sustainable Development Goal 3: Good Health and Well-being** by supporting early identification of harmful air pollution trends, which can aid public health awareness and preventive action.

---

## Author

**Madeeha Rehan**
MS Artificial Intelligence
GitHub: [https://github.com/madeeharehan](https://github.com/madeeharehan)
