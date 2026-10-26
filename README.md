# Sleep, Screen Time and Stress Analysis

Final Project, Unit 3: Individual Data Exploration and Dashboard Development.

This project explores how smartphone use and sleep habits relate to stress. It includes a full exploratory data analysis in a Jupyter notebook and an interactive Streamlit dashboard.

## Dataset

- **Title:** Sleep, Screen Time and Stress Analysis
- **Source:** [Kaggle](https://www.kaggle.com/datasets/jayjoshi37/sleep-screen-time-and-stress-analysis/)
- **Size:** 15,000 rows and 13 columns (14,415 rows after cleaning)
- **Columns:** age, gender, occupation, daily screen time, phone use before sleep, sleep duration, sleep quality, caffeine intake, physical activity, notifications per day, stress level, mental fatigue

## Main questions

- Is higher daily screen time associated with higher stress?
- Do people who sleep fewer hours have higher stress?
- Is phone use before sleep associated with shorter or poorer sleep?
- How do caffeine and physical activity relate to sleep and stress?
- Does stress differ between occupations?
- Which variables have the strongest relationship with stress?

## Data cleaning

- Checked for missing values and duplicates (none found)
- Removed rows with the invalid gender value "Other"
- Renamed `notifications_received_per_day` to `notifications_per_day`
- Saved the result as `sleep_mobile_stress_dataset_15000_cleaned.csv`

## Key findings

- Screen time has a strong positive correlation with stress (about 0.88)
- Sleep quality has a strong negative correlation with stress (about -0.86)
- Mental fatigue has the strongest relationship with stress (about 0.95)
- Stress differs very little between occupations
- Caffeine and physical activity show almost no relationship with stress

These are correlations, so they do not prove that one thing causes another.

## Project files

| File | Description |
| --- | --- |
| `EDA_Project.ipynb` | Jupyter notebook with the full analysis |
| `app.py` | Streamlit dashboard |
| `sleep_mobile_stress_dataset_15000.csv` | Original dataset |
| `sleep_mobile_stress_dataset_15000_cleaned.csv` | Cleaned dataset used by the dashboard |
| `requirements.txt` | Python packages needed |
| `.streamlit/config.toml` | Dashboard colour theme |

## How to run the dashboard

1. Install Python 3.9 or newer.
2. Open a terminal in this folder and install the packages:

   ```
   pip install -r requirements.txt
   ```

3. Start the app:

   ```
   streamlit run app.py
   ```

4. The dashboard opens in your browser at http://localhost:8501.

Keep the cleaned CSV in the same folder as `app.py`.

## Dashboard features

- **Sidebar:** dataset description and filters (gender dropdown, occupation multiselect, age slider)
- **Main page:** summary numbers, data preview, summary statistics, eight interactive charts and a key insights section

## How to run the notebook

Install Jupyter, open `EDA_Project.ipynb` and run all cells. Keep the original CSV in the same folder as the notebook.

## Author

Add your name here.
