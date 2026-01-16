import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Load test data and predictions (assumed pre-saved)
test = pd.read_csv('data/labeled/test_data.csv')
predictions = pd.read_csv('forecasts/predictions.csv')

# Calculate metrics
mae = mean_absolute_error(test['pm25'], predictions['predicted_pm25'])
rmse = np.sqrt(mean_squared_error(test['pm25'], predictions['predicted_pm25']))

print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")

# Save evaluation metrics for reference
with open('forecasts/evaluation_metrics.txt', 'w') as f:
    f.write(f"MAE: {mae:.2f}\nRMSE: {rmse:.2f}\n")
