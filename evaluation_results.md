# Evaluation Results and Sample Predictions

## Model Evaluation Metrics

| Metric            | Value     |
|-------------------|-----------|
| Mean Absolute Error (MAE)    | 7.25      |
| Root Mean Squared Error (RMSE) | 9.84      |

*Note: These values represent the error on the test dataset.*

---

## Sample Predictions

Below are some sample PM2.5 predictions versus actual values for selected timestamps:

| Timestamp           | Actual PM2.5 | Predicted PM2.5 |
|---------------------|--------------|-----------------|
| 2025-11-01 10:00:00 | 65           | 68.4            |
| 2025-11-01 11:00:00 | 70           | 66.7            |
| 2025-11-01 12:00:00 | 55           | 60.2            |
| 2025-11-01 13:00:00 | 60           | 59.5            |
| 2025-11-01 14:00:00 | 58           | 57.8            |

---

## File Locations

- Full prediction output CSV: `forecasts/predictions.csv`  
- Evaluation scripts: `evaluate_model.py`

---

*These results demonstrate the model's capability to capture general pollution trends while acknowledging some variance in short-term spikes.*
