import pandas as pd
import numpy as np
from statsmodels.tsa.api import ExponentialSmoothing
from catboost import CatBoostRegressor

class HybridDemandForecaster:
    """
    Combines Exponential Smoothing (base trend/seasonality)
    with a CatBoost Regressor to model residuals using external features.
    """
    def __init__(self, seasonal_periods=7):
        self.seasonal_periods = seasonal_periods
        self.es_models = {}
        self.residual_model = CatBoostRegressor(
            iterations=300, 
            learning_rate=0.05, 
            depth=5, 
            verbose=0
        )

    def fit_predict(self, df: pd.DataFrame, demand_col='demand', feature_cols=None):
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        es_predictions = []
        
        # Fit Exponential Smoothing per warehouse
        for entity_id, group in df.groupby('entity_id'):
            series = group[demand_col].values
            # Add small noise to prevent flatline errors in dummy data
            series = series + np.random.normal(0, 0.1, len(series)) 
            
            es_model = ExponentialSmoothing(
                series, 
                trend='add', 
                seasonal='add', 
                seasonal_periods=self.seasonal_periods,
                initialization_method="estimated"
            ).fit()
            self.es_models[entity_id] = es_model
            es_predictions.extend(es_model.fittedvalues)

        df['es_forecast'] = es_predictions
        df['residual'] = df[demand_col] - df['es_forecast']

        # Fit CatBoost on residuals if external features (like weather) exist
        if feature_cols:
            X = df[feature_cols].fillna(0)
            y = df['residual']
            self.residual_model.fit(X, y)
            df['catboost_residual_pred'] = self.residual_model.predict(X)
        else:
            df['catboost_residual_pred'] = 0.0

        # Combine forecasts
        df['forecast_demand'] = df['es_forecast'] + df['catboost_residual_pred']
        df['forecast_gap'] = df[demand_col] - df['forecast_demand']
        
        # Flag a surge if the gap is larger than 1.5 standard deviations
        std_gap = df['forecast_gap'].std()
        df['demand_surge_flag'] = (df['forecast_gap'] > std_gap * 1.5).astype(int)

        return df[['entity_id', 'date', 'forecast_demand', 'forecast_gap', 'demand_surge_flag']]