# Development of a Demand Forecasting Model for Public Transport

Welcome to the repository for the project **"Development of a Demand Forecasting Model for Public Transport"**.
This project focuses on building a machine learning-based forecasting model to predict taxi demand across different urban clusters in a metropolitan area. The goal is to optimize resource allocation for public transport services.

## Project Structure

```
transport_forecasting/
├── data_acquisition/
|   ├── data_ingest/            # Scripts for raw data ingestion and preprocessing
|   └── data_explore/            # Scripts for exploratory data analysis and visualization
├── data_provision/              # Scripts for data downsampling, sampling, and cluster simulation
├── development/                 # Simple web interface for input and result presentation
├── modeling/                    # Model training, registration, and MLflow tracking scripts
├── requirements.txt             # List of required Python packages
├── README.md                    # Project overview (this file)
└── diagnosis.py                 # Diagnostic scripts
```

## Project Overview

This project was built following the Microsoft Team Data Science Process (TDSP) methodology and includes:

- **Data Ingestion**: Loading 4.5 million GPS taxi trip records into a SQLite database.
- **Data Exploration**: Outlier detection and data cleaning using IQR and DBSCAN methods.
- **Clustering**: Identification of 10 stable urban clusters using KMeans.
- **Feature Engineering**: Minimal feature expansion including holiday and weekend classifications.
- **Model Training**: 
  - First approach using Poisson Regression.
  - Final model using HistGradientBoostingRegressor with Poisson loss function.
  - Cluster-specific model training and evaluation with MLflow tracking.
- **Model Evaluation**: Model selection based on cross-validated MAE, SHAP value analysis.
- **Deployment**: Simple Flask-based web interface allowing users to input day and hour for taxi demand prediction.

## Key Technologies Used

- Python 3
- scikit-learn
- MLflow
- SQLite
- Flask
- SHAP (for model interpretation)

## Getting Started

1. **Clone the repository:**
```bash
git clone https://github.com/jgoth9301/transport_forecasting.git
cd transport_forecasting
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run web interface:**
```bash
python development/web_interface.py
```
Then open your browser and navigate to `http://127.0.0.1:5000/`

## Future Enhancements

- Integration of external features like weather data, event calendars.
- Advanced spatial clustering based on event-driven mobility patterns.
- Scalable deployment using Docker or Azure Web Services.
- Full integration with a real-time database.

## Important Notes

- `.db` files are excluded from the repository to avoid exceeding GitHub's file size limits.
- All ML models are tracked using MLflow locally.

## License

This project is provided for educational and research purposes.

---

**Author:** Jürgen Goth  
**Contact:** [GitHub Profile](https://github.com/jgoth9301)

---

> "Optimizing transport today for the demands of tomorrow."
