import os
import pandas as pd
import numpy as np
from demand_forecast import HybridDemandForecaster

def generate_forecasts():
    print("Loading data...")
    # Right now, we simulate Member 1's data. 
    # Once they push the real data, we just change these lines to read their CSV.
    dates = pd.date_range(start='2025-04-01', end='2025-10-31', freq='D')
    warehouses = ['WH_001', 'WH_002', 'WH_003']
    
    records = []
    np.random.seed(42)
    for wh in warehouses:
        base_demand = np.random.randint(50, 200)
        for date in dates:
            # Simulate some weekend seasonality
            is_weekend = 1 if date.weekday() >= 5 else 0
            demand = base_demand + (is_weekend * 50) + np.random.randint(-20, 20)
            records.append({
                'entity_id': wh,
                'date': date,
                'demand': max(0, demand)
            })
            
    df = pd.DataFrame(records)
    
    print("Running Hybrid Forecaster (Exponential Smoothing + CatBoost)...")
    forecaster = HybridDemandForecaster(seasonal_periods=7)
    
    # Run the math
    results = forecaster.fit_predict(df, demand_col='demand')
    
    # We must also add the Chronos and PatchTST blank columns 
    # so the API contract is fulfilled until you run Colab later.
    results['chronos_forecast'] = results['forecast_demand'] 
    results['patchtst_delay_forecast'] = 0.0
    
    # Save the output as a Parquet file
    os.makedirs('outputs', exist_ok=True)
    output_path = 'outputs/forecast_scores.parquet'
    results.to_parquet(output_path, index=False)
    
    print(f"Success! Forecasts saved to: {output_path}")

if __name__ == "__main__":
    generate_forecasts()