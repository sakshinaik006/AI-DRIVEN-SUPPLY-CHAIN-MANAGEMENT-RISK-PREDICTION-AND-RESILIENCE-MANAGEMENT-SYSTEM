import os
import pandas as pd
import numpy as np

def generate_dummy_predictions():
    # Make sure the outputs folder exists
    os.makedirs('outputs', exist_ok=True)
    
    dates = pd.date_range(start='2025-04-01', end='2025-10-31', freq='D')
    risk_types = ['supplier', 'manufacturing', 'warehouse', 'transport']
    entities = ['SUP_001', 'PLANT_001', 'WH_001', 'ROUTE_001']
    
    records = []
    np.random.seed(42)
    
    for date in dates:
        for risk in risk_types:
            for entity in entities:
                prob = float(np.random.uniform(0.05, 0.85))
                level = 'Low' if prob < 0.30 else ('Medium' if prob < 0.60 else 'High')
                
                records.append({
                    'entity_id': entity,
                    'date': date.strftime('%Y-%m-%d'),
                    'risk_type': risk,
                    'probability': round(prob, 4),
                    'level': level
                })
                
    # Save the dummy file
    pd.DataFrame(records).to_csv('outputs/predictions.csv', index=False)
    print("[Handover #6] Successfully generated outputs/predictions.csv")

if __name__ == '__main__':
    generate_dummy_predictions()